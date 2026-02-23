# Phase 1: Transparency & Explainability Implementation

## Overview

Phase 1 introduces a comprehensive transparency layer that explains every analytical decision to users in plain English. This provides full auditability and builds trust in the system's outputs.

## Components Implemented

### 1. **QueryAnalyzer** (`src/explainability/query_analyzer.py`)

**Purpose:** Analyzes user natural language queries to understand intent and extract key entities.

**Key Features:**
- Intent Classification (5 types):
  - **LOOKUP**: Fetch specific record (e.g., "show me order PO-1042")
  - **AGGREGATION**: Summarize data (e.g., "what was average yield")
  - **COMPARISON**: Compare groups (e.g., "day shift vs night shift")
  - **TREND**: Historical analysis (e.g., "yield trend last 10 days")
  - **REPORT**: Full summary (e.g., "what happened last shift")

- Entity Extraction (automatic detection of):
  - Table names (orders, shifts, lines, products, staff, etc.)
  - Metrics (yield, efficiency, performance, quality, etc.)
  - Time references (today, yesterday, last week, etc.)
  - Comparisons (day/night, morning/evening, etc.)
  - IDs (PO-1042, line-01, emp-123, etc.)

- Complexity Estimation (simple, moderate, complex)

**Output:**
```python
{
    "intent": "AGGREGATION",
    "confidence": 0.85,
    "reasoning": "Query asks for summary statistics. Detected keywords: yield, average",
    "key_entities": {
        "metrics": ["yield"],
        "time_refs": ["last 10 days"]
    },
    "expected_tables": ["production_orders", "shift_logs"],
    "query_type": "counting",
    "complexity": "moderate"
}
```

### 2. **SchemaExplainer** (`src/explainability/schema_explainer.py`)

**Purpose:** Explains why specific database tables were selected and how they match the query.

**Key Features:**
- Table selection reasoning with scores
- Keyword match explanations
- Context-based selection logic
- Comparison of different matching methods (keyword vs semantic)

**Output:**
```python
{
    "summary": "✓ Selected 2 tables using keyword matching (confidence: 85%)",
    "details": [
        {
            "table": "production_orders",
            "score": 9.5,
            "reason": "Exact match: 'orders' mentioned | Keywords matched: yield, planned, actual",
            "description": "Core manufacturing orders with planned vs actual quantities"
        },
        {
            "table": "shift_logs",
            "score": 7.2,
            "reason": "Keywords matched: shift",
            "description": "Daily shift information with supervisors and line assignments"
        }
    ],
    "method": "keyword",
    "confidence": 0.85,
    "total_tables_considered": 7,
    "tables_selected": 2
}
```

### 3. **SQLExplainer** (`src/explainability/sql_explainer.py`)

**Purpose:** Breaks down SQL queries into understandable components with plain English explanations.

**Key Features:**
- Automatic extraction of:
  - Tables and joins
  - Selected columns
  - WHERE filters
  - Aggregations (COUNT, SUM, AVG, etc.)
  - GROUP BY and ORDER BY
  - LIMIT clauses

- Plain English translation of complex SQL logic
- Performance considerations
- Complexity estimation

**Output:**
```python
{
    "summary": "Aggregated query joining 2 tables with 1 filter(s)",
    "plain_english": """
    Calculate:
      • total_yield: Calculating total sum
      • avg_efficiency: Calculating average

    From tables:
      • production_orders (primary)
      • shift_logs (joined)

    Table relationships:
      • INNER JOIN shift_logs: Matching shift_log_id with production_order_id

    Filters applied:
      • Greater than or equal to: date >= '2024-01-01'

    Grouped by: shift_date, shift_type
    
    Sorted by:
      • shift_date (ASC)

    Performance Notes:
      ✓ Good: Results limited for performance
      ✓ Date filter likely using index
    """,
    "complexity": "moderate",
    "components": { ... detailed breakdown ... }
}
```

### 4. **KPIExplainer** (`src/explainability/kpi_explainer.py`)

**Purpose:** Explains KPI calculations, formulas, and business logic.

**Key Features:**
- Formula documentation for 5 standard KPIs:
  - **Yield**: (Actual Qty / Planned Qty) × 100
  - **Efficiency**: (Actual Output / Standard Output) × 100
  - **OEE**: Availability × Performance × Quality
  - **Cycle Time**: Total Production Time / Units
  - **Utilization**: (Production Time / Available Time) × 100

- Interpretation ranges and meaning
- Data source identification
- Assumption documentation
- Comparative insights across KPIs

**Output:**
```python
{
    "kpi": "yield",
    "value": 97.5,
    "formula": "(Actual Quantity / Planned Quantity) × 100",
    "description": "Percentage of planned production actually achieved",
    "interpretation": "Meeting expectations (value: 97.5)",
    "units": "%",
    "good_range": "> 95%",
    "data_sources": [
        "production_orders (planned_quantity, actual_quantity)"
    ],
    "assumptions": [
        "Planned quantity represents actual production target",
        "Actual quantity includes only good/accepted units",
        "Partial orders are included in calculations"
    ]
}
```

### 5. **Explainability UI** (`src/report/explainability_ui.py`)

**Purpose:** Streamlit components to display explanations in the UI.

