"""
LangGraph 5-node analytics agent.
Intent Classification -> Schema Retrieval -> SQL Gen+Exec -> KPI Calc -> Report Assembly
"""
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
import pandas as pd
import os

from src.llm.provider import LLMProvider
from src.schema.extractor import extract_schema, get_schema_context
from src.retrieval.schema_store import SchemaStore
from src.sql.generator import SQL_SYSTEM_PROMPT, build_sql_prompt, parse_sql_response
from src.sql.validator import validate_sql
from src.sql.executor import SQLExecutor
from src.calculations.kpi_agent import calculate_kpis
from src.report.summarizer import SUMMARY_SYSTEM_PROMPT, build_summary_prompt
from src.report.assembler import assemble_report

# Explainability modules
from src.explainability.query_analyzer import QueryAnalyzer
from src.explainability.schema_explainer import SchemaExplainer
from src.explainability.sql_explainer import SQLExplainer
from src.explainability.kpi_explainer import KPIExplainer


# ---- Agent State ----
class AgentState(TypedDict):
    query: str
    intent: str
    needs_chart: bool
    relevant_tables: List[str]
    schema_context: str
    sql_query: str
    sql_result: Optional[pd.DataFrame]
    calculations: dict
    sql_retries: int
    chart_code: str
    chart_retries: int
    chart_output: Optional[object]
    report_summary: str
    final_report: dict
    error: str
    # Explainability fields
    query_analysis: dict
    schema_explanation: dict
    sql_explanation: dict
    kpi_explanations: dict
    table_scores: dict


# ---- Intent Classification Prompt ----
INTENT_SYSTEM_PROMPT = """Classify the user's manufacturing question into exactly one intent.

Respond with ONLY a JSON object, no explanation:
{"intent": "LOOKUP|AGGREGATION|COMPARISON|TREND|REPORT", "needs_chart": true|false}

INTENT DEFINITIONS:
- LOOKUP: fetch a specific record (e.g., "show me order PO-1042")
- AGGREGATION: summarize data with averages/totals (e.g., "what was average yield")
- COMPARISON: compare two groups or periods (e.g., "day shift vs night shift")
- TREND: show change over time (e.g., "yield trend for last 10 days")
- REPORT: full summary of a period/shift (e.g., "what happened last shift")

Return ONLY the JSON object."""


