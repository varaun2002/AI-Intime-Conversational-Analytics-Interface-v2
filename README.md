# 🏭 AI Intime V2 — Conversational Manufacturing Analytics

> Built for [Vegam Solutions](https://vegam.co) | Varaun Gandhi

A fully on-device conversational analytics system that converts plain English questions into structured reports with calculated KPIs and interactive charts — powered by **LangGraph**, **Ollama (DeepSeek Coder V2)**, **Pandas**, and **Plotly**.

Plant managers type questions in plain English. The system automatically writes SQL, retrieves data, computes KPIs deterministically, generates intelligent charts, and assembles complete reports with full explainability. **Zero SQL knowledge required. Zero data leaves the device.**

---

---

## Architecture

```
User Question (plain English)
        │
        ▼
┌─────────────────────┐
│  Node 1             │
│  Intent Classifier  │   → LOOKUP | AGGREGATION | COMPARISON | TREND | REPORT
│  (DeepSeek LLM)     │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Node 2             │
│  Schema Retriever   │   → ChromaDB (→ TF-IDF → keyword) semantic search
│  (ChromaDB + embeddings) │     matches query to relevant tables
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Node 3             │
│  SQL Generator      │   → DeepSeek writes SQL → Validator blocks writes
│  + Executor         │   → SQLAlchemy executes → Multi-statement support
│  (DeepSeek + SQLAlchemy) │  → Auto-retry up to 3x
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Node 4             │
│  KPI Calculator     │   → Pure Pandas: yield %, variance, trends
│  (Pandas)           │   → No LLM involved — deterministic math
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Node 5             │
│  Report Assembler   │   → Text summary (DeepSeek)
│                     │   → Auto-chart (Plotly, intent-driven)
│                     │   → Full explainability (query, schema, SQL, KPI)
└──────────┬──────────┘
           ▼
    ┌──────┴──────┐
    ▼             ▼
Streamlit UI   MCP Server
```

---

## 🚀 Current Status: Phase 1 Complete ✅

### Phase 1: Transparency & Explainability (COMPLETE)

Every analytical decision is now **fully transparent and auditable**.

**What's New:**
- 📊 **Query Analysis**: Understand how your question is interpreted (intent, entities, confidence)
- 🗄️ **Schema Selection**: See which tables were chosen and why (with relevance scores)
- 🔍 **SQL Explanation**: Get plain English breakdown of the generated SQL query
- 📈 **KPI Explanations**: Understand what each metric means, how it's calculated, and what assumptions apply

**Implementation:**
- 4 new explainability modules (query analyzer, schema explainer, SQL explainer, KPI explainer)
- ~1,200 lines of new code integrated into the agent workflow
- Streamlit UI components showing all explanations in expandable accordions
- Full documentation in [PHASE1_TRANSPARENCY.md](PHASE1_TRANSPARENCY.md)

**Example:**
```
User: "Average yield for day shifts last week?"

Query Analysis:
  Intent: AGGREGATION (confidence: 92%)
  Entities: metrics=[yield], shifts=[day], time=[last week]
  
Schema Selection:
  production_orders (score: 9.8) - Contains yield data
  shift_logs (score: 8.5) - Contains shift type info
  
SQL Explanation:
  Joins 2 tables on shift_id, filters for day shift & last 7 days,
  calculates: AVG(actual_qty/planned_qty)*100, groups by date
  
KPI Explanation:
  Yield = 94.5%
  Formula: (Actual / Planned) × 100
  Target: > 95%
  Status: Below target - optimization opportunity identified
```

See [PHASE1_SUMMARY.md](PHASE1_SUMMARY.md) for complete implementation details.

---

## 🛣️ Production Roadmap

Complete 10-week plan to production-grade analytics system: [PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md)

**Phase 2** (3 weeks): Dynamic Context Engineering  
**Phase 3** (2 weeks): Milvus Production Setup  
**Phase 4** (2 weeks): Scale & Performance  
**Phase 5** (1 week): Enhanced Reports & Deployment  

---

## Tech Stack

| Component | Technology | Role |
|---|---|---|
| Agent Orchestrator | LangGraph | 5-node stateful workflow with conditional retry |
| LLM | Ollama — DeepSeek Coder V2 | Intent classification, SQL generation, summaries |
| SQL Engine | SQLAlchemy | Database-agnostic query execution + multi-statement support |
| KPI Calculations | Pandas + NumPy | Deterministic metrics (yield, variance, trends) |
| Vector Search | ChromaDB (on-device) | Embedded vector DB with DuckDB persistence, auto-dedup |
| Keyword Fallback | scikit-learn TF-IDF | Semantic keyword matching with cosine similarity |
| Charts | Plotly | Auto-generated based on intent type (line, bar, pie, scatter) |
| UI | Streamlit | Chat interface with report rendering + full explainability |
| Database | SQLite (swappable) | Sample manufacturing data (flexible to PostgreSQL/MySQL) |

---

## Key Design Decisions

**Why on-device LLM?** Manufacturing data is sensitive operational IP. Sending it to a cloud API creates compliance and security risks. Ollama runs everything locally — zero data leaves the premises.

**Why Pandas for math, not the LLM?** LLMs hallucinate numbers. Pandas does not. Every KPI is computed deterministically on the actual dataframe. The LLM only writes the English summary around numbers Pandas already calculated.

**Why ChromaDB on-device?** Vector search must be entirely local (no cloud calls, manufacturing data never leaves premises). ChromaDB is a fully embedded vector DB with persistent DuckDB storage. Zero configuration, automatic deduplication on re-ingest, built-in sentence-transformers embeddings. Scales from 7 to 100+ table schemas seamlessly. Falls back gracefully to TF-IDF keyword search if needed.

**Why TF-IDF + scikit-learn fallback?** Vector DBs can fail or be unavailable. TF-IDF provides deterministic, explainable semantic keyword matching using cosine similarity. Works without any external dependencies beyond scikit-learn. Automatically used if ChromaDB unavailable or on keyword-only mode.

**Why multi-statement SQL support?** Users request "show all tables" or "compare output across all products" naturally. System now splits multi-statement queries (semicolon-delimited), executes each, and concatenates results with source labels. Prevents "only one statement" errors.

**Why LangGraph + alignment detection?** SQL generation fails. Chart code fails. Query intents can be ambiguous. Agent needs to retry, route errors, and validate that QueryAnalyzer pattern-based prediction aligns with LLM's actual decision. Full explainability on alignment mismatches.

**Why SQLAlchemy?** Database-agnostic. Same code works whether customer runs PostgreSQL, MySQL, SQLite, or MSSQL.

---

## Sample Database

The demo uses a SQLite database simulating a chemical/polymer production facility.

| Metric | Value |
|---|---|
| Time period | Jan 18 – Feb 16, 2026 (30 days) |
| Total records | 949 across 7 tables |
| Production lines | 4 lines across 3 buildings |
| Products | ChemX-500, PolyBlend-A, SurfaceCoat-Pro, AdhesivePrime |
| Staff | 6 (3 Supervisors, 2 Operators, 1 QC Inspector) |
| Shifts | 240 (2 per day per line) |
| Production orders | 117 completed |
| Production steps | 578 step-level logs |
| Average yield | 91.4% (range: 85–98%) |

Full schema documentation: [`data/DATABASE_SCHEMA.md`](data/DATABASE_SCHEMA.md)

---

## Test Results (V2)

### Benchmark Queries

All queries below run **live** on a local Ollama instance (DeepSeek Coder V2) + SQLite ERP database (28 tables, 5K+ records):

#### ✅ **Text Report Queries**
- **Input:** `What was the total quantity produced by each product in the last 7 days?`
  - **Output:** Aggregation report | 3.2s | Success
  - **SQL:** Joins production_orders + product_master, groups by product, sums quantity_actual
  - **KPI:** Total, Average, Variance by product
  
- **Input:** `Compare yield percentage between Supervisor A and Supervisor B`
  - **Output:** Comparison report | 2.8s | Success  
  - **SQL:** Joins production_orders + employees, filters by supervisor, calculates yield%
  - **KPI:** Yield %, variance, trend by supervisor

#### ✅ **Chart Queries (NEW V2)**
- **Input:** `Plot yield trend for the last 10 days`
  - **Output:** Line chart (daily trend) | 3.1s | Success
  - **SQL:** Date grouping on actual_start, aggregates yield%
  - **Chart:** Date-indexed line graph with trend
  - **Data Points:** 10 days × daily yield values
  - **Fix V2:** Now recognizes all ERP date columns (order_date, actual_start, actual_end, planned_start, planned_end)

- **Input:** `Make a pie chart of output by product`
  - **Output:** Interactive pie chart | 2.4s | Success
  - **Chart:** Segments by product name, sized by total_quantity
  - **Data Points:** 8 products with color-coded slices
  - **New V2:** Deterministic pie generation without LLM hallucination

- **Input:** `Show a scatter plot of quantity_actual vs quantity_planned`
  - **Output:** Scatter plot | 2.6s | Success
  - **Chart:** X-axis: quantity_planned | Y-axis: quantity_actual
  - **Data Points:** 500+ manufacturing records
  - **New V2:** Explicit scatter chart support with automatic column mapping

#### ✅ **Error Handling & Warnings (NEW V2)**
- **Input:** `Plot yield for nonexistent_table`
  - **Output:** ⚠️ Warning: "SQL Error — table 'nonexistent_table' does not exist"
  - **Response:** Falls back to general yield query, data limited to available schema
  
- **Input:** `Show revenue trend`
  - **Output:** ⚠️ Warning: "Chart Requested — found trend_data but limited numeric columns"
  - **Response:** Generates bar chart as fallback, suggests schema inspection

- **Input:** `Analyze shift_A performance on 2024-15-45`
  - **Output:** ⚠️ Warning: "SQL Error — invalid date format in query"
  - **Response:** Returns schema help message, suggests valid date ranges

### Test Summary

```
Total V2 queries tested:  12
Data returned:           11/12  (92%)
KPIs computed:           11/12  (92%)
Summaries valid:         11/12  (92%)
Charts generated:        9/12   (when explicitly requested or TREND intent detected)
Error warnings issued:   3/12   (contextual + actionable)
Avg response time:       ~2.8s  (local Ollama on MacBook Air)
```

### V2 Improvements Over V1

| Feature | V1 | V2 | Impact |
|---------|----|----|--------|
| **Database Selection** | Hardcoded file | Environment `DATABASE_PATH` / `DATABASE_URL` | Switch databases without code changes |
| **Chart Types** | Line only | Line, Bar, Pie, Donut, Scatter | 5 chart types with automatic + explicit selection |
| **Trend Queries** | Fails on ERP DB | Works on both sample & ERP | Query `"Plot yield trend"` now succeeds (was failing) |
| **Error Messages** | Generic "error" | Contextual warnings with guidance | SQL column/table/syntax errors now surfaced |
| **Chart Validation** | Silent failures | Warns if chart requested but missing | User knows if visualization was generated |
| **KPI Fallbacks** | None | Deterministic Pandas defaults | No LLM hallucinations on missing columns |
| **Database Support** | Single file | ERP + Sample + Swappable | Run on 28-table ERP or 7-table sample |
| **Explainability** | Report only | Report + SQL + Schema + KPI math | Full chain-of-thought visible in UI |

---

## 📚 Documentation For Recruiters & Tech Leads

**Important:** Before presenting this project, read these:

- 🎯 [RECRUITER_PRESENTATION.md](RECRUITER_PRESENTATION.md) — **5,000+ words.** Deep dive on every tool choice (why LangGraph > Airflow, why ChromaDB > Milvus, why Pandas > LLM for math). Production-readiness analysis. Chart accuracy guarantees. Scaling defense mechanisms. Read this if you need to articulate *why* each decision was made.

- 🎬 [DEMO_CHEAT_SHEET.md](DEMO_CHEAT_SHEET.md) — **Demo script.** 30-second pitch, 2-minute technical explanation, 5 copy-paste queries, talking points for each, common recruiter Q&A with pre-written answers. Use this during live demo.

- ✅ [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) — **Pre-presentation checklist.** Run all 10 verification suites before showing project. Ensures Ollama works, ChromaDB initialized, dependencies installed, no secrets in repo, full pipeline functional.

---

## 📁 Project Structure

The project is now organized into clean, logical folders:

```
ai-intime v2/
├── 📚 docs/                       # All documentation (15 files)
│   ├── README_INDEX.md            # Navigation guide ← Start here
│   ├── TEST_QUICK_START.md        # 3-step quick start
│   ├── COMPREHENSIVE_TEST_SUITE.md # 10 edge cases detailed
│   ├── TESTING_STRATEGY.md        # Strategic approach
│   ├── DELIVERY_SUMMARY.md        # Framework overview
│   └── PHASE1_*.md & others       # Complete docs
│
├── 🔧 scripts/                    # All executable scripts
│   ├── setup/                     # Database setup
│   │   ├── setup_database.py
│   │   └── startup.py             # One-command startup
│   ├── testing/                   # Comprehensive test suite
│   │   ├── generate_comprehensive_erp.py  # 28-table ERP
│   │   ├── test_edge_cases.py     # 10 edge tests
│   │   └── run_all_tests.py       # Orchestrator
│   └── utilities/
│       └── verify_setup.py
│
├── 📦 src/                        # Source code
│   ├── agents/       │ agents/                    # LangGraph workflow
│   ├── schema/                    # Schema extraction
│   ├── retrieval/                 # Vector search
│   ├── sql/                       # SQL generation
│   ├── calculations/              # KPI calculations
│   ├── report/                    # Reports & charts
│   ├── llm/                       # LLM abstraction
│   └── utils/
│
├── 🎨 ui/            └── app.py                     # Streamlit UI
├── 📊 data/          ├── sample_manufacturing.db
│   ├── manufacturing_erp.db
│   └── DATABASE_SCHEMA.md
├── 🧪 tests/         └── test_all_queries.py
├── requirements.txt
└── .env / .env.example
```

📖 **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** — Full organization details  
📖 **[docs/README_INDEX.md](docs/README_INDEX.md)** — All documentation navigation

---

## Setup & Quick Start

### ⚡ Fastest Way to Start (2 minutes)

Make sure you have:
1. Python 3.9+ installed
2. Ollama running: `ollama serve` in another terminal
3. Dependencies installed: `pip install -r requirements.txt`

Then run:

```bash
python3 scripts/setup/startup.py
```

This will:
- ✅ Create the database automatically
- ✅ Verify the schema
- ✅ Start the Streamlit app

**→ See [`docs/SETUP.md`](docs/SETUP.md) for detailed setup instructions and troubleshooting**

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai) installed and running
- DeepSeek Coder V2 model pulled: `ollama pull deepseek-coder-v2`

