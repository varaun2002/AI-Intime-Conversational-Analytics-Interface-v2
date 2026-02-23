"""
KPI Explanation Module
Explains KPI calculations and business logic.
"""
from typing import Dict, List, Any


class KPIExplainer:
    """
    Explains KPI calculations, formulas, and business logic.
    Documents assumptions and data sources for each metric.
    """
    
    # Standard KPI formulas and explanations
    KPI_DEFINITIONS = {
        # Actual KPI keys from kpi_agent.py
        "avg_yield": {
            "formula": "Mean(Actual / Planned)",
            "description": "Average yield percentage across period",
            "good_range": "> 95%",
            "units": "%",
        },
        "min_yield": {
            "formula": "Min(Actual / Planned)",
            "description": "Lowest yield percentage in period",
            "good_range": "> 85%",
            "units": "%",
        },
        "max_yield": {
            "formula": "Max(Actual / Planned)",
            "description": "Highest yield percentage in period",
            "good_range": "> 95%",
            "units": "%",
        },
        "yield_variance": {
            "formula": "Var(Actual / Planned)",
            "description": "Variance of yield percentages",
            "good_range": "< 10%",
            "units": "variance",
        },
        "avg_variance": {
            "formula": "Mean(|Planned - Actual|)",
            "description": "Average difference between planned and actual",
            "good_range": "< 5",
            "units": "units",
        },
        "trend_data": {
            "formula": "Time-series aggregation",
            "description": "KPI values aggregated by date (TREND intent)",
            "good_range": "Increasing trend",
            "units": "varies",
        },
        "yield_by_line": {
            "formula": "Mean(Actual / Planned) grouped by line",
            "description": "Yield percentage breakdown by production line",
            "good_range": "> 95%",
            "units": "%",
        },
        "yield_by_supervisor": {
            "formula": "Mean(Actual / Planned) grouped by supervisor",
            "description": "Yield percentage breakdown by supervisor",
            "good_range": "> 95%",
            "units": "%",
        },
        "output_by_product_name": {
            "formula": "Sum(Actual) grouped by product",
            "description": "Total production output by product",
            "good_range": "Meets plan",
            "units": "units",
        },
        # Legacy definitions for backward compatibility
        "yield": {
            "formula": "(Actual Quantity / Planned Quantity) × 100",
            "description": "Percentage of planned production actually achieved",
            "good_range": "> 95%",
            "units": "%",
        },
        "efficiency": {
            "formula": "(Actual Output / Standard Output) × 100",
            "description": "How efficiently resources were used vs. standard",
            "good_range": "> 85%",
            "units": "%",
        },
        "oee": {
            "formula": "Availability × Performance × Quality",
            "description": "Overall Equipment Effectiveness - comprehensive productivity metric",
            "good_range": "> 85%",
            "units": "%",
        },
        "cycle_time": {
            "formula": "Total Production Time / Units Produced",
            "description": "Average time to produce one unit",
            "good_range": "< Target cycle time",
            "units": "minutes",
        },
        "utilization": {
            "formula": "(Actual Production Time / Available Time) × 100",
            "description": "Percentage of available time actually spent producing",
            "good_range": "> 80%",
            "units": "%",
        }
    }
    
    def explain_kpi(
        self,
        kpi_name: str,
        value: float,
        calculation_details: Dict[str, Any] = None
    ) -> Dict:
        """
        Explain a KPI calculation with context.
        
        Args:
            kpi_name: Name of the KPI
            value: Calculated value
            calculation_details: Dict with numerator, denominator, etc.
        
        Returns:
            {
                "kpi": str,
                "value": float,
                "formula": str,
                "description": str,
                "interpretation": str,
                "calculation_breakdown": str,
                "data_sources": List[str],
                "assumptions": List[str]
            }
        """
        definition = self.KPI_DEFINITIONS.get(kpi_name.lower(), {})
        
        interpretation = self._interpret_value(kpi_name, value, definition)
        
        breakdown = ""
        if calculation_details:
            breakdown = self._format_calculation(kpi_name, calculation_details)
        
        return {
            "kpi": kpi_name,
            "value": value,
            "formula": definition.get("formula", "Custom calculation"),
            "description": definition.get("description", f"Custom metric: {kpi_name}"),
            "interpretation": interpretation,
            "calculation_breakdown": breakdown,
            "data_sources": self._identify_data_sources(kpi_name),
            "assumptions": self._identify_assumptions(kpi_name),
            "units": definition.get("units", ""),
            "good_range": definition.get("good_range", "")
        }
    
    def _interpret_value(self, kpi_name: str, value: float, definition: Dict) -> str:
        """Interpret a KPI value."""
        interpretations = definition.get("interpretation", {})
        
        if not interpretations:
            return f"Value: {value}"
        
        # Check threshold-based interpretations
        for threshold, meaning in interpretations.items():
            if self._matches_threshold(value, threshold):
                return f"{meaning} (value: {value})"
        
        return f"Value: {value}"
    
    def _matches_threshold(self, value: float, threshold: str) -> bool:
        """Check if value matches threshold description."""
        try:
            if '>' in threshold and '<' not in threshold:
                threshold_val = float(threshold.replace('>', '').strip().replace('%', ''))
                return value > threshold_val
            elif '<' in threshold and '>' not in threshold:
                threshold_val = float(threshold.replace('<', '').strip().replace('%', ''))
                return value < threshold_val
            elif '-' in threshold:
                parts = threshold.split('-')
                low = float(parts[0].strip().replace('%', ''))
                high = float(parts[1].strip().replace('%', ''))
                return low <= value <= high
            elif '=' in threshold:
                threshold_val = float(threshold.replace('=', '').strip().replace('%', ''))
                return abs(value - threshold_val) < 0.01
        except:
            pass
        
        return False
    
    def _format_calculation(self, kpi_name: str, details: Dict) -> str:
        """Format calculation details."""
        lines = []
        
        if "numerator" in details and "denominator" in details:
            lines.append(f"Calculation:")
            lines.append(f"  Numerator: {details['numerator']}")
            lines.append(f"  Denominator: {details['denominator']}")
            lines.append(f"  Result: {details['numerator']} / {details['denominator']} = {details.get('result', 'N/A')}")
        
        if "components" in details:
            lines.append(f"Components:")
            for key, val in details["components"].items():
                lines.append(f"  {key}: {val}")
        
        if "filters" in details:
            lines.append(f"Data filtered by:")
            for filt in details["filters"]:
                lines.append(f"  • {filt}")
        
        return "\n".join(lines)
    
    def _identify_data_sources(self, kpi_name: str) -> List[str]:
        """Identify data sources for KPI."""
        source_map = {
            "yield": ["production_orders (planned_quantity, actual_quantity)"],
            "efficiency": ["production_orders", "recipes (standard_cycle_time)"],
            "oee": ["shift_logs", "production_steps", "downtime_logs"],
            "cycle_time": ["production_steps (start_time, end_time)"],
            "utilization": ["shift_logs (shift_start, shift_end)", "production_orders"],
        }
        
        return source_map.get(kpi_name.lower(), ["Multiple tables"])
    
    def _identify_assumptions(self, kpi_name: str) -> List[str]:
        """Identify assumptions made in calculation."""
        assumption_map = {
            "yield": [
                "Planned quantity represents actual production target",
                "Actual quantity includes only good/accepted units",
                "Partial orders are included in calculations"
            ],
            "efficiency": [
                "Standard times are accurate and up-to-date",
                "All production time is included (no gaps)",
                "Downtime is excluded from efficiency calculation"
            ],
            "oee": [
                "Availability = Runtime / Planned production time",
                "Performance = (Total parts / Operating time) / Ideal run rate",
                "Quality = Good parts / Total parts produced"
            ],
            "cycle_time": [
                "Cycle time measured from step start to step completion",
                "Setup time is excluded",
                "Only completed units are counted"
            ],
            "utilization": [
                "Available time = Total shift duration",
                "Scheduled breaks are excluded from available time",
                "Unplanned downtime reduces utilization"
            ]
        }
        
        return assumption_map.get(kpi_name.lower(), ["Standard business logic applied"])
    
    def explain_multiple_kpis(self, kpis: Dict[str, float]) -> Dict:
        """Explain multiple KPIs together with context."""
        explanations = {}
        
        for kpi_name, value in kpis.items():
            explanations[kpi_name] = self.explain_kpi(kpi_name, value)
        
        # Add comparative insights
        insights = self._generate_comparative_insights(kpis)
        
        return {
            "kpis": explanations,
            "comparative_insights": insights,
            "summary": self._generate_kpi_summary(kpis)
        }
    
    def _generate_comparative_insights(self, kpis: Dict[str, float]) -> List[str]:
        """Generate insights by comparing multiple KPIs."""
        insights = []
        
        # Yield vs Efficiency
        if "yield" in kpis and "efficiency" in kpis:
            if kpis["yield"] > 95 and kpis["efficiency"] < 85:
                insights.append("⚠️ High yield but low efficiency suggests room for speed optimization")
            elif kpis["yield"] < 90 and kpis["efficiency"] > 90:
                insights.append("⚠️ High efficiency but low yield suggests quality or capacity issues")
        
        # Utilization insights
        if "utilization" in kpis:
            if kpis["utilization"] < 70:
                insights.append("⚠️ Low utilization indicates significant idle time or downtime")
            elif kpis["utilization"] > 95:
                insights.append("✓ Excellent utilization - equipment running near capacity")
        
        # Overall performance
        if all(k in kpis for k in ["yield", "efficiency", "utilization"]):
            avg = sum(kpis[k] for k in ["yield", "efficiency", "utilization"]) / 3
            if avg > 90:
                insights.append("✓ Strong overall performance across all metrics")
            elif avg < 80:
                insights.append("⚠️ Multiple metrics below target - review process")
        
        return insights
    
    def _generate_kpi_summary(self, kpis: Dict[str, float]) -> str:
        """Generate overall summary of KPIs."""
        total = len(kpis)
        
        # Count how many are in "good" range
        good_count = 0
        for kpi_name, value in kpis.items():
            definition = self.KPI_DEFINITIONS.get(kpi_name.lower(), {})
            good_range = definition.get("good_range", "")
            
            if '>' in good_range:
                threshold = float(good_range.replace('>', '').strip().replace('%', ''))
                if value > threshold:
                    good_count += 1
            elif '<' in good_range:
                threshold = float(good_range.replace('<', '').strip().replace('%', ''))
                if value < threshold:
                    good_count += 1
        
        if good_count == total:
            return f"✓ All {total} KPIs meeting targets"
        elif good_count >= total * 0.7:
            return f"⚠️ {good_count}/{total} KPIs meeting targets"
        else:
            return f"⚠️ Only {good_count}/{total} KPIs meeting targets - attention needed"
    
    def format_explanation(self, explanation: Dict) -> str:
        """Format KPI explanation as readable text."""
        lines = [
            f"📊 KPI: {explanation['kpi']}",
            f"",
            f"Value: {explanation['value']:.2f} {explanation['units']}",
            f"",
            f"Description: {explanation['description']}",
            f"Formula: {explanation['formula']}",
            f"",
            f"Interpretation: {explanation['interpretation']}",
            f"Target Range: {explanation['good_range']}",
        ]
        
        if explanation["calculation_breakdown"]:
            lines.append("")
            lines.append(explanation["calculation_breakdown"])
        
        lines.append("")
        lines.append("Data Sources:")
        for source in explanation["data_sources"]:
            lines.append(f"  • {source}")
        
        lines.append("")
        lines.append("Assumptions:")
        for assumption in explanation["assumptions"]:
            lines.append(f"  • {assumption}")
        
        return "\n".join(lines)
