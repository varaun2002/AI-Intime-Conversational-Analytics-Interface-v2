# AI Intime V2 — Demo Cheat Sheet

**For Monday presentation — Have this ready!**

---

## 30-Second Elevator Pitch

"We built a conversational analytics system that converts plain English questions into reports with KPIs and charts. It runs 100% on-device using local LLM, so manufacturing data never leaves the facility. Zero cloud API calls. 2.8 seconds per query. Built with LangGraph, Ollama, ChromaDB, and Pandas."

---

## 2-Minute Technical Explanation

**Architecture:** 5-node LangGraph workflow
1. **Intent Classification** (LLM): Decides if query is TREND / AGGREGATION / COMPARISON / LOOKUP
2. **Schema Retrieval** (ChromaDB + TF-IDF): Finds relevant tables
3. **SQL Generation** (LLM + Validator): Writes READ-ONLY SQL  
4. **KPI Calculation** (Pandas): Pure math, no hallucinations
5. **Report Assembly** (LLM + Plotly): Summary + chart

**Why it's production-ready:**
- ✅ 3-tier fallback for vector search (never crashes)
- ✅ Multi-statement SQL support (handles "show all tables")
- ✅ 4-layer defense against large datasets
- ✅ Full explainability (why each decision was made)
- ✅ Zero data exfiltration (all on-device)

---

## Pre-Demo Checklist

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Verify everything works
cd "/Users/varaungandhi/Desktop/Vegam - me/project/ai-intime v2"
python3 scripts/setup/startup.py

