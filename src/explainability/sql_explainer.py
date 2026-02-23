"""
SQL Explanation Module
Explains generated SQL queries in plain English.
"""
import re
import sqlparse
from typing import Dict, List


class SQLExplainer:
    """
    Breaks down SQL queries into understandable components.
    Explains joins, filters, aggregations, and logic.
    """
    
    def explain_query(self, sql: str) -> Dict:
        """
        Explain a SQL query in plain English.
        
        Returns:
            {
                "summary": str,
                "components": Dict,
                "plain_english": str,
                "complexity": str,
                "performance_notes": List[str]
            }
        """
        # Format SQL for better parsing
        formatted_sql = sqlparse.format(
            sql,
            reindent=True,
            keyword_case='upper'
        )
        
        components = {
            "tables": self._extract_tables(sql),
            "columns": self._extract_columns(sql),
            "joins": self._extract_joins(sql),
            "filters": self._extract_filters(sql),
            "aggregations": self._extract_aggregations(sql),
            "grouping": self._extract_grouping(sql),
            "ordering": self._extract_ordering(sql),
            "limits": self._extract_limits(sql)
        }
        
        plain_english = self._generate_plain_english(components)
        complexity = self._estimate_complexity(components)
        performance_notes = self._generate_performance_notes(components)
        
        return {
            "summary": self._generate_summary(components),
            "components": components,
            "plain_english": plain_english,
            "complexity": complexity,
            "performance_notes": performance_notes,
            "formatted_sql": formatted_sql
        }
    
    def _extract_tables(self, sql: str) -> List[Dict]:
        """Extract table information."""
        tables = []
        
        # FROM clause
        from_match = re.search(r'FROM\s+(\w+)(?:\s+AS\s+(\w+))?', sql, re.IGNORECASE)
        if from_match:
            tables.append({
                "name": from_match.group(1),
                "alias": from_match.group(2),
                "type": "primary"
            })
        
        # JOIN clauses
        join_pattern = r'(?:LEFT|RIGHT|INNER|OUTER)?\s*JOIN\s+(\w+)(?:\s+AS\s+(\w+))?'
        for match in re.finditer(join_pattern, sql, re.IGNORECASE):
            tables.append({
                "name": match.group(1),
                "alias": match.group(2),
                "type": "joined"
            })
        
        return tables
    
    def _extract_columns(self, sql: str) -> List[str]:
        """Extract selected columns."""
        # Simple extraction from SELECT clause
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', sql, re.IGNORECASE | re.DOTALL)
        if not select_match:
            return []
        
        columns_str = select_match.group(1)
        
        # Handle SELECT *
        if '*' in columns_str:
            return ["* (all columns)"]
        
        # Split by comma and clean
        columns = [col.strip() for col in columns_str.split(',')]
        return columns
    
    def _extract_joins(self, sql: str) -> List[Dict]:
        """Extract JOIN information."""
        joins = []
        
        join_pattern = r'(LEFT|RIGHT|INNER|OUTER)?\s*JOIN\s+(\w+)(?:\s+AS\s+(\w+))?\s+ON\s+(.*?)(?:LEFT|RIGHT|INNER|OUTER|JOIN|WHERE|GROUP|ORDER|$)'
        
        for match in re.finditer(join_pattern, sql, re.IGNORECASE | re.DOTALL):
            join_type = match.group(1) or "INNER"
            table = match.group(2)
            alias = match.group(3)
            condition = match.group(4).strip()
            
            joins.append({
                "type": join_type.upper(),
                "table": table,
                "alias": alias,
                "condition": condition,
                "explanation": self._explain_join_condition(condition)
            })
        
        return joins
    
    def _explain_join_condition(self, condition: str) -> str:
        """Explain a JOIN condition in plain English."""
        # Simple pattern matching
        if '=' in condition:
            parts = condition.split('=')
            if len(parts) == 2:
                left = parts[0].strip()
                right = parts[1].strip()
                return f"Matching {left} with {right}"
        
        return condition
    
    def _extract_filters(self, sql: str) -> List[Dict]:
        """Extract WHERE clause filters."""
        filters = []
        
        where_match = re.search(r'WHERE\s+(.*?)(?:GROUP BY|ORDER BY|LIMIT|$)', sql, re.IGNORECASE | re.DOTALL)
        if not where_match:
            return []
        
        where_clause = where_match.group(1).strip()
        
        # Split by AND/OR
        conditions = re.split(r'\s+AND\s+|\s+OR\s+', where_clause, flags=re.IGNORECASE)
        
        for condition in conditions:
            condition = condition.strip()
            filters.append({
                "condition": condition,
                "explanation": self._explain_filter(condition)
            })
        
        return filters
    
    def _explain_filter(self, condition: str) -> str:
        """Explain a filter condition."""
        condition = condition.strip()
        
        # Date filters
        if re.search(r'date', condition, re.IGNORECASE):
            if '>=' in condition or '<=' in condition:
                return "Date range filter"
            elif '=' in condition:
                return "Specific date filter"
        
        # LIKE filters
        if 'LIKE' in condition.upper():
            return "Text pattern matching"
        
        # IN filters
        if 'IN' in condition.upper():
            return "Value must be in specified list"
        
        # Comparison filters
        if '>=' in condition:
            return "Greater than or equal to"
        elif '<=' in condition:
            return "Less than or equal to"
        elif '>' in condition:
            return "Greater than"
        elif '<' in condition:
            return "Less than"
        elif '=' in condition:
            return "Exact match"
        
        return condition
    
    def _extract_aggregations(self, sql: str) -> List[Dict]:
        """Extract aggregation functions."""
        aggregations = []
        
        agg_pattern = r'(COUNT|SUM|AVG|MIN|MAX|ROUND)\s*\([^)]+\)(?:\s+AS\s+(\w+))?'
        
        for match in re.finditer(agg_pattern, sql, re.IGNORECASE):
            func = match.group(0)
            alias = match.group(2)
            
            aggregations.append({
                "function": func,
                "alias": alias,
                "explanation": self._explain_aggregation(func)
            })
        
        return aggregations
    
    def _explain_aggregation(self, func: str) -> str:
        """Explain an aggregation function."""
        func_upper = func.upper()
        
        if 'COUNT' in func_upper:
            return "Counting number of records"
        elif 'SUM' in func_upper:
            return "Calculating total sum"
        elif 'AVG' in func_upper:
            return "Calculating average"
        elif 'MIN' in func_upper:
            return "Finding minimum value"
        elif 'MAX' in func_upper:
            return "Finding maximum value"
        elif 'ROUND' in func_upper:
            return "Rounding to decimal places"
        
        return func
    
    def _extract_grouping(self, sql: str) -> List[str]:
        """Extract GROUP BY columns."""
        group_match = re.search(r'GROUP BY\s+(.*?)(?:HAVING|ORDER BY|LIMIT|$)', sql, re.IGNORECASE | re.DOTALL)
        if not group_match:
            return []
        
        groups = group_match.group(1).strip().split(',')
        return [g.strip() for g in groups]
    
    def _extract_ordering(self, sql: str) -> List[Dict]:
        """Extract ORDER BY information."""
        order_match = re.search(r'ORDER BY\s+(.*?)(?:LIMIT|$)', sql, re.IGNORECASE | re.DOTALL)
        if not order_match:
            return []
        
        orders = []
        order_parts = order_match.group(1).strip().split(',')
        
        for part in order_parts:
            part = part.strip()
            direction = "ASC"
            
            if part.upper().endswith(' DESC'):
                direction = "DESC"
                column = part[:-5].strip()
            elif part.upper().endswith(' ASC'):
                column = part[:-4].strip()
            else:
                column = part
            
            orders.append({
                "column": column,
                "direction": direction
            })
        
        return orders
    
    def _extract_limits(self, sql: str) -> Dict:
        """Extract LIMIT information."""
        limit_match = re.search(r'LIMIT\s+(\d+)', sql, re.IGNORECASE)
        if not limit_match:
            return {}
        
        return {
            "value": int(limit_match.group(1)),
            "explanation": f"Limiting results to {limit_match.group(1)} rows"
        }
    
    def _generate_summary(self, components: Dict) -> str:
        """Generate a brief summary."""
        parts = []
        
        if components["aggregations"]:
            parts.append("Aggregated query")
        else:
            parts.append("Data retrieval query")
        
        table_count = len(components["tables"])
        if table_count > 1:
            parts.append(f"joining {table_count} tables")
        
        if components["filters"]:
            parts.append(f"with {len(components['filters'])} filter(s)")
        
        return " ".join(parts)
    
    def _generate_plain_english(self, components: Dict) -> str:
        """Generate plain English explanation."""
        lines = []
        
        # What we're getting
        if components["aggregations"]:
            lines.append("Calculate:")
            for agg in components["aggregations"]:
                alias = agg["alias"] or "value"
                lines.append(f"  • {alias}: {agg['explanation']}")
        else:
            col_count = len(components["columns"])
            if col_count > 0:
                lines.append(f"Retrieve {col_count} columns from the database")
        
        # From which tables
        lines.append("")
        lines.append("From tables:")
        for table in components["tables"]:
            lines.append(f"  • {table['name']} ({table['type']})")
        
        # How tables are joined
        if components["joins"]:
            lines.append("")
            lines.append("Table relationships:")
            for join in components["joins"]:
                lines.append(f"  • {join['type']} JOIN {join['table']}: {join['explanation']}")
        
        # What filters are applied
        if components["filters"]:
            lines.append("")
            lines.append("Filters applied:")
            for filt in components["filters"]:
                lines.append(f"  • {filt['explanation']}: {filt['condition']}")
        
        # How data is grouped
        if components["grouping"]:
            lines.append("")
            lines.append(f"Grouped by: {', '.join(components['grouping'])}")
        
        # How data is sorted
        if components["ordering"]:
            lines.append("")
            lines.append("Sorted by:")
            for order in components["ordering"]:
                lines.append(f"  • {order['column']} ({order['direction']})")
        
        # Result limits
        if components["limits"]:
            lines.append("")
            lines.append(components["limits"]["explanation"])
        
        return "\n".join(lines)
    
    def _estimate_complexity(self, components: Dict) -> str:
        """Estimate query complexity."""
        score = 0
        
        score += len(components["tables"])
        score += len(components["joins"]) * 2
        score += len(components["aggregations"])
        score += min(len(components["filters"]), 3)
        
        if score <= 3:
            return "simple"
        elif score <= 7:
            return "moderate"
        else:
            return "complex"
    
    def _generate_performance_notes(self, components: Dict) -> List[str]:
        """Generate performance considerations."""
        notes = []
        
        if len(components["joins"]) > 2:
            notes.append("⚠️ Multiple joins may impact performance on large datasets")
        
        if not components["filters"]:
            notes.append("⚠️ No filters applied - may return large result set")
        
        if components["aggregations"] and not components["grouping"]:
            notes.append("✓ Good: Aggregating entire dataset")
        
        if components["limits"]:
            notes.append("✓ Good: Results limited for performance")
        
        # Check for indexed columns in filters
        for filt in components["filters"]:
            if 'date' in filt["condition"].lower():
                notes.append("✓ Date filter likely using index")
        
        return notes
    
    def format_explanation(self, explanation: Dict) -> str:
        """Format explanation as readable text."""
        lines = [
            f"🔍 SQL Query Explanation:",
            f"",
            f"Summary: {explanation['summary']}",
            f"Complexity: {explanation['complexity']}",
            f"",
            f"{explanation['plain_english']}",
        ]
        
        if explanation["performance_notes"]:
            lines.append("")
            lines.append("Performance Notes:")
            for note in explanation["performance_notes"]:
                lines.append(f"  {note}")
        
        return "\n".join(lines)
