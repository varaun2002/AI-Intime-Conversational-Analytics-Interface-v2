# AI InTime v2 - Setup & Startup Guide

## Quick Start (2 minutes)

### Step 1: Initialize Database
```bash
python3 startup.py
```

This will:
- ✅ Create the `sample_manufacturing.db` database with correct schema
- ✅ Populate it with 30 days of sample data (949 records across 7 tables)
- ✅ Start the Streamlit application

**That's it!** The app will open in your browser.

---

## Detailed Setup

### Prerequisites
- Python 3.9+
- Ollama running locally (`ollama serve` in another terminal)
- Dependencies installed (`pip install -r requirements.txt`)

### Database Issues?

If you get database schema errors like `no such column: line_master.location`:

**Option 1: Quick Fix (Recommended)**
```bash
python3 startup.py
```

**Option 2: Manual Setup**
```bash
# Create database with correct schema
python3 setup_database.py

# Verify everything works
python3 verify_setup.py

# Start the app
streamlit run ui/app.py
```

---

## Database Schema

The application uses **SQLite** with these tables:

| Table | Records | Purpose |
|-------|---------|---------|
| `line_master` | 4 | Production lines with location (Building A/B/C) |
| `products` | 4 | Product definitions |
| `recipes` | 4 | Manufacturing recipes |
| `staff` | 6 | Employee information |
| `shift_logs` | 240 | Daily shift records |
| `production_orders` | 117 | Manufacturing orders with yield data |
| `production_steps` | 578 | Step-by-step execution logs |

### Key Columns for Yield Analysis

**For "Building A vs Building B yield" query:**
- `line_master.location` → Building A, Building B, Building C
- `line_master.line_id` → LINE-1, LINE-2, LINE-3, LINE-4
- `production_orders.quantity_planned` → Target quantity
- `production_orders.quantity_actual` → Actual output
- **Yield Formula**: `(quantity_actual / quantity_planned) * 100`

---

## Testing Your Query

### Test Query: Building A vs Building B Yield
```sql
SELECT 
    lm.location,
    AVG((po.quantity_actual / po.quantity_planned) * 100) AS average_yield,
    COUNT(po.order_id) AS order_count
FROM 
    production_orders po
JOIN 
    line_master lm ON po.line_id = lm.line_id
WHERE 
    lm.location IN ('Building A', 'Building B')
GROUP BY 
    lm.location
```

**Expected Output:**
```
Building A | 89.3% | 35 orders
Building B | 91.2% | 32 orders
```

### Run in UI

In the Streamlit app, ask:
> "Compare yield between Building A and Building B"

or

> "Create a pie chart showing Building A vs Building B yield"

---

## Troubleshooting

### Issue: "no such column: line_master.location"
**Fix:** The database needs to be recreated
```bash
rm data/sample_manufacturing.db
python3 startup.py
```

### Issue: Ollama connection error
**Fix:** Start Ollama in a separate terminal
```bash
ollama serve
```

### Issue: Dependencies missing
**Fix:** Install requirements
```bash
pip install -r requirements.txt
```

### Issue: Port 8501 already in use (Streamlit)
**Fix:** Use a different port
```bash
streamlit run ui/app.py --server.port 8502
```

---

## How the System Works

1. **Schema Extraction** (`src/schema/extractor.py`)
   - Reads actual database schema at startup
   - Detects tables: line_master, products, recipes, etc.

2. **Intent Classification** (`src/agents/analytics_agent.py`)
   - Analyzes user question
   - Detects intent: COMPARISON for "Building A vs Building B"

3. **SQL Generation** (`src/sql/generator.py`)
   - LLM generates SQL with these rules:
     - Use `production_orders` for yield (NOT production_steps)
     - Join with `line_master` to get location
     - Filter by `location IN ('Building A', 'Building B')`

4. **SQL Validation** (`src/sql/validator.py`)
   - Checks for forbidden keywords (INSERT, UPDATE, DELETE, etc.)
   - Validates query structure

5. **Execution** (`src/sql/executor.py`)
   - Runs validated SQL safely
   - Catches errors and auto-fixes SQLite compatibility issues

6. **Yield Calculation** (`src/calculations/kpi_agent.py`)
   - Pure Pandas calculations (deterministic)
   - Validates: (actual / planned) * 100

7. **Chart Generation** (`src/report/chart_generator.py`)
   - Deterministic auto-chart (PIE chart for comparisons)
   - LLM fallback with sandboxed execution

---

## Example Queries

### Building Yield Comparison
```
"Show me the yield for Building A vs Building B"
"Create a pie chart comparing Building A and Building B yield"
"Which building has better yield - A or B?"
```

### Product Analysis
```
"What's the total output for each product?"
"Show yield by product"
"Compare ChemX-500 and PolyBlend-A performance"
```

### Timeline Analysis
```
"What was the yield trend over the last 10 days?"
"Show production volume by shift"
```

All queries will:
✅ Generate explanations (plain English)
✅ Show confidence scores
✅ Display validation status
✅ Create visualizations automatically

---

## Production Roadmap

- **Phase 1** ✅ DONE: Transparency layer (4 explainability modules)
- **Phase 2** (Next 3 weeks): Dynamic Context Engineering (adaptive SQL prompting)
- **Phase 3** (Production): Milvus semantic search + Production database scaling

See [PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md) for details.
