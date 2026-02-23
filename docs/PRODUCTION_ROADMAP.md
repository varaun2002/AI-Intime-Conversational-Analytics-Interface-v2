# AI Intime V2 - Production Roadmap

## Overview
Transform the current prototype into a production-grade analytics system capable of handling 40-50 tables with 50-100 columns, featuring full transparency, dynamic context engineering, and Milvus-based semantic search.

---

## 1. Milvus Integration (Production-Ready)

### Current Status
- Basic implementation exists but disabled due to initialization hang
- Using keyword-based fallback

### Production Requirements
✅ **Async initialization** - Load embeddings in background  
✅ **Connection pooling** - Reuse Milvus connections  
✅ **Error recovery** - Graceful fallback if Milvus unavailable  
✅ **Health checks** - Monitor Milvus connection status  
✅ **Caching** - Cache embeddings to avoid regeneration  

### Implementation Tasks
- [ ] Async model loading with progress callbacks
- [ ] Milvus connection pool with retry logic
- [ ] Local embedding cache (disk-based)
- [ ] Hybrid search: embeddings + keyword fallback
- [ ] Monitoring dashboard for Milvus health

---

## 2. Transparency & Explainability

### Goal
Every report should explain in simple English:
- Which tables were selected and why
- What SQL was generated and why
- Which columns were used
- How KPIs were calculated
- What transformations were applied

### Components

#### A. Query Analysis Layer
```python
class QueryAnalyzer:
    """Analyzes user query and explains reasoning"""
    
    def analyze(self, query: str) -> dict:
        return {
            "intent": "AGGREGATION",
            "reasoning": "User asked 'how many' which indicates counting",
            "key_entities": ["orders", "completed"],
            "expected_tables": ["production_orders", "shift_logs"],
            "confidence": 0.92
        }
```

#### B. Schema Selection Explainer
```python
class SchemaExplainer:
    """Explains why specific tables were chosen"""
    
    def explain_selection(self, query: str, tables: list, scores: dict) -> str:
        return """
        I selected these tables:
        1. production_orders (score: 0.94) - Contains order completion data
        2. shift_logs (score: 0.81) - Provides time context for orders
        3. Rejected: products (score: 0.42) - Not needed for counting orders
        """
```

#### C. SQL Generation Explainer
```python
class SQLExplainer:
    """Explains the generated SQL query"""
    
    def explain_sql(self, sql: str, intent: str) -> str:
        return """
        The SQL query:
        - SELECTS: Count of distinct order_id (to count orders)
        - FROM: production_orders (main table with order data)
        - WHERE: status = 'completed' (filter for completed only)
        - No JOIN needed: All data in single table
        """
```

#### D. KPI Calculation Explainer
```python
class KPIExplainer:
    """Explains how each KPI was calculated"""
    
    def explain_kpi(self, kpi_name: str, calculation: dict) -> str:
        return """
        avg_yield (91.4%):
        - Formula: (quantity_actual / quantity_planned) * 100
        - Calculated for: 117 orders
        - Min: 85.2%, Max: 97.8%
        - Why: Shows production efficiency
        """
```

### Implementation Tasks
- [ ] Create QueryAnalyzer class
- [ ] Add SchemaExplainer to retrieval layer
- [ ] Build SQLExplainer with AST parsing
- [ ] Enhance KPIExplainer with formula tracking
- [ ] Add Explanation section to UI report
- [ ] Store explanations in report metadata

---

## 3. Dynamic Context Engineering

### Goal
Intelligently determine:
- How much data is needed for each query type
- Which columns are relevant
- Which time ranges to query
- When to use sampling vs full data

### Query Type → Data Requirements Matrix

| Query Type | Tables Needed | Columns Needed | Row Limit | Time Range |
|------------|--------------|----------------|-----------|------------|
| LOOKUP | 1-2 | 5-10 | 1-10 | Specific |
| AGGREGATION | 2-3 | 10-20 | All | Last 30 days |
| COMPARISON | 2-4 | 15-25 | All | Last 90 days |
| TREND | 3-5 | 20-30 | All | Last 6-12 months |
| REPORT | 4-6 | 30-50 | All | Custom range |

### Context Selection Strategy

#### A. Column Relevance Scoring
```python
class ColumnSelector:
    """Determines which columns are needed"""
    
    def select_columns(self, query: str, tables: list, intent: str) -> dict:
        # Score columns based on:
        # 1. Query keywords match (name, yield → quantity_actual, quantity_planned)
        # 2. Intent requirements (TREND → date columns)
        # 3. Relationship columns (FK columns for JOINs)
        # 4. Metadata columns (always include PK, timestamps)
        
        return {
            "production_orders": [
                "order_id",  # PK (always)
                "quantity_planned",  # Needed for yield
                "quantity_actual",  # Needed for yield
                "start_time",  # Needed for time filtering
                "status"  # Needed for filtering
            ],
            "excluded": ["unit", "end_time"]  # Not needed for this query
        }
```

