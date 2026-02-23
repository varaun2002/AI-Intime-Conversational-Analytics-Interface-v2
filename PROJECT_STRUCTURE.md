# 📁 Project Structure - AI InTime v2

## Overview
This document describes the organized folder structure of the AI InTime project after cleanup.

```
ai-intime v2/
├── 📋 Root Configuration Files
│   ├── README.md                  # Main project README
│   ├── requirements.txt           # Python dependencies
│   ├── .env                       # Environment variables (local)
│   ├── .env.example              # Environment template
│   └── .gitignore                # Git ignore rules
│
├── 📚 docs/                       # All documentation
│   ├── README_INDEX.md                    # Documentation index & navigation
│   ├── TEST_QUICK_START.md               # 3-step testing quick start
│   ├── COMPREHENSIVE_TEST_SUITE.md       # Detailed test descriptions
│   ├── TESTING_STRATEGY.md               # Strategic testing approach
│   ├── DELIVERY_SUMMARY.md               # Complete framework overview
│   ├── SETUP.md                          # Database setup guide
│   ├── PHASE1_SUMMARY.md                 # Phase 1 completion summary
│   ├── PHASE1_TRANSPARENCY.md            # Phase 1 transparency layer
│   ├── PHASE1_QUICKSTART.md              # Phase 1 quick start
│   ├── PHASE1_COMPLETE.md                # Phase 1 completion details
│   ├── PHASE1_IMPLEMENTATION_CHECKLIST.md # Phase 1 checklist
│   ├── PHASE1_FILE_TREE.md               # Phase 1 file organization
│   ├── PRODUCTION_ROADMAP.md             # Long-term vision & roadmap
│   ├── MIGRATION_GUIDE.md                # Migration guidelines
│   └── FIX_BUILDING_YIELD_QUERY.md       # Specific yield query fix
│
├── 🔧 scripts/                    # All executable scripts
│   ├── setup/                     # Database setup scripts
│   │   ├── setup_database.py               # Single database generator
│   │   └── startup.py                     # One-command app launcher
│   ├── testing/                   # Comprehensive testing suite
│   │   ├── generate_comprehensive_erp.py   # 28-table ERP generator
│   │   ├── test_edge_cases.py             # 10 edge case tests
│   │   ├── run_all_tests.py               # Master test orchestrator
│   │   ├── test_quick.py                  # Quick validation tests
│   │   ├── test_explainability.py         # Explainability tests
│   │   └── test_milvus_integration.py     # Milvus integration tests
│   └── utilities/                 # Utility scripts
│       └── verify_setup.py                 # Setup verification
│
├── 📦 src/                        # Source code (existing structure)
│   ├── __init__.py
│   ├── agents/                    # Analytics agents
│   ├── calculations/              # KPI calculations
│   ├── llm/                       # LLM provider integration
│   ├── mcp/                       # Model context protocol
│   ├── report/                    # Report generation
│   ├── retrieval/                 # Schema retrieval & storage
│   ├── schema/                    # Schema extraction
│   ├── sql/                       # SQL generation & validation
│   └── utils/                     # Utility functions
│
├── 🎨 ui/                         # User interface (existing)
│   └── app.py                     # Streamlit application
│
├── 📊 data/                       # Data files (existing)
│   ├── sample_manufacturing.db    # Sample database
│   ├── manufacturing_erp.db       # Comprehensive ERP database
│   └── DATABASE_SCHEMA.md         # Schema documentation
│
└── 🧪 tests/                      # Traditional test suite (existing)
    └── test_all_queries.py        # Query validation tests
```

## Folder Organization Details

### 📚 `/docs` - All Documentation
**Purpose:** Centralized documentation for the entire project

| File | Purpose |
|------|---------|
| `README_INDEX.md` | **START HERE** - Navigation guide for all docs |
| `TEST_QUICK_START.md` | 3-step guide + copy-paste test questions |
| `COMPREHENSIVE_TEST_SUITE.md` | 10 tests with SQL patterns & challenges |
| `TESTING_STRATEGY.md` | Strategic approach & integration path |
| `DELIVERY_SUMMARY.md` | Complete framework overview |
| `SETUP.md` | Database initialization steps |
| `PHASE1_*` | Phase 1 documentation (6 files) |
| `PRODUCTION_ROADMAP.md` | Long-term vision & next phases |
| `MIGRATION_GUIDE.md` | Migration & deployment guidelines |
| `FIX_BUILDING_YIELD_QUERY.md` | Specific yield comparison fix |

**How to navigate:**
- New to project? Start with `README_INDEX.md`
- Want to test now? Go to `TEST_QUICK_START.md`
- Need details? Check `COMPREHENSIVE_TEST_SUITE.md`
- Planning integration? Read `TESTING_STRATEGY.md`

### 🔧 `/scripts` - Executable Scripts

#### `/scripts/setup/` 
Database initialization & application startup
- `setup_database.py` - Creates single 7-table database
- `startup.py` - One-command launcher for app + database

#### `/scripts/testing/`
Comprehensive edge case testing suite
- `generate_comprehensive_erp.py` - Creates 28-table ERP with 5,000+ records
- `test_edge_cases.py` - Runs 10 SQL edge case tests
- `run_all_tests.py` - Orchestrates database generation + all tests
- `test_quick.py` - Quick validation tests
- `test_explainability.py` - Tests explainability layer
- `test_milvus_integration.py` - Tests Milvus vector store

