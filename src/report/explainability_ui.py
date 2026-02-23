"""
Streamlit UI components for transparency and explainability.
"""
import streamlit as st


def show_query_analysis(analysis: dict):
    """Display query analysis in an expandable section."""
    with st.expander("📊 Query Analysis", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Intent", analysis.get("intent", "UNKNOWN"))
        with col2:
            st.metric("Confidence", f"{analysis.get('confidence', 0):.0%}")
        with col3:
            st.metric("Complexity", analysis.get("complexity", "unknown").title())
        
        st.write("**Reasoning:**")
        st.write(analysis.get("reasoning", "N/A"))
        
        # Entities detected
        entities = analysis.get("key_entities", {})
        if entities:
            st.write("**Entities Detected:**")
            for entity_type, values in entities.items():
                if values:
                    # Ensure all values are strings - robust handling
                    str_values = []
                    for v in values[:3]:
                        try:
                            if isinstance(v, str):
                                str_values.append(v)
                            elif isinstance(v, tuple):
                                # Join tuple elements or take first element
                                str_values.append(' '.join(str(x) for x in v if x) if len(v) > 1 else (v[0] if v else ''))
                            else:
                                str_values.append(str(v))
                        except Exception:
                            str_values.append(str(v))
                    if str_values:
                        st.write(f"- **{entity_type.replace('_', ' ').title()}:** {', '.join(str_values)}")


def show_schema_explanation(explanation: dict):
    """Display schema selection explanation."""
    with st.expander("🗄️ Schema Selection", expanded=False):
        st.write("**Summary:**")
        st.write(explanation.get("summary", "No summary available"))
        
        st.write("**Tables Selected:**")
        for detail in explanation.get("details", []):
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 2])
                with col1:
                    st.write(f"**{detail['table']}**")
                with col2:
                    st.metric("Score", f"{detail['score']:.2f}")
                with col3:
                    st.write(f"*{detail['reason']}*")
                st.write(f"```\n{detail['description']}\n```")
                st.divider()


def show_sql_explanation(explanation: dict):
    """Display SQL explanation."""
    with st.expander("🔍 SQL Query Explanation", expanded=False):
        st.write("**Summary:**")
        st.write(explanation.get("summary", "No summary available"))
        
        st.write("**Complexity:**")
        complexity = explanation.get("complexity", "unknown")
        st.write(f"- {complexity.title()}")
        
        st.write("**Plain English Explanation:**")
        st.text(explanation.get("plain_english", "N/A"))
        
        # Performance notes
        performance_notes = explanation.get("performance_notes", [])
        if performance_notes:
            st.write("**Performance Notes:**")
            for note in performance_notes:
                st.write(f"- {note}")
        
        # Show formatted SQL
        st.write("**Formatted Query:**")
        st.code(explanation.get("formatted_sql", ""), language="sql")


def show_kpi_explanations(kpi_explanations: dict):
    """Display KPI explanations."""
    if not kpi_explanations:
        return
    
    with st.expander("📈 KPI Explanations", expanded=False):
        for kpi_name, explanation in kpi_explanations.items():
            with st.container():
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    st.metric(
                        kpi_name.replace("_", " ").title(),
                        f"{explanation.get('value', 0):.2f} {explanation.get('units', '')}"
                    )
                with col2:
                    st.write("**Target Range:**")
                    st.write(explanation.get("good_range", "N/A"))
                with col3:
                    st.write("**Interpretation:**")
                    st.write(explanation.get("interpretation", "N/A"))
                
                # Show formula and details
                st.write(f"**Formula:** {explanation.get('formula', 'N/A')}")
                st.write(f"**Description:** {explanation.get('description', '')}")
                
                # Data sources
                sources = explanation.get("data_sources", [])
                if sources:
                    st.write("**Data Sources:**")
                    for source in sources:
                        st.write(f"- {source}")
                
                # Assumptions
                assumptions = explanation.get("assumptions", [])
                if assumptions:
                    st.write("**Assumptions:**")
                    for assumption in assumptions:
                        st.write(f"- {assumption}")
                
                st.divider()


def show_explainability_panel(report: dict):
    """Show a comprehensive explainability panel."""
    explainability = report.get("explainability", {})
    
    if not any(explainability.values()):
        st.info("💡 Explainability information not available for this query")
        return
    
    st.header("🔍 Explainability")
    st.write("---")
    
    # Query Analysis
    query_analysis = explainability.get("query_analysis")
    if query_analysis:
        show_query_analysis(query_analysis)
    
    # Schema Explanation
    schema_explanation = explainability.get("schema_explanation")
    if schema_explanation:
        show_schema_explanation(schema_explanation)
    
    # SQL Explanation
    sql_explanation = explainability.get("sql_explanation")
    if sql_explanation:
        show_sql_explanation(sql_explanation)
    
    # KPI Explanations
    kpi_explanations = explainability.get("kpi_explanations")
    if kpi_explanations:
        show_kpi_explanations(kpi_explanations)