#### B. Row Sampling Strategy
```python
class DataSampler:
    """Intelligent data sampling for large tables"""
    
    def should_sample(self, table: str, row_count: int, intent: str) -> dict:
        if row_count < 1000:
            return {"sample": False, "reason": "Small table"}
        
        if intent == "TREND":
            return {
                "sample": True,
                "strategy": "time_based",
                "sample_rate": 0.1,  # 10% of data
                "reason": "Large dataset, trend patterns visible in sample"
            }
        
        return {"sample": False}
```

#### C. Time Window Determination
```python
class TimeWindowSelector:
    """Determines relevant time range"""
    
    def select_window(self, query: str, intent: str) -> dict:
        # Parse time references from query
        if "last week" in query:
            return {"start": "7 days ago", "end": "now"}
        
        if "this month" in query:
            return {"start": "start of month", "end": "now"}
        
        # Default by intent
        defaults = {
            "LOOKUP": {"start": None, "end": None},  # No filter
            "AGGREGATION": {"start": "30 days ago", "end": "now"},
            "COMPARISON": {"start": "90 days ago", "end": "now"},
            "TREND": {"start": "6 months ago", "end": "now"},
        }
        
        return defaults.get(intent, {"start": "30 days ago", "end": "now"})
```

### Implementation Tasks
- [ ] Build ColumnSelector with relevance scoring
- [ ] Implement DataSampler with sampling strategies
- [ ] Create TimeWindowSelector with NLP parsing
- [ ] Add context optimization to SQL generator
- [ ] Track context decisions for transparency
- [ ] Add context summary to reports

---

## 4. Scale Optimization (40-50 Tables)

### Challenges
- Schema search across 50 tables
- JOIN optimization for multi-table queries
- Query performance with large datasets
- Memory management for embeddings

### Solutions

#### A. Hierarchical Schema Organization
```python
class SchemaHierarchy:
    """Organize tables into logical groups"""
    
    def __init__(self, schema: dict):
        self.groups = {
            "core": ["production_orders", "shift_logs"],
            "master_data": ["products", "line_master", "recipes", "staff"],
            "detailed": ["production_steps", "quality_checks"],
            "analytics": ["aggregated_metrics", "historical_kpis"]
        }
    
    def filter_by_relevance(self, query: str) -> list:
        # First: Search within most relevant group
        # Second: Expand to related groups if needed
        pass
```

#### B. Multi-Stage Schema Search
```python
class MultiStageSearch:
    """Two-stage search for better performance"""
    
    def search(self, query: str, top_k: int = 5) -> list:
        # Stage 1: Fast keyword filter (eliminate 80% of tables)
        candidates = self.keyword_filter(query, top_k=15)
        
        # Stage 2: Semantic ranking on candidates only
        results = self.semantic_rank(query, candidates, top_k=top_k)
        
        return results
```

#### C. Smart JOIN Detection
```python
class JoinOptimizer:
    """Optimize multi-table queries"""
    
    def detect_joins(self, tables: list) -> dict:
        # Analyze FK relationships
        # Suggest optimal JOIN order
        # Detect unnecessary JOINs
        # Recommend covering indexes
        
        return {
            "joins": [
                {
                    "left": "production_orders",
                    "right": "shift_logs",
                    "condition": "production_orders.shift_id = shift_logs.shift_id",
                    "type": "INNER",
                    "cardinality": "many-to-one"
                }
            ],
            "order": ["shift_logs", "production_orders"],  # Optimal order
            "indexes_needed": ["shift_logs.shift_id"]
        }
```

### Implementation Tasks
- [ ] Create SchemaHierarchy classifier
- [ ] Implement multi-stage search
- [ ] Build automatic JOIN optimizer
- [ ] Add query plan analysis
- [ ] Implement connection pooling for SQLAlchemy
- [ ] Add query result caching

---

## 5. Enhanced Report Generation

### New Report Structure

```python
{
    # Existing fields
    "query": "...",
    "intent": "...",
    "summary": "...",
    "kpis": {...},
    "chart": plotly_figure,
    "data": dataframe,
    
    # NEW: Transparency fields
    "explanation": {
        "query_analysis": "User asked 'how many orders completed' which is a counting question...",
        
        "schema_selection": {
            "selected": ["production_orders", "shift_logs"],
            "reasoning": {
                "production_orders": "Contains order completion status (score: 0.94)",
                "shift_logs": "Provides time context for filtering (score: 0.81)"
            },
            "rejected": {
                "products": "Not needed for counting (score: 0.42)"
            }
        },
        
        "sql_explanation": {
            "operation": "COUNT with WHERE filter",
            "tables_used": ["production_orders"],
            "key_columns": ["order_id", "status"],
            "filters": "status = 'completed'",
            "why": "Counting distinct orders that meet completion criteria"
        },
        
        "kpi_calculations": {
            "total_orders": {
                "formula": "COUNT(DISTINCT order_id)",
                "input_rows": 117,
                "result": 117,
                "confidence": "high"
            }
        },
        
        "context_decisions": {
            "columns_used": 5,
            "columns_available": 12,
            "why_excluded": "unit, end_time not needed for counting",
            "time_range": "Last 30 days (default for aggregation)",
            "sampling": "No sampling (small dataset)"
        }
    },
    
    # Metadata
    "performance": {
        "schema_search_ms": 12,
        "sql_generation_ms": 145,
        "execution_ms": 23,
        "kpi_calculation_ms": 8,
        "total_ms": 188
    }
}
```