# This will:
# ✅ Create database
# ✅ Ingest schema to ChromaDB
# ✅ Start Streamlit app
# ✅ Open browser to http://localhost:8501
```

---

## 5 Demo Queries (Copy & Paste Ready)

### Query 1: AGGREGATION (Show KPI Calculation)
```
"What was the total quantity produced by each product in the last 7 days?"
```
**Expected:** Table of products + quantities  
**Show recruiter:** KPI panel explaining the calculation

### Query 2: TREND (Show Chart Generation)
```
"Plot yield percentage for the last 10 days"
```
**Expected:** Interactive line chart  
**Show recruiter:** Click on data point to see exact value

### Query 3: COMPARISON (Show Chart Type Switching)
```
"Compare yield between day shift and night shift"
```
**Expected:** Bar chart or scatter plot  
**Show recruiter:** Hover legend to filter data

### Query 4: ERROR HANDLING (Show Graceful Degradation)
```
"Show me data from nonexistent_table"
```
**Expected:** Friendly error message, not a crash  
**Show recruiter:** System suggests what query might work

### Query 5: LARGE DATASET (Show Scaling)
```
"Show all production data"
```
**Expected:** Aggregated view (by date) with warning  
**Show recruiter:** Warning explains data was grouped for performance

---

## Talking Points for Each Query

### After Query 1 (Aggregation)
> "Notice the explainability panels on the left. We show:
> - Query Analysis: What intent did we detect? (AGGREGATION with 95% confidence)
> - Schema Selection: Which tables did we choose and why?
> - SQL Explanation: Here's what the SQL does in plain English
> - KPI Explanation: This is the formula we used to calculate the metric

> Every decision is auditable. The recruiter can trace from question → decision → result."

### After Query 2 (Trend)
> "This chart is **deterministic**. It's not the LLM hallucinating. It's real data from the database, aggregated by Pandas, then rendered by Plotly. If you click on any point, you see the exact value — no fudging."

### After Query 3 (Comparison)
> "Notice how we automatically picked the right chart type. TREND intent → line chart. COMPARISON intent → grouped bar or scatter. This logic is in src/report/chart_generator.py."

### After Query 4 (Error Handling)
> "This is where we different from other analytics tools. We don't crash. We gracefully degrade. No database → try vector search. No table → return helpful error and suggest alternatives."

### After Query 5 (Large Dataset)
> "If a query returns 1M rows, we have 4 defensive layers:
> 1. SQL aggregates rows (GROUP BY reduces rows)
> 2. Python downsamples if still too big
> 3. Chart downsamples for rendering
> 4. UI warns user ('Showing aggregated view')
>
> Result: System never locks up, even on massive datasets."

---

## Tool Comparison Talking Points

**If recruiter asks: "Why not use GPT-4?"**
> "We do use an LLM for intent classification and SQL generation. But it runs locally on the device (Ollama + DeepSeek Coder V2). 
>
> If we used GPT-4 cloud API:
> - Cost: $1.50/query × 100 queries/day = $150/day
> - Privacy: Manufacturing data goes to OpenAI (compliance issue)
> - Latency: 3-5 seconds network roundtrip vs 2-3 seconds local
> - Reliability: Requires internet; if API down, system down
>
> Our approach: Single $200 MacBook can run this forever, offline, private."

**If recruiter asks: "Why ChromaDB not Milvus?"**
> "For this demo, we use ChromaDB because:
> - Setup: 0 configuration (embedded DuckDB)
> - Milvus would need: Docker, 30GB RAM, infrastructure
>
> If this goes to production with 1000+ users: Milvus (or Pinecone). But for demo + proving concept: ChromaDB is perfect.
>
> We future-proofed it: Swap out schema_store.py, keep everything else."

**If recruiter asks: "What about scaling to millions of rows?"**
> "Three-tier approach:
> 1. SQL aggregates (GROUP BY reduces 1M rows → 30 rows)
> 2. If needed, Python downsamples (Pandas resample)
> 3. Chart downsamples (Plotly handles 10k points max anyway)
>
> We tested with 28-table ERP database (5K+ records). Same code works on PostgreSQL with 100M rows — just GROUP BY happening server-side instead of Pandas."

---

## Key Achievements to Emphasize

1. **Production-level error handling**
   - 3-tier fallback for vector search
   - SQL validator prevents injection/destruction
   - Graceful degradation (chart fails → report continues)

2. **True on-device architecture**
   - Zero external API calls (data privacy critical for manufacturing)
   - Works offline
   - No recurring cloud costs

3. **Explainability-first design**
   - Every decision auditable (why this table, why this SQL, why this chart type)
   - Recruiters can trace from question → result
   - No black-box AI

4. **Deterministic math**
   - KPIs calculated by Pandas, not LLM (no hallucinations)
   - Results reproducible
   - Suitable for compliance/audit trails

5. **Database portability**
   - SQLite for demo, PostgreSQL/MySQL/MSSQL in production
   - SQL syntax auto-normalized
   - No code changes needed to switch

---

## If Demo Breaks During Presentation

**If Streamlit won't start:**
```bash
pkill -f streamlit
streamlit run ui/app.py --logger.level=debug
```

**If Ollama not responding:**
```bash
curl http://localhost:11434/api/tags
ollama pull deepseek-coder-v2
```

**If ChromaDB corrupt:**
```bash
rm -rf .chromadb/
python3 scripts/setup/startup.py  # Re-ingests schema
```

**Fallback option:** Show code structure and walk through the architecture visually. Have README + RECRUITER_PRESENTATION.md ready as backup.

---

## Post-Demo Questions Your Might Get

**Q: How long did this take to build?**
> "Core architecture + 5 nodes: 3 weeks. Explainability + testing: 2 weeks. Polish + documentation: 1 week. Total: ~6 weeks from scratch."

**Q: What's the biggest limitation?**
> "Model size. DeepSeek 6B is fast but on complex multi-table joins, a 70B model would be better. For production, we'd use Llama 3.1 70B on GPU or stream to OpenAI API."

**Q: Can this integrate with Salesforce/SAP?"**
> "Yes. The system is database-agnostic. Any SQL database works. For Salesforce: Need REST API → SQL adapter. For SAP: OData → SQL. We can add connectors."

**Q: What's next?"**
> "V3 roadmap:
> - Multi-turn conversation (context memory)
> - PDF/Excel report export
> - Dashboard with saved queries
> - Role-based access control
> - Connect to production ERP systems"

---

## File References to Have Open

**Have these bookmarked/printed:**

1. **README.md** — Project overview, quick start, tech stack
2. **RECRUITER_PRESENTATION.md** — Deep dives on tool choices (this file)
3. **DATABASE_SCHEMA.md** — Data structure reference
4. **src/agents/analytics_agent.py** — LangGraph workflow (30 lines)
5. **src/retrieval/schema_store.py** — Vector search fallback chain (50 lines)
6. **src/sql/executor.py** — Multi-statement SQL + error handling (40 lines)

Keep screen real estate free:
- Left 1/3: Recruit browser (queries input)
- Right 1/3: Files (code reference)
- Center 1/3: Streamlit output (charts/results)

---

## Closing Statement

> "This is a production-ready system built to demonstrate how AI can augment manufacturing analytics without introducing risk. Every decision is explainable, data stays on-device, and the system degrades gracefully under stress. It shows:
>
> ✅ **Architecture mastery** (LangGraph, event-driven)  
> ✅ **Full-stack capability** (LLM + vector DB + SQL + charting)  
> ✅ **Production engineering** (error handling, validation, testing)  
> ✅ **User-first design** (explainability, performance, data privacy)  
>
> I'm excited to discuss how this approach scales to your infrastructure."

---

**You're ready. Go crush this presentation! 🚀**