class AnalyticsAgent:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.llm = LLMProvider()
        self.executor = SQLExecutor(db_path)
        self.schema = extract_schema(db_path)
        
        # Initialize SchemaStore with Milvus config from environment
        milvus_host = os.getenv("MILVUS_HOST", "localhost")
        milvus_port = os.getenv("MILVUS_PORT", "19530")
        use_milvus = os.getenv("USE_MILVUS", "false").lower() == "true"
        
        self.store = SchemaStore(
            milvus_host=milvus_host,
            milvus_port=milvus_port,
            use_milvus=use_milvus
        )
        self.store.ingest(self.schema)
        
        # Initialize explainability modules
        self.query_analyzer = QueryAnalyzer()
        self.schema_explainer = SchemaExplainer()
        self.sql_explainer = SQLExplainer()
        self.kpi_explainer = KPIExplainer()
        
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the 5-node LangGraph workflow."""
        graph = StateGraph(AgentState)

        # Add nodes
        graph.add_node("classify_intent", self.classify_intent)
        graph.add_node("retrieve_schema", self.retrieve_schema)
        graph.add_node("generate_sql", self.generate_sql)
        graph.add_node("calculate_kpis", self.calculate_kpis_node)
        graph.add_node("assemble_report", self.assemble_report_node)

        # Set entry point
        graph.set_entry_point("classify_intent")

        # Linear flow with conditional on SQL
        graph.add_edge("classify_intent", "retrieve_schema")
        graph.add_edge("retrieve_schema", "generate_sql")
        graph.add_conditional_edges(
            "generate_sql",
            self._sql_router,
            {"success": "calculate_kpis", "retry": "generate_sql", "fatal": "assemble_report"},
        )
        graph.add_edge("calculate_kpis", "assemble_report")
        graph.add_edge("assemble_report", END)

        return graph.compile()

    # ---- Node 1: Intent Classifier ----
    def classify_intent(self, state: AgentState) -> dict:
        try:
            response = self.llm.generate(state["query"], INTENT_SYSTEM_PROMPT)
            # Parse JSON from response
            import json
            # Find JSON in response
            text = response.strip()
            if "{" in text:
                json_str = text[text.index("{"):text.rindex("}") + 1]
                result = json.loads(json_str)
                intent = result.get("intent", "AGGREGATION").upper()
                needs_chart = result.get("needs_chart", False)
            else:
                intent = "AGGREGATION"
                needs_chart = False
        except Exception:
            intent = "AGGREGATION"
            needs_chart = False

        valid_intents = {"LOOKUP", "AGGREGATION", "COMPARISON", "TREND", "REPORT"}
        if intent not in valid_intents:
            intent = "AGGREGATION"

        query_lower = state["query"].lower()
        if any(word in query_lower for word in ["plot", "chart", "graph", "visualize", "visualise"]):
            needs_chart = True

        # Generate query analysis with actual LLM intent for alignment reporting
        query_analysis = self.query_analyzer.analyze(state["query"], actual_intent=intent)

        return {
            "intent": intent,
            "needs_chart": needs_chart,
            "sql_retries": 0,
            "chart_retries": 0,
            "query_analysis": query_analysis
        }

    # ---- Node 2: Schema Retriever ----
    def retrieve_schema(self, state: AgentState) -> dict:
        # Get matched tables with scores
        matches = self.store.get_matched_tables(state["query"], top_k=4)
        
        # Extract table names and scores
        tables = [m["table"] for m in matches]
        scores = {m["table"]: m["score"] for m in matches}

        # Cap retrieval results BEFORE heuristics
        if len(tables) > 6:
            tables = tables[:6]

        # Heuristics add domain-critical tables (never capped)
        query_lower = state["query"].lower()
        if "yield" in query_lower or "trend" in query_lower:
            for table_name in ["production_orders", "line_master", "shift_logs", "products"]:
                if table_name in self.schema and table_name not in tables:
                    tables.append(table_name)
        
        if "cycle" in query_lower or "recipe" in query_lower:
            for table_name in ["recipes", "production_orders", "products"]:
                if table_name in self.schema and table_name not in tables:
                    tables.append(table_name)
        
        # Get schema context
        schema_context = get_schema_context(self.schema, tables)
        
        # Generate explanation
        schema_explanation = self.schema_explainer.explain_selection(
            query=state["query"],
            selected_tables=tables,
            scores=scores,
            method="keyword"  # or "semantic" when Milvus is enabled
        )
        
        return {
            "relevant_tables": tables,
            "schema_context": schema_context,
            "schema_explanation": schema_explanation,
            "table_scores": scores
        }

    # ---- Node 3: SQL Generator + Executor ----
    def generate_sql(self, state: AgentState) -> dict:
        error_ctx = state.get("error") if state.get("sql_retries", 0) > 0 else None
        prompt = build_sql_prompt(state["query"], state["schema_context"], error_ctx)
        response = self.llm.generate(prompt, SQL_SYSTEM_PROMPT)
        sql = parse_sql_response(response)

        # Validate
        validation = validate_sql(sql)
        if not validation["valid"]:
            return {
                "sql_query": sql,
                "sql_result": None,
                "error": validation["error"],
                "sql_retries": state.get("sql_retries", 0) + 1,
            }

        # Execute
        result = self.executor.execute(validation["cleaned_sql"])
        if not result["success"]:
            return {
                "sql_query": validation["cleaned_sql"],
                "sql_result": None,
                "error": result["error"],
                "sql_retries": state.get("sql_retries", 0) + 1,
            }

        # Generate SQL explanation
        sql_explanation = self.sql_explainer.explain_query(validation["cleaned_sql"])

        return {
            "sql_query": validation["cleaned_sql"],
            "sql_result": result["data"],
            "error": "",
            "sql_explanation": sql_explanation
        }

    # ---- SQL Router ----
    def _sql_router(self, state: AgentState) -> str:
        if state.get("sql_result") is not None and state.get("error", "") == "":
            return "success"
        if state.get("sql_retries", 0) >= 3:
            return "fatal"
        return "retry"

    # ---- Node 4: KPI Calculator ----
    def calculate_kpis_node(self, state: AgentState) -> dict:
        df = state.get("sql_result")
        if df is None or df.empty:
            return {"calculations": {"error": "No data available"}, "kpi_explanations": {}}
        
        kpis = calculate_kpis(df, state["intent"], state["query"])
        
        # Generate KPI explanations
        kpi_explanations = {}
        for kpi_name, kpi_value in kpis.items():
            if isinstance(kpi_value, (int, float)):
                kpi_explanations[kpi_name] = self.kpi_explainer.explain_kpi(
                    kpi_name=kpi_name,
                    value=kpi_value
                )
        
        return {
            "calculations": kpis,
            "kpi_explanations": kpi_explanations
        }

    # ---- Node 5: Report Assembler ----
    def assemble_report_node(self, state: AgentState) -> dict:
        df = state.get("sql_result")
        kpis = state.get("calculations", {})
        warnings = []
        if kpis.get("warning"):
            warnings.extend(kpis.pop("warning").split(" | "))

        error_text = (state.get("error") or "").lower()
        if "no such column" in error_text:
            warnings.append("SQL referenced a column that does not exist. This often means the schema context was incomplete or the wrong database was selected.")
        if "no such table" in error_text:
            warnings.append("SQL referenced a table that does not exist. Check the selected database and available tables.")
        if "syntax error" in error_text:
            warnings.append("SQL had a syntax error. Retrying may resolve this, or rephrase the question.")
        if "database is locked" in error_text:
            warnings.append("Database is locked. Try again in a few seconds or restart the app.")

        if df is not None:
            if state["intent"] == "LOOKUP" and len(df) > 50:
                warnings.append("Query returned many rows for a lookup — results may be too broad.")
            if state["intent"] == "TREND" and len(df) < 3:
                warnings.append("Insufficient data points for trend analysis.")

        # Handle fatal SQL error
        if df is None:
            report = assemble_report(
                query=state["query"],
                intent=state.get("intent", "UNKNOWN"),
                sql_query=state.get("sql_query", ""),
                df=pd.DataFrame(),
                kpis={},
                summary=f"Sorry, I couldn't retrieve data for your question. Error: {state.get('error', 'Unknown')}",
                chart_figure=None,
                tables_used=state.get("relevant_tables", []),
                warnings=warnings,
                db_path=self.db_path,
                query_analysis=state.get("query_analysis"),
                schema_explanation=state.get("schema_explanation"),
                sql_explanation=state.get("sql_explanation"),
                kpi_explanations=state.get("kpi_explanations"),
            )
            return {"final_report": report}

        # 5a: Generate text summary
        df_preview = df.head(5).to_string()
        summary_prompt = build_summary_prompt(state["query"], kpis, df_preview)
        try:
            summary = self.llm.generate(summary_prompt, SUMMARY_SYSTEM_PROMPT)
        except Exception as e:
            summary = f"Data retrieved: {len(df)} rows. KPIs: {kpis}"

        # 5b: Generate chart
        chart_fig = None
        if state["intent"] != "LOOKUP":
            # Try auto-chart first (deterministic, reliable)
            from src.report.chart_generator import auto_chart, build_chart_prompt, execute_chart_code, CHART_SYSTEM_PROMPT
            chart_fig = auto_chart(df, kpis, state["intent"], state["query"])

            # If auto-chart didn't produce anything, try LLM
            if chart_fig is None and state.get("needs_chart", True):
                df_info = f"Columns: {list(df.columns)}\nShape: {df.shape}\nFirst 3 rows:\n{df.head(3).to_string()}"
                chart_prompt = build_chart_prompt(
                    state["query"], state["intent"], kpis, df_info
                )
                if chart_prompt:
                    retries = 0
                    while retries < 2 and chart_fig is None:
                        try:
                            chart_code = self.llm.generate(chart_prompt, CHART_SYSTEM_PROMPT)
                            result = execute_chart_code(chart_code, df, kpis)
                            if result["success"]:
                                chart_fig = result["figure"]
                                try:
                                    if chart_fig is not None and getattr(chart_fig, "data", None):
                                        x_title = ""
                                        y_title = ""
                                        if getattr(chart_fig, "layout", None):
                                            if getattr(chart_fig.layout, "xaxis", None) and getattr(chart_fig.layout.xaxis, "title", None):
                                                x_title = (chart_fig.layout.xaxis.title.text or "").lower()
                                            if getattr(chart_fig.layout, "yaxis", None) and getattr(chart_fig.layout.yaxis, "title", None):
                                                y_title = (chart_fig.layout.yaxis.title.text or "").lower()

                                        if state["intent"] == "TREND":
                                            date_cols = [
                                                c for c in df.columns
                                                if any(k in c.lower() for k in ["date", "day", "time", "start", "end"])
                                            ]
                                            if date_cols and not x_title:
                                                warnings.append("Chart created but X-axis label is missing; expected a date-based axis for trend.")
                                        if state["intent"] == "COMPARISON":
                                            text_cols = [c for c in df.columns if df[c].dtype == "object"]
                                            if text_cols and not x_title:
                                                warnings.append("Chart created but X-axis label is missing; expected a grouping dimension for comparison.")
                                        if not x_title or not y_title:
                                            warnings.append("Chart created but axis labels are missing or unclear. Consider specifying the chart explicitly.")
                                except Exception:
                                    pass
                            else:
                                chart_prompt += f"\n\nPREVIOUS CODE FAILED: {result['error']}\nFix it."
                        except Exception:
                            pass
                        retries += 1

        if state.get("needs_chart") and chart_fig is None:
            warnings.append("Chart requested but could not be generated. Try a more specific chart request or check the data returned.")

        # 5c: Assemble
        report = assemble_report(
            query=state["query"],
            intent=state["intent"],
            sql_query=state["sql_query"],
            df=df,
            kpis=kpis,
            summary=summary,
            chart_figure=chart_fig,
            tables_used=state.get("relevant_tables", []),
            warnings=warnings,
            db_path=self.db_path,
            query_analysis=state.get("query_analysis"),
            schema_explanation=state.get("schema_explanation"),
            sql_explanation=state.get("sql_explanation"),
            kpi_explanations=state.get("kpi_explanations"),
        )
        return {"final_report": report}

    # ---- Public API ----
    def ask(self, question: str) -> dict:
        """Run a question through the full pipeline."""
        initial_state = {
            "query": question,
            "intent": "",
            "needs_chart": False,
            "relevant_tables": [],
            "schema_context": "",
            "sql_query": "",
            "sql_result": None,
            "calculations": {},
            "sql_retries": 0,
            "chart_code": "",
            "chart_retries": 0,
            "chart_output": None,
            "report_summary": "",
            "final_report": {},
            "error": "",
            # Initialize explainability fields
            "query_analysis": {},
            "schema_explanation": {},
            "sql_explanation": {},
            "kpi_explanations": {},
            "table_scores": {}
        }
        result = self.graph.invoke(initial_state)
        return result["final_report"]