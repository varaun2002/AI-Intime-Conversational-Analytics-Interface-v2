# Phase 1: Quick Start Guide

Get the transparency features up and running in under 5 minutes.

## Prerequisites

- Python 3.10+
- Ollama with DeepSeek Coder V2 running on `localhost:11434`
- Optional: Milvus (has in-memory fallback)

## Installation

```bash
# Install new dependency for SQL parsing
pip install sqlparse
```

That's it! The explainability modules are pure Python with no external service dependencies.

## Test the Components

```bash
# From project root, run the explainability test suite
python3 test_explainability.py
```

You'll see:
```
============================================================
Testing QueryAnalyzer
============================================================

📝 Query: What was the average yield for the day shift last week?
📊 Query Analysis:
Intent: AGGREGATION (confidence: 92%)
Reasoning: Query asks for summary statistics...
...

✅ QueryAnalyzer test passed!
...
============================================================
   ✅ ALL TESTS PASSED!
============================================================
```

## Run the App

```bash
# Start Streamlit
streamlit run ui/app.py

# Opens in browser at http://localhost:8501
```

## Try These Queries

### 1. Simple Aggregation (Tests Query Analysis)
```
"What was the average yield last week?"
```
Expected: Confidence ~90%, detects metrics=[yield], time=[last week]

### 2. Table-Specific Query (Tests Schema Selection)
```
"Show me the production orders from February"
```
Expected: Selects production_orders table with high confidence

### 3. Comparison Query (Tests SQL Complexity)
```
"Compare day shift vs night shift efficiency"
```
Expected: Complex query with JOIN, GROUP BY, multiple aggregations

### 4. Trend Query (Tests Chart Generation)
```
"Plot yield trend for the last 2 weeks"
```
Expected: Shows all 4 explanation types + chart

### 5. Report Query (Tests Multiple KPIs)
```
"Give me a full summary of yesterday's shift"
```
Expected: Multiple KPIs with individual explanations

## What You Should See

For each query, you'll now see below the main report:

### 📊 Query Analysis (Accordion)
```
Intent: [LOOKUP|AGGREGATION|COMPARISON|TREND|REPORT] (XX% confidence)
Reasoning: [Why we classified it this way]
Key Information Detected:
  • Metrics: [what metrics were found]
  • Time refs: [what time periods were found]
  • Comparisons: [what was compared]
Expected Tables: [table1, table2, ...]
Query Complexity: [simple|moderate|complex]
```

### 🗄️ Schema Selection (Accordion)
```
Summary: Selected N tables using [keyword|semantic] matching (XX% confidence)

Tables Selected:
  📋 table_name
     Score: 9.5
     Reason: [Why this table was selected]
     Purpose: [What this table contains]
```

### 🔍 SQL Query Explanation (Accordion)
```
Summary: [What the query does in one sentence]
Complexity: [simple|moderate|complex]

Plain English Explanation:
  • What's being calculated/retrieved
  • Which tables are involved
  • How tables are joined
  • Which filters are applied
  • How results are grouped/sorted

Performance Notes:
  [Recommendations for optimization]

[Formatted SQL query]
```

### 📈 KPI Explanations (Accordion)
```
For each calculated metric:
  • Value and units
  • Target range
  • Plain English interpretation
  • Formula used
  • Data sources
  • Key assumptions
```

## Example: Complete Walkthrough

### User Query
```
"What was the average yield for the day shift last week?"
```

### Query Analysis
```
Intent: AGGREGATION (confidence: 92%)
Reasoning: Query asks for summary statistics. Detected keywords: average, yield
Key Information Detected:
  • Metrics: yield
  • Comparisons: day shift
  • Time refs: last week
Expected Tables: production_orders, shift_logs
Query Complexity: moderate
```

### Schema Selection
```
Selected 2 tables using keyword matching (confidence: 85%)

📋 production_orders
   Score: 9.8
   Reason: Keywords matched: yield | Exact mention of yield data
   Purpose: Core manufacturing orders with planned vs actual quantities

📋 shift_logs
   Score: 8.2
   Reason: Keywords matched: shift | Contains shift type information
   Purpose: Daily shift information with supervisors and line assignments
```