### UI Enhancement - Explanation Panel

```
📋 Summary
[Existing summary content]

🔍 How This Report Was Generated (click to expand)
├─ 1️⃣ Query Analysis
│   └─ Detected intent: AGGREGATION (confidence: 92%)
│   └─ Key entities: orders, completed
│
├─ 2️⃣ Data Selection
│   └─ Selected tables: production_orders (94% match), shift_logs (81% match)
│   └─ Used columns: order_id, status, shift_date
│   └─ Time range: Last 30 days
│
├─ 3️⃣ SQL Generation
│   └─ Operation: COUNT with status filter
│   └─ No JOINs needed (all data in production_orders)
│
└─ 4️⃣ Results
    └─ Found 117 completed orders
    └─ Calculated 8 KPIs from this data
    └─ Query executed in 188ms
```

### Implementation Tasks
- [ ] Add explanation field to AgentState
- [ ] Collect explanations at each workflow step
- [ ] Build ExplanationPanel UI component
- [ ] Add performance tracking
- [ ] Store explanations in session for debugging

---

## 6. Production Infrastructure

### A. Environment Configuration
```env
# Production settings
ENVIRONMENT=production

# Milvus (Production cluster)
MILVUS_HOST=milvus-prod.company.com
MILVUS_PORT=19530
MILVUS_USER=analytics_app
MILVUS_PASSWORD=***
USE_MILVUS=true

# Database (Production)
DATABASE_URL=postgresql://user:pass@prod-db.company.com:5432/manufacturing
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# LLM (Production model)
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=***
ANTHROPIC_MODEL=claude-opus-4
LLM_TIMEOUT=30
LLM_MAX_RETRIES=3

# Redis (for caching)
REDIS_URL=redis://prod-redis.company.com:6379
CACHE_TTL=3600

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=true
LOG_PATH=/var/log/ai-intime/

# Performance
MAX_CONCURRENT_QUERIES=10
QUERY_TIMEOUT=60
ENABLE_QUERY_CACHE=true
```

### B. Monitoring & Observability
- [ ] Add Prometheus metrics export
- [ ] Implement structured logging (JSON)
- [ ] Add OpenTelemetry tracing
- [ ] Create Grafana dashboards
- [ ] Set up alerts for failures

### C. Testing Strategy
```
tests/
├── unit/
│   ├── test_query_analyzer.py
│   ├── test_schema_explainer.py
│   ├── test_context_selector.py
│   └── test_milvus_store.py
├── integration/
│   ├── test_full_pipeline.py
│   ├── test_large_schema.py (40-50 tables)
│   └── test_milvus_connection.py
└── performance/
    ├── test_query_latency.py
    ├── test_concurrent_users.py
    └── test_large_dataset.py
```

---

## Implementation Timeline

### Phase 1: Core Transparency (Week 1-2)
- [x] Plan architecture
- [ ] Implement QueryAnalyzer
- [ ] Add SchemaExplainer
- [ ] Build SQLExplainer
- [ ] Create KPIExplainer
- [ ] Update UI with explanation panel

### Phase 2: Dynamic Context (Week 3-4)
- [ ] Build ColumnSelector
- [ ] Implement TimeWindowSelector
- [ ] Add DataSampler
- [ ] Integrate context decisions into pipeline
- [ ] Add context explanations to reports

### Phase 3: Production Milvus (Week 5-6)
- [ ] Fix async initialization
- [ ] Add connection pooling
- [ ] Implement embedding cache
- [ ] Add health monitoring
- [ ] Test with 50-table schema

### Phase 4: Scale Optimization (Week 7-8)
- [ ] Implement schema hierarchy
- [ ] Build multi-stage search
- [ ] Add JOIN optimizer
- [ ] Performance testing
- [ ] Query result caching

### Phase 5: Production Hardening (Week 9-10)
- [ ] Comprehensive testing
- [ ] Documentation updates
- [ ] Deployment automation
- [ ] Monitoring setup
- [ ] Performance tuning

---

## Success Metrics

### Performance Targets
- **Query latency**: < 2s for 95th percentile
- **Schema search**: < 50ms for 50 tables
- **Concurrent users**: Support 20+ simultaneous queries
- **Uptime**: 99.9% availability

### Quality Targets
- **SQL accuracy**: > 95% valid queries
- **Explanation clarity**: User satisfaction > 4.5/5
- **Context relevance**: > 90% appropriate column selection

---

## Next Steps

1. **Review & Approve** this roadmap
2. **Start Phase 1**: Implement transparency layer
3. **Test incrementally** with existing 7-table database
4. **Scale gradually** to 40-50 table test database
5. **Deploy to production** with monitoring

---

**Author:** GitHub Copilot  
**Date:** February 19, 2026  
**Version:** 2.0 Production Roadmap