#### `/scripts/utilities/`
Utility & verification scripts
- `verify_setup.py` - Validates database schema & setup

### 📦 `/src` - Source Code (Unchanged)
The main application code organized by feature:
- `agents/` - Analytics agents for question answering
- `calculations/` - KPI and metric calculations
- `llm/` - LLM provider management
- `mcp/` - Model context protocol handlers
- `report/` - Report generation & assembly
- `retrieval/` - Schema storage & retrieval
- `schema/` - Database schema extraction
- `sql/` - SQL generation, validation, execution
- `utils/` - Shared utility functions

### 🎨 `/ui` - User Interface (Unchanged)
- `app.py` - Streamlit web application

### 📊 `/data` - Data Files (Unchanged)
- `sample_manufacturing.db` - Basic 7-table test database
- `manufacturing_erp.db` - Comprehensive 28-table test database
- `DATABASE_SCHEMA.md` - Schema documentation

### 🧪 `/tests` - Test Suite (Unchanged)
- `test_all_queries.py` - Comprehensive query validation

## File Statistics

### Documentation
- **Total lines:** 1,150+
- **Files:** 15
- **Focus:** Clear guidance for usage, testing, and integration

### Code & Scripts
- **Total lines:** 1,500+
- **Setup scripts:** 2 files
- **Testing scripts:** 6 files
- **Utilities:** 1 file

### Coverage
- **Main source:** 4,000+ lines in `/src`
- **Test coverage:** 10 edge cases + traditional tests
- **Database:** 28 tables with 5,000+ records

## Quick Navigation

### I Want To...

**🚀 Get Started Testing**
```
1. Read: docs/TEST_QUICK_START.md
2. Run: python3 scripts/testing/generate_comprehensive_erp.py
3. Run: python3 scripts/testing/test_edge_cases.py
```

**📚 Understand the Framework**
```
Read in order:
1. docs/README_INDEX.md (navigation guide)
2. docs/DELIVERY_SUMMARY.md (overview)
3. docs/COMPREHENSIVE_TEST_SUITE.md (details)
4. docs/TESTING_STRATEGY.md (integration)
```

**🛠️ Set Up Database**
```
Option 1 (quick): python3 scripts/setup/setup_database.py
Option 2 (comprehensive): python3 scripts/testing/generate_comprehensive_erp.py
Both produce SQLite database in data/
```

**🎨 Run the Application**
```
python3 scripts/setup/startup.py
# Or manually:
python3 scripts/setup/setup_database.py
streamlit run ui/app.py
```

**✅ Validate Setup**
```
python3 scripts/utilities/verify_setup.py
```

## Key Commands

| Command | Purpose |
|---------|---------|
| `python3 scripts/setup/startup.py` | Full application startup |
| `python3 scripts/testing/generate_comprehensive_erp.py` | Create 28-table database |
| `python3 scripts/testing/test_edge_cases.py` | Run 10 edge case tests |
| `python3 scripts/testing/run_all_tests.py` | Full test suite |
| `python3 scripts/utilities/verify_setup.py` | Verify setup |
| `streamlit run ui/app.py` | Run web UI |

## Before & After

### Before Organization ❌
```
Root directory (very messy):
├── 15 markdown files (docs scattered everywhere)
├── 9 Python scripts (no clear organization)
├── Mixed setup and test files
└── Hard to find what you need
```

### After Organization ✅
```
Clean structure:
├── docs/ (all 15 documentation files)
├── scripts/
│   ├── setup/ (2 setup files)
│   ├── testing/ (6 testing files)
│   └── utilities/ (1 utility file)
└── src/, ui/, data/, tests/ (organized as-is)
```

## Migration Notes

- **All files moved:** 24 files organized into appropriate folders
- **No code changes:** Only organizational restructuring
- **All imports work:** Relative imports preserved
- **Database unaffected:** Data folder structure unchanged
- **Tests unchanged:** All tests work from new locations

## Documentation Reading Order

**For First-Time Users:**
1. This file (`PROJECT_STRUCTURE.md`)
2. `docs/README_INDEX.md`
3. `docs/TEST_QUICK_START.md`

**For Integration:**
1. `docs/TESTING_STRATEGY.md`
2. `docs/COMPREHENSIVE_TEST_SUITE.md`
3. `docs/PRODUCTION_ROADMAP.md`

**For Deep Dive:**
1. Phase 1 docs: `docs/PHASE1_SUMMARY.md`
2. Architecture: `docs/PHASE1_TRANSPARENCY.md`
3. Roadmap: `docs/PRODUCTION_ROADMAP.md`

## Questions?

- **Where do I start?** → `docs/README_INDEX.md`
- **How do I test?** → `docs/TEST_QUICK_START.md`
- **What's inside?** → `docs/COMPREHENSIVE_TEST_SUITE.md`
- **How do I integrate?** → `docs/TESTING_STRATEGY.md`
- **What's the vision?** → `docs/PRODUCTION_ROADMAP.md`

---

**Total Project Size:**
- 📄 Documentation: 1,150+ lines (15 files)
- 💻 Code: 1,500+ lines in scripts
- 📦 Source: 4,000+ lines in src/
- 📊 Test coverage: 10 edge cases + comprehensive data

**Status:** ✅ Organized & Ready for Use