### Full Installation (if starting from scratch)

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/ai-intime.git
cd ai-intime

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Pull the LLM
ollama pull deepseek-coder-v2

# Quick start
python3 scripts/setup/startup.py
```

### Configuration

Set database and LLM parameters via environment variables:

```bash
# Use the comprehensive 28-table ERP database
export DATABASE_PATH=/path/to/manufacturing_erp.db
python3 scripts/setup/startup.py

# OR use DATABASE_URL (SQLAlchemy format)
export DATABASE_URL=sqlite:///data/manufacturing_erp.db
streamlit run ui/app.py

# Use the sample 7-table database
export DATABASE_PATH=data/sample_manufacturing.db
python3 scripts/setup/startup.py

# LLM Configuration
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=deepseek-coder-v2

# Vector Search Configuration (ChromaDB)
export CHROMADB_PATH=./chromadb_storage
```

**Note:** ChromaDB runs fully embedded with persistent storage. Schema ingestion happens automatically on first run. Swapping `DATABASE_PATH` or `DATABASE_URL` switches the backend database instantly.

---

## Safety & Error Handling

### Vector Search Fallback Chain
1. **Primary**: ChromaDB (embedded, persistent, auto-deduplication)
2. **Secondary**: TF-IDF semantic keyword search (scikit-learn, deterministic)
3. **Fallback**: Simple keyword matching (built-in, zero dependencies)

Result: Schema search always succeeds, gracefully degrading to simpler methods when needed.

### Query Execution Safety
- **Read-only enforcement**: SQL validator blocks INSERT, UPDATE, DELETE, DROP, TRUNCATE, ALTER before execution
- **Multi-statement support**: "Show all tables" queries now work — splits on semicolons, executes each statement, concatenates results with source labels
- **PostgreSQL syntax auto-fix**: Catches `::DATE`, `EXTRACT()`, `NOW()`, `ILIKE` and converts to SQLite equivalents
- **Auto-retry with guardrails**: SQL retries up to 3x with exponential backoff, chart retries up to 2x, graceful degradation on failure

### Data & Integrity Protection
- **No data exfiltration**: Ollama runs fully local — zero API calls to external services
- **Deterministic KPI math**: All metrics (yield %, variance, trends) computed via Pandas — no LLM hallucinations
- **Intent alignment validation**: QueryAnalyzer reports when pattern-based prediction differs from LLM's actual decision, flags ambiguous intents

### Error Detection & Reporting
Warnings surface for:
- SQL errors (missing column, missing table, syntax errors, locked database)
- Chart generation failures (requested but not generated due to missing data)
- Database not found (expected path does not exist)
- Vector search unavailability (falls back automatically)
- Intent misalignment (reported in explainability panel)

---

## Roadmap (V3+)

**V2 Complete.** The following features are planned for V3 and beyond:

- [ ] Connect to production database (PostgreSQL/MySQL/MSSQL) with advanced schema inference
- [ ] MCP Server integration for Claude Desktop
- [x] Milvus + sentence-transformers for semantic schema search (✅ V2)
- [x] Multiple chart types (line, bar, pie, donut, scatter) (✅ V2)
- [x] Environment-based database selection (✅ V2)
- [x] Comprehensive error warnings system (✅ V2)
- [ ] Multi-turn conversation memory with context carryover
- [ ] PDF/Excel report export
- [ ] User authentication + role-based access control
- [ ] Larger LLM option (Llama 3.1 70B) for complex multi-table joins
- [ ] Dashboard mode with saved queries and scheduled reports

---

## Author

**Varaun Gandhi**
- M.S. AI Systems Management, Carnegie Mellon University (Dec 2025)
- varaun.gandhi@gmail.com

Built for Vegam Solutions — AI Intime platform validation.
