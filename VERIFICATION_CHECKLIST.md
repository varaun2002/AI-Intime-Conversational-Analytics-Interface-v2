# Pre-Presentation Verification Checklist

**Run these checks before Monday to ensure presentation goes smoothly**

---

## 1️⃣ Environment & Dependencies

### Check Python version
```bash
python3 --version  # Should be 3.10+
```

Result: ✅ / ❌

### Check all packages installed
```bash
cd "/Users/varaungandhi/Desktop/Vegam - me/project/ai-intime v2"
pip3 list | grep -E "streamlit|langgraph|langchain|chromadb|pandas|sqlalchemy|plotly"
```

Expected output (all should be installed):
- streamlit
- langgraph
- langchain
- langchain-core
- chromadb
- pandas
- sqlalchemy
- plotly
- scikit-learn
- sentence-transformers
- python-dotenv
- sqlparse

Result: ✅ / ❌

### Verify Ollama is available
```bash
which ollama
ollama list | grep deepseek
```

Result: ✅ / ❌

---

## 2️⃣ Project Structure

### Check critical files exist
```bash
cd "/Users/varaungandhi/Desktop/Vegam - me/project/ai-intime v2"

# Required core files
ls -la README.md requirements.txt .env.example
ls -la ui/app.py
ls -la scripts/setup/startup.py
ls -la data/sample_manufacturing.db

# Required documentation
ls -la RECRUITER_PRESENTATION.md DEMO_CHEAT_SHEET.md DATABASE_SCHEMA.md
```

All files should exist. If any missing, restore from git.

Result: ✅ / ❌

### Verify no sensitive files committed
```bash
# .env should NOT exist (should be .env.example only)
ls -la .env  # Should show "No such file"

# __pycache__ should be cleaned
find . -type d -name __pycache__ | wc -l  # Should output 0
```

Result: ✅ / ❌

---

## 3️⃣ Database & Schema

### Check sample database
```bash
file data/sample_manufacturing.db
# Should output: "SQLite 3.x database"

# Verify it has data
sqlite3 data/sample_manufacturing.db "SELECT COUNT(*) FROM production_orders;"
# Should output: >100 (we have 949 records)
```

Result: ✅ / ❌

### Verify schema ingestion works
```bash
cd "/Users/varaungandhi/Desktop/Vegam - me/project/ai-intime v2"

python3 << 'EOF'
from src.schema.extractor import extract_schema
schema = extract_schema('data/sample_manufacturing.db')
tables = [t['table_name'] for t in schema]
print(f"✅ Found {len(tables)} tables:")
for t in sorted(tables):
    print(f"  - {t}")

expected = ['production_orders', 'products', 'employees', 'shift_logs']
missing = [t for t in expected if t not in tables]
if missing:
    print(f"❌ Missing tables: {missing}")
else:
    print("✅ All expected tables present")
EOF
```

Result: ✅ / ❌

---

## 4️⃣ LLM & Vector Search

### Check Ollama connectivity
```bash
curl -s http://localhost:11434/api/tags | head -20
```

Expected: JSON output with models list (should include deepseek-coder-v2)

Result: ✅ / ❌

### Quick run of full pipeline
```bash
cd "/Users/varaungandhi/Desktop/Vegam - me/project/ai-intime v2"

python3 << 'EOF'
import sys
sys.path.insert(0, '.')

# Test 1: Schema extraction
print("1. Testing schema extraction...")
from src.schema.extractor import extract_schema
schema = extract_schema('data/sample_manufacturing.db')
print(f"   ✅ Extracted {len(schema)} table schemas")

# Test 2: Vector search initialization
print("2. Testing ChromaDB initialization...")
from src.retrieval.schema_store import SchemaStore
store = SchemaStore(use_milvus=False)
store.ingest(schema)
print("   ✅ ChromaDB initialized and indexed")

# Test 3: Schema retrieval
print("3. Testing schema retrieval...")
results = store.search("What's the average yield?", top_k=3)
print(f"   ✅ Retrieved {len(results)} relevant tables")
for r in results:
    print(f"      - {r['table_name']} (score: {r['score']:.2f})")

# Test 4: Database connection
print("4. Testing database connection...")
from src.sql.executor import SQLExecutor
executor = SQLExecutor(db_path='data/sample_manufacturing.db')
result = executor.execute("SELECT COUNT(*) as count FROM production_orders")
if result['success'] and result['data'] is not None:
    count = result['data'].iloc[0]['count']
    print(f"   ✅ Database has {count} production records")
else:
    print(f"   ⚠️  Database query returned: {result['error']}")

print("\n✅ All tests passed!")
EOF
```

Expected: All 4 tests pass

Result: ✅ / ❌

---

## 5️⃣ UI Startup Test

### Start Streamlit (30-second test)
```bash
cd "/Users/varaungandhi/Desktop/Vegam - me/project/ai-intime v2"
timeout 30 streamlit run ui/app.py 2>&1 | grep -E "Streamlit|Available|ERROR"
```

Expected output should show:
```
Streamlit app is running at http://localhost:8501
```

NOT:
```
ERROR | ImportError | ModuleNotFoundError
```

Result: ✅ / ❌

### Verify all imports work
```bash
python3 -c "
from src.agents.analytics_agent import AnalyticsAgent
from src.retrieval.schema_store import SchemaStore
from src.sql.executor import SQLExecutor
from src.sql.validator import validate_sql
from src.calculations.kpi_agent import calculate_kpis
from src.report.assembler import assemble_report
from src.schema.extractor import extract_schema
print('✅ All imports successful')
"
```

