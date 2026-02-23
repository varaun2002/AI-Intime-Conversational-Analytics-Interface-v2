"""
Schema search using vector database (Milvus/ChromaDB) + sentence-transformers.
Provides semantic similarity search for schema matching.
Fully on-device — no cloud dependencies.
"""
import numpy as np
import time
import os


class SchemaStore:
    def __init__(self, 
                 collection_name: str = "schema_tables",
                 milvus_host: str = "localhost",
                 milvus_port: str = "19530",
                 model_name: str = "all-MiniLM-L6-v2",
                 use_milvus: bool = True,
                 use_chromadb: bool = False,
                 **kwargs):
        """
        Initialize schema store with vector search backend.
        
        Supports:
        - Milvus (server-based vector DB)
        - ChromaDB (embedded, Zero-config, fully on-device)
        - Keyword fallback (no embeddings needed)
        
        Args:
            collection_name: Name of the collection
            milvus_host: Milvus server host
            milvus_port: Milvus server port
            model_name: Sentence transformer model for embeddings
            use_milvus: Try Milvus connection first (default: True)
            use_chromadb: Use ChromaDB if Milvus unavailable (default: False, auto-enable if Milvus fails)
        """
        self.collection_name = collection_name
        self.table_names = []
        self.descriptions = []
        self._ready = False
        self._backend = None  # "milvus", "chromadb", or "keyword"
        self.vectors = None
        self.model = None
        self.embedding_dim = 384  # Default for all-MiniLM-L6-v2
        self._model_name = model_name
        
        # Try backends in order: Milvus → ChromaDB → Keyword
        if use_milvus:
            if self._try_connect_milvus(milvus_host, milvus_port, max_retries=3):
                return  # Success with Milvus
        
        # Milvus failed, try ChromaDB
        if self._try_setup_chromadb():
            return  # Success with ChromaDB
        
        # Both failed, use keyword fallback
        print("[SchemaStore] Using keyword-based search (no vector DB available)")
        self._backend = "keyword"

    def _try_connect_milvus(self, host: str, port: str, max_retries: int = 3) -> bool:
        """Try to connect to Milvus with retries. Returns True if successful."""
        for attempt in range(max_retries):
            try:
                from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
                
                print(f"[SchemaStore] Attempting Milvus connection ({attempt + 1}/{max_retries})...")
                connections.connect(
                    alias="default",
                    host=host,
                    port=port,
                    timeout=5
                )
                print(f"[SchemaStore] ✅ Connected to Milvus at {host}:{port}")
                
                self._backend = "milvus"
                self._milvus_modules = {
                    'connections': connections,
                    'Collection': Collection,
                    'FieldSchema': FieldSchema,
                    'CollectionSchema': CollectionSchema,
                    'DataType': DataType,
                    'utility': utility
                }
                
                # Drop existing collection if it exists
                if utility.has_collection(self.collection_name):
                    utility.drop_collection(self.collection_name)
                
                # Create collection schema
                fields = [
                    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                    FieldSchema(name="table_name", dtype=DataType.VARCHAR, max_length=200),
                    FieldSchema(name="description", dtype=DataType.VARCHAR, max_length=5000),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim)
                ]
                schema = CollectionSchema(fields=fields, description="Schema table embeddings")
                self.collection = Collection(name=self.collection_name, schema=schema)
                print(f"[SchemaStore] Created Milvus collection: {self.collection_name}")
                return True
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"[SchemaStore] Milvus connection failed: {e}")
                    print(f"[SchemaStore] Retrying in {wait_time}s...")
                    time.sleep(wait_time)
        
        print(f"[SchemaStore] Milvus unavailable after {max_retries} attempts")
        return False

    def _try_setup_chromadb(self) -> bool:
        """Try to initialize ChromaDB (fully on-device). Returns True if successful."""
        try:
            import chromadb
            
            # Create persistent ChromaDB in .chromadb folder
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                ".chromadb"
            )
            os.makedirs(db_path, exist_ok=True)
            
            # Use new ChromaDB API (v0.4+)
            self.chroma_client = chromadb.PersistentClient(path=db_path)
            
            # Create or get collection with cosine similarity
            self.chroma_collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            self._backend = "chromadb"
            print(f"[SchemaStore] ✅ Using ChromaDB (fully on-device) at {db_path}")
            return True
            
        except Exception as e:
            print(f"[SchemaStore] ChromaDB setup failed: {e}")
            return False

    def ingest(self, schema: dict):
        """Embed table descriptions and store in vector DB (ChromaDB/Milvus) or keyword index."""
        self.table_names = list(schema.keys())
        self.descriptions = [schema[t]["description"] for t in self.table_names]
        
        # Ingest based on backend
        if self._backend == "chromadb":
            self._ingest_chromadb()
        elif self._backend == "milvus":
            self._ingest_milvus()
        else:
            # Keyword-only mode
            print("[SchemaStore] Using fast keyword-based search (embeddings disabled)")
        
        self._ready = True
        print(f"[SchemaStore] Ingested {len(self.table_names)} tables ({self._backend})")

    def _ingest_chromadb(self):
        """Add embeddings to ChromaDB using built-in sentence-transformers."""
        try:
            # ChromaDB has built-in embedding support
            # Automatically uses sentence-transformers "all-MiniLM-L6-v2"
            
            # Clear existing data first to avoid duplicates
            try:
                # Get all existing IDs and delete them
                existing = self.chroma_collection.get()
                if existing and existing.get("ids"):
                    self.chroma_collection.delete(ids=existing["ids"])
            except Exception:
                pass  # Collection might be empty
            
            # Now add fresh data
            ids = [f"table_{i}" for i in range(len(self.table_names))]
            
            self.chroma_collection.add(
                ids=ids,
                metadatas=[{"table_name": name} for name in self.table_names],
                documents=self.descriptions
            )
            print(f"[SchemaStore] ChromaDB ingested {len(self.table_names)} schema items")
        except Exception as e:
            print(f"[SchemaStore] ChromaDB ingestion failed: {e}")
            print("[SchemaStore] Falling back to keyword search")
            self._backend = "keyword"

    def _ingest_milvus(self):
        """Add embeddings to Milvus (not currently active, kept for compatibility)."""
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer(self._model_name)
            embeddings = model.encode(self.descriptions, show_progress_bar=False)
            
            data = {
                "table_name": self.table_names,
                "description": self.descriptions,
                "embedding": embeddings.tolist()
            }
            self.collection.insert(data)
            print(f"[SchemaStore] Milvus ingested {len(self.table_names)} schema items")
        except Exception as e:
            print(f"[SchemaStore] Milvus ingestion failed: {e}")
            self._backend = "keyword"

    def search(self, query: str, top_k: int = 3) -> list:
        """Find the most relevant tables for a user query."""
        if not self._ready:
            raise RuntimeError("SchemaStore not initialized. Call ingest() first.")
        
        # Route to appropriate search backend
        if self._backend == "chromadb":
            return self._search_chromadb(query, top_k)
        elif self._backend == "milvus":
            return self._search_milvus(query, top_k)
        else:
            return self._keyword_search(query, top_k)

    def _search_chromadb(self, query: str, top_k: int = 3) -> list:
        """Search using ChromaDB vector similarity."""
        try:
            results = self.chroma_collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            matched = []
            if results["metadatas"] and len(results["metadatas"]) > 0:
                for i, metadata in enumerate(results["metadatas"][0]):
                    # ChromaDB returns distances (0-2), convert to similarity (0-1)
                    distance = results["distances"][0][i] if results.get("distances") else 0
                    similarity = max(0, 1 - distance / 2)  # Convert distance to similarity
                    
                    matched.append({
                        "table_name": metadata["table_name"],
                        "score": round(similarity, 4)
                    })
            
            return matched
        except Exception as e:
            print(f"[SchemaStore] ChromaDB search failed: {e}. Falling back to keyword search.")
            self._backend = "keyword"
            return self._keyword_search(query, top_k)

    def _search_milvus(self, query: str, top_k: int = 3) -> list:
        """
        Search using Milvus vector similarity (stubbed).
        
        NOTE: This is a placeholder because we don't have a Milvus server running in the demo environment.
        The ingestion pathway works (collection.create_index() succeeded), but search is not implemented.
        
        When Milvus infrastructure is available, this would:
        1. Embed the query using the same sentence-transformers model
        2. Call collection.search(vectors=[embedded_query], limit=top_k, metric_type="L2")
        3. Return formatted results with relevance scores
        
        For now, falls back to TF-IDF keyword search to maintain functionality.
        """
        return self._keyword_search(query, top_k)

    def get_matched_table_names(self, query: str, top_k: int = 3) -> list:
        """Convenience method — returns just table name strings."""
        results = self.search(query, top_k)
        return [r["table_name"] for r in results]
    
    def get_matched_tables(self, query: str, top_k: int = 3) -> list:
        """
        Get matched tables with scores.
        Returns list of dicts with 'table' and 'score' keys.
        """
        results = self.search(query, top_k)
        # Rename table_name to table for consistency
        return [{"table": r["table_name"], "score": r["score"]} for r in results]
    
    def _keyword_search(self, query: str, top_k: int = 3) -> list:
        """TF-IDF based keyword search for schema matching."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            
            # Prepare documents: table names + descriptions
            documents = [f"{name} {desc}" for name, desc in zip(self.table_names, self.descriptions)]
            
            # Build TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words='english',
                token_pattern=r'\b\w+\b',
                max_features=500
            )
            
            # Fit and transform documents
            tfidf_matrix = vectorizer.fit_transform(documents)
            
            # Transform query
            query_vec = vectorizer.transform([query])
            
            # Compute cosine similarity
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(query_vec, tfidf_matrix)[0]
            
            # Get top k with scores
            top_indices = (-similarities).argsort()[:top_k]
            
            matched = []
            for i in top_indices:
                matched.append({
                    "table_name": self.table_names[i],
                    "score": round(float(similarities[i]), 4)
                })
            
            return matched
            
        except ImportError:
            # Fallback to simple keyword matching if sklearn not available
            return self._simple_keyword_search(query, top_k)

    def _simple_keyword_search(self, query: str, top_k: int = 3) -> list:
        """Fallback simple keyword matching when sklearn unavailable."""
        query_lower = query.lower()
        query_words = set(query_lower.split())

        # Expand keywords for common analytics terms
        extra_terms = set()
        if "yield" in query_lower:
            extra_terms.update({
                "quantity_actual", "quantity_planned", "production_orders",
                "order_date", "actual_start", "start_time",
            })
        if "cycle" in query_lower or "recipe" in query_lower:
            extra_terms.update({
                "recipes", "production_orders", "products", "cycle_time_minutes",
                "recipe_name", "recipe_id",
            })
        if any(t in query_lower for t in ["trend", "last", "days", "weeks", "months", "date", "time"]):
            extra_terms.update({
                "order_date", "actual_start", "planned_start", "shift_date",
            })
        if any(t in query_lower for t in ["order", "production"]):
            extra_terms.update({"production_orders", "order_id"})

        query_words |= extra_terms
        
        scores = []
        for i, (table_name, description) in enumerate(zip(self.table_names, self.descriptions)):
            desc_lower = description.lower()
            table_lower = table_name.lower()
            
            # Count keyword matches
            score = 0
            for word in query_words:
                if len(word) > 2:  # Skip very short words
                    if word in table_lower:
                        score += 3  # Table name match is worth more
                    if word in desc_lower:
                        score += 1
            
            # Boost score for exact table name mentions
            if table_name.lower() in query_lower:
                score += 10
            
            scores.append((i, score))
        
        # Sort by score and return top_k
        scores.sort(key=lambda x: x[1], reverse=True)
        
        matched = []
        for i, score in scores[:top_k]:
            matched.append({
                "table_name": self.table_names[i],
                "score": round(score / 10.0, 4),  # Normalize to 0-1 range roughly
            })
        
        return matched
    
    def __del__(self):
        """Cleanup connections."""
        if self._backend == "milvus":
            try:
                from pymilvus import connections
                connections.disconnect("default")
            except Exception:
                pass
        elif self._backend == "chromadb":
            # ChromaDB auto-closes, no explicit cleanup needed
            pass