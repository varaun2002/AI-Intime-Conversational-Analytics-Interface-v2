"""
Query Analysis and Explanation Module
Provides transparency into how queries are interpreted and processed.
"""
import re
from typing import Dict, List, Tuple


class QueryAnalyzer:
    """
    Analyzes user queries to understand intent and extract key entities.
    Provides reasoning for classification decisions.
    """
    
    INTENT_PATTERNS = {
        "LOOKUP": [
            r'\b(show|display|get|find|what is|details? for|info about)\b.*\b(order|po-\d+|id|specific)\b',
            r'\b(po-\d+|#\d+|id\s+\d+)\b',
        ],
        "AGGREGATION": [
            r'\b(how many|count|total|sum|average|avg|mean)\b',
            r'\b(what.*total|what.*average)\b',
        ],
        "COMPARISON": [
            r'\b(compare|versus|vs|difference|better|worse|higher|lower)\b',
            r'\b(day.*night|shift.*shift|line.*line)\b',
        ],
        "TREND": [
            r'\b(trend|over time|plot|graph|chart|timeline|history)\b',
            r'\b(last \d+ (days?|weeks?|months?))\b',
            r'\b(daily|weekly|monthly)\b',
        ],
        "REPORT": [
            r'\b(report|summary|overview|full|complete|breakdown)\b',
            r'\b(what happened|performance|status)\b',
        ],
    }
    
    ENTITY_PATTERNS = {
        "table_names": r'\b(?:orders?|shifts?|lines?|products?|staff|supervisors?|steps?)\b',
        "metrics": r'\b(?:yield|efficiency|performance|output|quality|duration|cycle time)\b',
        "time_refs": r'\b(?:today|yesterday|last (?:week|month|year)|this (?:week|month)|\d+ days? ago)\b',
        "comparisons": r'\b(?:day|night|morning|evening) (?:shift|time)\b',
        "ids": r'\b(?:po-\d+|line-\d+|emp-\d+|step-\d+)\b',
    }
    
    def analyze(self, query: str, actual_intent: str = None) -> Dict:
        """
        Analyze query and return structured analysis with reasoning.
        
        Args:
            query: The user's question
            actual_intent: (Optional) The actual intent determined by LLM. If provided,
                          explanation will note what the LLM decided vs what patterns suggest.
        
        Returns:
            {
                "intent": str,
                "confidence": float,
                "reasoning": str,
                "key_entities": Dict[str, List[str]],
                "expected_tables": List[str],
                "query_type": str,
                "llm_intent": str (if actual_intent provided),
                "llm_alignment": bool,
            }
        """
        query_lower = query.lower()
        
        # Detect intent based on patterns
        intent, confidence, reasoning = self._detect_intent(query_lower)
        
        # Extract entities
        entities = self._extract_entities(query_lower)
        
        # Predict tables
        tables = self._predict_tables(query_lower, entities)
        
        analysis = {
            "intent": intent,
            "confidence": confidence,
            "reasoning": reasoning,
            "key_entities": entities,
            "expected_tables": tables,
            "query_type": self._classify_query_type(query_lower),
            "complexity": self._estimate_complexity(tables, entities),
        }
        
        # If actual intent provided, add alignment info
        if actual_intent:
            analysis["llm_intent"] = actual_intent
            analysis["llm_alignment"] = (actual_intent.upper() == intent.upper())
            if not analysis["llm_alignment"]:
                analysis["alignment_note"] = f"LLM determined {actual_intent}, pattern-based suggestion was {intent}"
        
        return analysis
    
    def _detect_intent(self, query: str) -> Tuple[str, float, str]:
        """Detect intent with confidence and reasoning."""
        matches = {}
        
        for intent, patterns in self.INTENT_PATTERNS.items():
            score = 0
            matched_patterns = []
            
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    score += 1
                    matched_patterns.append(pattern)
            
            if score > 0:
                matches[intent] = {
                    "score": score,
                    "patterns": matched_patterns
                }
        
        if not matches:
            return "AGGREGATION", 0.5, "No specific intent detected, defaulting to aggregation"
        
        # Get best match
        best_intent = max(matches.keys(), key=lambda k: matches[k]["score"])
        confidence = min(0.95, 0.5 + (matches[best_intent]["score"] * 0.15))
        
        # Build reasoning
        reasoning = self._build_intent_reasoning(query, best_intent, matches[best_intent])
        
        return best_intent, confidence, reasoning
    
    def _build_intent_reasoning(self, query: str, intent: str, match_info: Dict) -> str:
        """Generate human-readable reasoning for intent classification."""
        reasons = {
            "LOOKUP": "contains specific identifier or request for details",
            "AGGREGATION": "asks for summary statistics (count, total, average)",
            "COMPARISON": "compares multiple groups or categories",
            "TREND": "requests time-series analysis or historical data",
            "REPORT": "requests comprehensive overview or analysis",
        }
        
        base_reason = reasons.get(intent, "matches this pattern")
        
        # Extract key words that triggered the match
        keywords = []
        for pattern in match_info["patterns"]:
            # Simple extraction from pattern
            words = re.findall(r'\w+', pattern)
            keywords.extend([w for w in words if len(w) > 3 and w not in ['show', 'what', 'this']])
        
        if keywords:
            keyword_str = ", ".join(list(set(keywords))[:3])
            return f"Query {base_reason}. Detected keywords: {keyword_str}"
        
        return f"Query {base_reason}"
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract key entities from query."""
        entities = {}
        
        for entity_type, pattern in self.ENTITY_PATTERNS.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                # Convert all matches to strings (handle any type)
                str_matches = []
                for m in matches:
                    try:
                        if isinstance(m, str):
                            str_matches.append(m)
                        elif isinstance(m, tuple):
                            # Join tuple elements or take first non-empty
                            non_empty = [s for s in m if s]
                            if non_empty:
                                str_matches.append(non_empty[0])
                        else:
                            str_matches.append(str(m))
                    except Exception:
                        # Fallback: just convert to string
                        str_matches.append(str(m))
                # Remove duplicates and empty strings
                entities[entity_type] = list(set(s for s in str_matches if s))
        
        return entities
    
    def _predict_tables(self, query: str, entities: Dict) -> List[str]:
        """Predict which tables are likely needed."""
        table_keywords = {
            "production_orders": ["order", "po", "planned", "actual", "quantity", "recipe"],
            "shift_logs": ["shift", "supervisor", "day", "night", "date"],
            "production_steps": ["step", "stage", "operator", "temperature", "pressure"],
            "products": ["product", "chemx", "polymer", "coating", "adhesive"],
            "line_master": ["line", "capacity", "building", "location"],
            "staff": ["staff", "supervisor", "operator", "employee", "emp"],
            "recipes": ["recipe", "cycle time", "version", "process"],
        }
        
        predictions = []
        for table, keywords in table_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    predictions.append(table)
                    break
        
        # If no predictions, default to core tables
        if not predictions:
            predictions = ["production_orders", "shift_logs"]
        
        return list(set(predictions))
    
    def _classify_query_type(self, query: str) -> str:
        """Classify the type of question being asked."""
        if re.search(r'\b(how many|count)\b', query):
            return "counting"
        elif re.search(r'\b(what|which|show)\b', query):
            return "retrieval"
        elif re.search(r'\b(why|explain)\b', query):
            return "analytical"
        elif re.search(r'\b(when|date|time)\b', query):
            return "temporal"
        else:
            return "informational"
    
    def _estimate_complexity(self, tables: List[str], entities: Dict) -> str:
        """Estimate query complexity."""
        if len(tables) == 1 and len(entities) < 2:
            return "simple"
        elif len(tables) <= 2 and len(entities) < 4:
            return "moderate"
        else:
            return "complex"
    
    def explain_analysis(self, analysis: Dict) -> str:
        """Generate human-readable explanation of the analysis."""
        lines = [
            f"📊 Query Analysis:",
            f"",
            f"Intent: {analysis['intent']} (confidence: {analysis['confidence']:.0%})",
            f"Reasoning: {analysis['reasoning']}",
            f"",
            f"Key Information Detected:",
        ]
        
        if analysis['key_entities']:
            for entity_type, values in analysis['key_entities'].items():
                lines.append(f"  • {entity_type.replace('_', ' ').title()}: {', '.join(values[:3])}")
        else:
            lines.append("  • No specific entities detected")
        
        lines.extend([
            f"",
            f"Expected Tables: {', '.join(analysis['expected_tables'])}",
            f"Query Complexity: {analysis['complexity']}",
        ])
        
        return "\n".join(lines)
