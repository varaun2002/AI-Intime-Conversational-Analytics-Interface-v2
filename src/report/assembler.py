"""
Combines all outputs into the final report object.
"""
from datetime import datetime


def assemble_report(
    query: str,
    intent: str,
    sql_query: str,
    df,
    kpis: dict,
    summary: str,
    chart_figure,
    tables_used: list,
    warnings: list = None,
    db_path: str = None,
    query_analysis: dict = None,
    schema_explanation: dict = None,
    sql_explanation: dict = None,
    kpi_explanations: dict = None,
) -> dict:
    """Build the final report dict with explainability information."""
    report = {
        "query": query,
        "intent": intent,
        "summary": summary,
        "kpis": kpis,
        "chart": chart_figure,
        "sql_query": sql_query,
        "tables_used": tables_used,
        "warnings": warnings or [],
        "db_path": db_path,
        "row_count": len(df) if df is not None else 0,
        "data": df,
        "timestamp": datetime.now().isoformat(),
        # Explainability information
        "explainability": {
            "query_analysis": query_analysis or {},
            "schema_explanation": schema_explanation or {},
            "sql_explanation": sql_explanation or {},
            "kpi_explanations": kpi_explanations or {},
        }
    }
    return report