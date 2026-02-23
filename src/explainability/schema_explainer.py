"""
Schema Explanation Module
Explains table selection and schema retrieval decisions.
"""
from typing import Dict, List


class SchemaExplainer:
    """
    Explains why specific tables were selected and how they match the query.
    Provides transparency into schema retrieval decisions.
    """
    
    def __init__(self):
        self.table_descriptions = {
            "production_orders": "Core manufacturing orders with planned vs actual quantities",
            "shift_logs": "Daily shift information with supervisors and line assignments",
            "production_steps": "Detailed step-by-step production data with operators and parameters",
            "products": "Product definitions and specifications",
            "line_master": "Production line capacity and configuration",
            "staff": "Employee information and roles",
            "recipes": "Manufacturing recipes with cycle times and versions",
        }
    
    def explain_selection(
        self,
        query: str,
        selected_tables: List[str],
        scores: Dict[str, float],
        method: str = "keyword"
    ) -> Dict:
        """
        Explain table selection with reasoning.
        
        Args:
            query: Original user query
            selected_tables: Tables that were selected
            scores: Relevance scores for each table
            method: Method used (keyword, semantic, hybrid)
        
        Returns:
            {
                "summary": str,
                "details": List[Dict],
                "method": str,
                "confidence": float
            }
        """
        details = []
        
        for table in selected_tables:
            score = scores.get(table, 0.0)
            explanation = self._explain_table_match(query, table, score, method)
            details.append({
                "table": table,
                "score": score,
                "reason": explanation,
                "description": self.table_descriptions.get(table, "No description available")
            })
        
        # Sort by score
        details.sort(key=lambda x: x['score'], reverse=True)
        
        # Calculate overall confidence
        avg_score = sum(scores.values()) / len(scores) if scores else 0
        confidence = min(0.95, avg_score / 10.0)  # Normalize to 0-1
        
        summary = self._generate_summary(selected_tables, method, confidence)
        
        return {
            "summary": summary,
            "details": details,
            "method": method,
            "confidence": confidence,
            "total_tables_considered": len(scores),
            "tables_selected": len(selected_tables)
        }
    
    def _explain_table_match(self, query: str, table: str, score: float, method: str) -> str:
        """Generate explanation for why a table matched."""
        query_lower = query.lower()
        table_lower = table.lower()
        
        reasons = []
        
        # Exact table name match
        if table_lower in query_lower:
            reasons.append(f"Exact match: '{table}' mentioned in query")
        
        # Keyword matches
        keywords = self._extract_table_keywords(table)
        matched_keywords = [kw for kw in keywords if kw in query_lower]
        if matched_keywords:
            reasons.append(f"Keywords matched: {', '.join(matched_keywords)}")
        
        # Context-based reasoning
        context_reason = self._get_context_reason(query_lower, table)
        if context_reason:
            reasons.append(context_reason)
        
        # If no specific reasons, provide general one
        if not reasons:
            reasons.append(f"General relevance based on {method} matching")
        
        return " | ".join(reasons)
    
    def _extract_table_keywords(self, table: str) -> List[str]:
        """Extract relevant keywords for a table."""
        keyword_map = {
            "production_orders": ["order", "po", "production", "quantity", "planned", "actual"],
            "shift_logs": ["shift", "day", "night", "supervisor", "date"],
            "production_steps": ["step", "stage", "operator", "parameter", "temperature", "pressure"],
            "products": ["product", "item", "coating", "adhesive", "polymer"],
            "line_master": ["line", "capacity", "equipment", "building"],
            "staff": ["staff", "employee", "supervisor", "operator"],
            "recipes": ["recipe", "process", "cycle", "version"],
        }
        return keyword_map.get(table, [])
    
    def _get_context_reason(self, query: str, table: str) -> str:
        """Get context-based reasoning for table selection."""
        context_rules = {
            "production_orders": {
                "triggers": ["yield", "output", "performance", "completed", "planned"],
                "reason": "Required for production metrics and order tracking"
            },
            "shift_logs": {
                "triggers": ["shift", "day", "night", "supervisor", "daily"],
                "reason": "Needed for shift-level analysis and supervisor tracking"
            },
            "production_steps": {
                "triggers": ["detail", "step", "stage", "operator", "breakdown"],
                "reason": "Provides granular step-level production details"
            },
            "line_master": {
                "triggers": ["line", "capacity", "location", "building"],
                "reason": "Provides line configuration and capacity information"
            },
        }
        
        rule = context_rules.get(table)
        if not rule:
            return ""
        
        for trigger in rule["triggers"]:
            if trigger in query:
                return rule["reason"]
        
        return ""
    
    def _generate_summary(self, tables: List[str], method: str, confidence: float) -> str:
        """Generate human-readable summary."""
        table_count = len(tables)
        
        if table_count == 0:
            return "⚠️ No tables matched the query criteria"
        elif table_count == 1:
            return f"✓ Selected 1 table using {method} matching (confidence: {confidence:.0%})"
        else:
            return f"✓ Selected {table_count} tables using {method} matching (confidence: {confidence:.0%})"
    
    def format_explanation(self, explanation: Dict) -> str:
        """Format explanation as readable text."""
        lines = [
            f"🗄️ Schema Selection:",
            f"",
            explanation["summary"],
            f"",
            f"Tables Selected:",
        ]
        
        for detail in explanation["details"]:
            lines.append(f"")
            lines.append(f"  📋 {detail['table']}")
            lines.append(f"     Score: {detail['score']:.1f}")
            lines.append(f"     Reason: {detail['reason']}")
            lines.append(f"     Purpose: {detail['description']}")
        
        lines.extend([
            f"",
            f"Method: {explanation['method'].title()} Matching",
            f"Total Tables Considered: {explanation['total_tables_considered']}",
        ])
        
        return "\n".join(lines)
    
    def compare_methods(
        self,
        keyword_result: Dict,
        semantic_result: Dict = None
    ) -> Dict:
        """Compare results from different matching methods."""
        comparison = {
            "keyword": {
                "tables": keyword_result.get("details", []),
                "confidence": keyword_result.get("confidence", 0)
            }
        }
        
        if semantic_result:
            comparison["semantic"] = {
                "tables": semantic_result.get("details", []),
                "confidence": semantic_result.get("confidence", 0)
            }
            
            # Find differences
            kw_tables = set(t["table"] for t in keyword_result.get("details", []))
            sem_tables = set(t["table"] for t in semantic_result.get("details", []))
            
            comparison["differences"] = {
                "only_keyword": list(kw_tables - sem_tables),
                "only_semantic": list(sem_tables - kw_tables),
                "both": list(kw_tables & sem_tables)
            }
        
        return comparison