### SQL Explanation
```
Summary: Aggregated query joining 2 tables with 1 filter(s)
Complexity: moderate

Plain English:
  Calculate:
    • avg_yield: Calculating average

  From tables:
    • production_orders (primary)
    • shift_logs (joined)

  Table relationships:
    • INNER JOIN shift_logs: Matching shift_id with production_order_id

  Filters applied:
    • Between: date >= '2024-01-01' and date < '2024-01-08'
    • Exact match: shift_type = 'day'

  Grouped by: shift_date

  Sorted by:
    • shift_date (DESC)

Performance Notes:
  ✓ Good: Aggregating entire dataset
  ✓ Date filter likely using index
```

### KPI Explanation
```
📋 avg_yield
   Value: 94.5 %
   Target: > 95%
   Interpretation: Below target but acceptable (value: 94.5)

   Formula: (Actual Quantity / Planned Quantity) × 100
   Description: Percentage of planned production actually achieved

   Data Sources:
   • production_orders (planned_quantity, actual_quantity)

   Assumptions:
   • Planned quantity represents actual production target
   • Actual quantity includes only good/accepted units
   • Partial orders are included in calculations
```

## Customizing Explanations

All explanation generators are modular in `src/explainability/`:

```python
# Customize intent patterns
src/explainability/query_analyzer.py:
  - INTENT_PATTERNS (add new intent types)
  - ENTITY_PATTERNS (add new entity types)

# Customize KPI definitions
src/explainability/kpi_explainer.py:
  - KPI_DEFINITIONS (edit formulas and ranges)
  - Define good/bad interpretation ranges

# Customize UI styling
src/report/explainability_ui.py:
  - Modify st.expander calls
  - Change emoji/formatting
  - Add/remove sections
```

## Troubleshooting

### Empty explanation sections
- **Cause**: Schema matching failed or no KPIs computed
- **Solution**: Check database connection and sample data

### "No syntax errors" but import fails
- **Cause**: Missing sqlparse dependency
- **Solution**: `pip install sqlparse`

### Explanations seem wrong
- **Cause**: Intent detection too conservative
- **Solution**: Adjust confidence thresholds in QueryAnalyzer

### Performance slow on large queries
- **Cause**: SQL parsing on complex queries
- **Solution**: Milvus will speed this up in Phase 3

## Architecture

```
User Question (plain English)
        ↓
   1️⃣  EXPLAINABILITY: QueryAnalyzer
        Understands: What are they asking?
        Outputs: Intent, entities, confidence
        ↓
   2️⃣  EXPLAINABILITY: SchemaExplainer
        Understands: Which tables are relevant?
        Outputs: Table scores, selection reasoning
        ↓
   3️⃣  EXPLAINABILITY: SQLExplainer
        Understands: What SQL was generated?
        Outputs: Plain English breakdown
        ↓
   4️⃣  EXPLAINABILITY: KPIExplainer
        Understands: What do these metrics mean?
        Outputs: Formulas, assumptions, ranges
        ↓
   Report with full transparency
```

## Next Steps

1. **Verify everything works**: `streamlit run ui/app.py`
2. **Test with your data**: Update `.env` with your database location
3. **Customize explanations** for your domain (Phase 2)
4. **Collect user feedback** on transparency/clarity
5. **Enable Milvus** when ready for semantic search (Phase 3)

## Documentation

- 📖 **Full Details**: [PHASE1_TRANSPARENCY.md](PHASE1_TRANSPARENCY.md)
- 📋 **Implementation Summary**: [PHASE1_SUMMARY.md](PHASE1_SUMMARY.md)
- 🛣️ **10-Week Roadmap**: [PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md)
- 📊 **Database Schema**: [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)

## Questions?

Check the test file for usage examples:
```bash
cat test_explainability.py  # See how each component is used
```

See the agent for integration points:
```bash
grep -n "explainability" src/agents/analytics_agent.py
```

## Status

✅ Phase 1 Complete  
✅ All components tested  
✅ UI integrated  
✅ Production ready for transparency requirements  

⏳ Coming Next: Phase 2 - Dynamic Context Engineering