**Features:**
- Expandable query analysis section
- Schema selection visualization with scoring
- SQL explanation with formatted query display
- KPI cards with formula, targets, and assumptions
- Comprehensive explainability panel

**UI Components:**
- 📊 Query Analysis accordion
- 🗄️ Schema Selection accordion
- 🔍 SQL Query Explanation accordion
- 📈 KPI Explanations accordion

### 6. **Agent Integration**

Updates to `src/agents/analytics_agent.py`:

**New State Fields:**
```python
query_analysis: dict           # From QueryAnalyzer
schema_explanation: dict       # From SchemaExplainer
sql_explanation: dict          # From SQLExplainer
kpi_explanations: dict         # From KPIExplainer
table_scores: dict             # Table matching scores
```

**Modified Nodes:**
- **Node 1 (Intent)**: Now generates `query_analysis` with full breakdown
- **Node 2 (Schema)**: Now generates `schema_explanation` with scoring
- **Node 3 (SQL)**: Now generates `sql_explanation` with plain English
- **Node 4 (KPIs)**: Now generates `kpi_explanations` for each calculated KPI
- **Node 5 (Report)**: Includes all explanations in final report

## Usage Examples

### Example 1: Simple Yield Query
```
User: "What was the average yield for the day shift last week?"

Query Analysis:
  Intent: AGGREGATION (confidence: 92%)
  Reasoning: Detected keywords (average, yield)
  Entities: Metrics=[yield], Time=[last week], Comparisons=[day shift]
  Complexity: moderate
  
Schema Selection:
  Table 1: production_orders (score: 9.8) - Contains yield data
  Table 2: shift_logs (score: 8.5) - Contains shift type information
  
SQL Explanation:
  - Join shift_logs to production_orders on shift_id
  - Filter for day shift and last 7 days
  - Calculate: AVG(actual_qty / planned_qty) * 100
  - Group by shift_date
  
KPI Explanation:
  Yield = 94.5%
  Formula: (Actual Quantity / Planned Quantity) × 100
  Target: > 95%
  Status: Below target - needs improvement
```

### Example 2: Complex Comparison
```
User: "Compare line 1 efficiency vs line 2 last month, including cycle times"

Query Analysis:
  Intent: COMPARISON (confidence: 88%)
  Entities: Lines=[line 1, line 2], Metrics=[efficiency, cycle time], Time=[last month]
  Complexity: complex
  
Schema Selection:
  - production_steps (score: 9.9) - Contains cycle times
  - line_master (score: 8.7) - Contains line information
  - shift_logs (score: 7.5) - Contains time data
  
SQL Explanation:
  - Join 3 tables with line filters
  - Calculate efficiency per line: actual_time / standard_time
  - Calculate cycle time per line and product
  - Filter for last 30 days
  - Group and compare by line
```

## Update to Report Structure

Reports now include:
```python
{
    # ... existing fields ...
    "explainability": {
        "query_analysis": {...},      # How we understood the question
        "schema_explanation": {...},  # Why we chose these tables
        "sql_explanation": {...},     # What the SQL does
        "kpi_explanations": {...}     # What the metrics mean
    }
}
```

## Benefits

1. **Transparency**: Users understand exactly how their questions are being processed
2. **Trust**: Shows reasoning behind table and metric selection
3. **Auditability**: Full traceability of analytical decisions
4. **Learning**: Users learn about schema and KPI definitions
5. **Debugging**: Issues in matching or interpretation are visible
6. **Data Literacy**: Explanations help non-technical users understand SQL and KPIs

## Next Steps (Phase 2)

Phase 2 will implement **Dynamic Context Engineering**:
- Intelligent column selection based on query intent
- Automatic time window determination
- Relevance scoring for rows/subsets
- Sampling strategies for large datasets
- Context optimization in real-time

Phase 1 provides the foundation for transparent, explainable analytics that build user confidence and enable better decision-making.

## Testing

All components can be tested independently:

```python
# Test QueryAnalyzer
from src.explainability.query_analyzer import QueryAnalyzer
analyzer = QueryAnalyzer()
analysis = analyzer.analyze("What was average yield last week?")
print(analyzer.explain_analysis(analysis))

# Test SchemaExplainer
from src.explainability.schema_explainer import SchemaExplainer
explainer = SchemaExplainer()
explanation = explainer.explain_selection(
    query="Average yield",
    selected_tables=["production_orders"],
    scores={"production_orders": 9.8},
    method="keyword"
)
print(explainer.format_explanation(explanation))

# Test SQLExplainer
from src.explainability.sql_explainer import SQLExplainer
sql_explainer = SQLExplainer()
explanation = sql_explainer.explain_query(
    "SELECT AVG(yield) FROM production_orders WHERE date > '2024-01-01'"
)
print(sql_explainer.format_explanation(explanation))

# Test KPIExplainer
from src.explainability.kpi_explainer import KPIExplainer
kpi_explainer = KPIExplainer()
explanation = kpi_explainer.explain_kpi("yield", 94.5)
print(kpi_explainer.format_explanation(explanation))
```

---

**Status**: ✅ Phase 1 Complete  
**Next Phase**: Phase 2 - Dynamic Context Engineering  
**Documentation**: See [PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md) for full 10-week plan