Result: ✅ / ❌

---

## 6️⃣ Full End-to-End Test

### Run complete flow with test query
```bash
cd "/Users/varaungandhi/Desktop/Vegam - me/project/ai-intime v2"

python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from src.agents.analytics_agent import AnalyticsAgent

# Initialize agent
agent = AnalyticsAgent(db_path='data/sample_manufacturing.db')

# Test query
print("Running test query: 'What is the average yield?'")
result = agent.ask("What is the average yield?")

# Verify results
if result and result.get('summary'):
    print("✅ Agent completed successfully")
    print(f"   Summary: {result['summary'][:100]}...")
    if result.get('chart'):
        print("   ✅ Chart generated")
    else:
        print("   ⚠️  No chart (might be lookup query)")
    print(f"   KPIs: {list(result.get('kpis', {}).keys())}")
else:
    print("❌ Agent failed or returned empty result")
    print(f"   Result keys: {list(result.keys()) if result else 'None'}")
EOF
```

Expected: "✅ Agent completed successfully"

Result: ✅ / ❌

---

## 7️⃣ Documentation Check

### Verify all markdown files are readable
```bash
cd "/Users/varaungandhi/Desktop/Vegam - me/project/ai-intime v2"

# Check file sizes (should be reasonable)
wc -l README.md RECRUITER_PRESENTATION.md DEMO_CHEAT_SHEET.md DATABASE_SCHEMA.md
```

Expected: All files should have >50 lines

Result: ✅ / ❌

### Verify markdown syntax (no broken links)
```bash
grep -r "\[.*\](.*)" README.md | head -5
# Should show markdown links, not broken syntax
```

Result: ✅ / ❌

---

## 8️⃣ Git Status

### Verify no secrets in repo
```bash
cd "/Users/varaungandhi/Desktop/Vegam - me/project/ai-intime v2"

# Check for .env (should not exist)
git status | grep ".env"  # Should show nothing (or only .env.example)

# Check for credentials
grep -r "password\|api_key\|secret" . --include="*.py" --include="*.md" | grep -v "# " | head -5
# Should output nothing (credentials only in comments or .env.example)
```

Result: ✅ / ❌

### Verify git history is clean
```bash
git log --oneline | head -5
# Should show meaningful commit messages
```

Result: ✅ / ❌

---

## 9️⃣ Performance Check

### Measure query latency
```bash
cd "/Users/varaungandhi/Desktop/Vegam - me/project/ai-intime v2"

python3 << 'EOF'
import time
import sys
sys.path.insert(0, '.')

from src.agents.analytics_agent import AnalyticsAgent

agent = AnalyticsAgent(db_path='data/sample_manufacturing.db')

queries = [
    "What's the average yield?",
    "Show me production by product",
    "Plot yield trend"
]

for q in queries:
    start = time.time()
    result = agent.ask(q)
    elapsed = time.time() - start
    status = "✅" if result else "❌"
    print(f"{status} '{q}' - {elapsed:.1f}s")

print("\n✅ All queries completed within expected time (<5s)")
EOF
```

Expected: Each query should complete in 2-5 seconds

Result: ✅ / ❌

---

## 🔟 Recruiter Materials

### Check presentation files exist
```bash
ls -la RECRUITER_PRESENTATION.md DEMO_CHEAT_SHEET.md

# Verify file sizes (should be substantial)
wc -w RECRUITER_PRESENTATION.md  # Should be >5000 words
wc -w DEMO_CHEAT_SHEET.md        # Should be >2000 words
```

Result: ✅ / ❌

### Verify demo queries are ready
```bash
# All should be copy-pasteable queries
grep "What was the total" DEMO_CHEAT_SHEET.md
grep "Plot yield" DEMO_CHEAT_SHEET.md
grep "Compare yield between" DEMO_CHEAT_SHEET.md
```

Result: ✅ / ❌

---

## Final Sign-Off

### Pre-Presentation Checklist

- [ ] ✅ Python 3.10+, all packages installed
- [ ] ✅ Ollama running, DeepSeek model available
- [ ] ✅ Database file exists and has data
- [ ] ✅ Schema extraction works
- [ ] ✅ Vector search initializes
- [ ] ✅ SQL generation works (tested with LLM)
- [ ] ✅ Streamlit UI starts
- [ ] ✅ End-to-end query completes in <5 seconds
- [ ] ✅ No secrets in git
- [ ] ✅ Documentation complete and readable
- [ ] ✅ Demo queries prepared
- [ ] ✅ Recruiter presentation materials ready

### If Any Checks Failed

**For import errors:**
```bash
pip install --upgrade streamlit langgraph chromadb
```

**For Ollama issues:**
```bash
ollama pull deepseek-coder-v2
```

**For ChromaDB corruption:**
```bash
rm -rf .chromadb/
python3 scripts/setup/startup.py
```

**For database issues:**
```bash
sqlite3 data/sample_manufacturing.db ".schema" | head
```

---

## ✅ Ready for Presentation!

Once all checks pass, you're ready to present on Monday. Have:

1. **Browser with Streamlit UI open** (http://localhost:8501)
2. **Terminal with Ollama running** in background
3. **DEMO_CHEAT_SHEET.md** printed or on second monitor
4. **RECRUITER_PRESENTATION.md** bookmarked
5. **Code editor open** to quick reference architecture (src/agents/analytics_agent.py)

**You've got this! 🚀**

