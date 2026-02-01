"""
Measure Analysis Page - StateGraph Agent Demo
"""

import streamlit as st
import os

# Set wide layout to use full page width
st.set_page_config(layout="wide")

st.title("📊 Measure Analysis")

st.markdown("""
Analyze HEDIS measure performance using our StateGraph AI agent.
""")

# Read configuration from environment variables (set in app.yaml)
CATALOG = os.getenv("CATALOG_NAME", "payer_star_ratings_dev")
SCHEMA = os.getenv("SCHEMA_NAME", "main")
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "148ccb90800933a1")
VECTOR_ENDPOINT = os.getenv("VECTOR_ENDPOINT", "one-env-shared-endpoint-2")

# Sample measures for demo
SAMPLE_MEASURES = {
    "BCS - Breast Cancer Screening": {
        "measure_id": "BCS",
        "data": "Breast Cancer Screening (BCS): Performance rate 62%, Target 75%, Gap 13%, Numerator 6200, Denominator 10000, 10,000 eligible women aged 50-74"
    },
    "CDC - Comprehensive Diabetes Care": {
        "measure_id": "CDC",
        "data": "Comprehensive Diabetes Care (CDC): Performance rate 68%, Target 80%, Gap 12%, HbA1c testing compliance issues, 15,000 diabetic members"
    },
    "CBP - Controlling High Blood Pressure": {
        "measure_id": "CBP",
        "data": "Controlling High Blood Pressure (CBP): Performance rate 65%, Target 78%, Gap 13%, BP control <140/90, 20,000 hypertensive members"
    }
}

# UI
col1, col2 = st.columns([3, 1])

with col1:
    measure_select = st.selectbox(
        "Select HEDIS Measure:",
        list(SAMPLE_MEASURES.keys())
    )

with col2:
    st.metric("Current Gap", "13%", delta="-2% vs last year")

measure_info = SAMPLE_MEASURES[measure_select]

# Initialize session state for query
if 'selected_query' not in st.session_state:
    st.session_state.selected_query = ""

# Query input
query = st.text_input(
    "What would you like to know?",
    value=st.session_state.selected_query,
    placeholder="Why is this measure underperforming? How can we improve? What are the root causes?"
)

# Quick question buttons
st.markdown("**Quick Questions:**")

# Organize questions by category
col1, col2, col3 = st.columns(3)

sample_questions = [
    "Why is this measure underperforming?",
    "What are the top 3 barriers to improving performance?",
    "How can we close the gap for this measure?",
    "What evidence-based interventions can improve this measure?",
    "What member outreach strategies work best?",
    "Should we prioritize provider education or member engagement?",
    "What are quick wins we can implement this quarter?",
    "Which member segments should we target first?",
    "What are the best practices from top-performing plans?",
    "What are the root causes AND recommended interventions?",
    "Compare the effectiveness of patient reminders vs provider incentives",
    "What's the ROI of improving this measure to target?"
]

# Display buttons in 3 columns
for i, question in enumerate(sample_questions):
    col_idx = i % 3
    with [col1, col2, col3][col_idx]:
        if st.button(question, key=f"sample_q_{i}", use_container_width=True):
            st.session_state.selected_query = question
            st.rerun()

st.markdown("---")

if st.button("🧠 Analyze with StateGraph Agent", type="primary"):
    if not query:
        st.warning("Please enter a question")
    else:
        st.markdown("---")
        st.markdown("### 🤖 Agent Execution")
        
        with st.spinner("Running StateGraph workflow..."):
            try:
                # Import agent from utils
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
                from star_agent import StarRatingsAgent
                
                # Create agent
                agent = StarRatingsAgent(
                    catalog=CATALOG,
                    schema=SCHEMA,
                    warehouse_id=WAREHOUSE_ID,
                    vector_endpoint=VECTOR_ENDPOINT
                )
                
                # Analyze
                result = agent.analyze_measure(
                    measure_name=measure_select,
                    measure_data=measure_info["data"],
                    user_query=query
                )
                
                st.success("✅ Analysis complete!")
                
                # Debug: Show what we got back (COMMENTED OUT FOR PRODUCTION)
                # st.sidebar.markdown("**Debug Info:**")
                # st.sidebar.json({
                #     "query_type": result.get('query_type'),
                #     "has_classification": bool(result.get('classification')),
                #     "has_gaps": bool(result.get('gaps')),
                #     "has_recommendations": bool(result.get('recommendations')),
                #     "has_knowledge": bool(result.get('knowledge')),
                #     "knowledge_count": len(result.get('knowledge', [])) if result.get('knowledge') else 0
                # })
                
                # Display results
                st.markdown("---")
                st.markdown("### 📊 Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Query Type**: {result['query_type']}")
                
                with col2:
                    # Handle classification (could be string or dict)
                    if result.get('classification'):
                        try:
                            import json
                            classification = result['classification']
                            if isinstance(classification, str):
                                classification = json.loads(classification)
                            gap_severity = classification.get('gap_severity', 'Unknown')
                            st.markdown(f"**Gap Severity**: {gap_severity}")
                        except:
                            pass
                
                # Show formatted results only (no raw answer text)
                if result.get('classification'):
                    with st.expander("🎯 Performance Classification"):
                        import json
                        classification = result['classification']
                        if isinstance(classification, str):
                            classification = json.loads(classification)
                        st.json(classification)
                
                # Gap Analysis with tabs formatting
                if result.get('gaps'):
                    st.markdown("### 🔍 Gap Analysis")
                    
                    import json
                    gaps = result['gaps']
                    if isinstance(gaps, str):
                        gaps = json.loads(gaps)
                    
                    # Define tab configuration
                    tab_config = [
                        ('root_causes', '🔍 Root Causes'),
                        ('affected_populations', '👥 Affected Populations'),
                        ('performance_barriers', '🚧 Performance Barriers'),
                        ('data_quality_issues', '📊 Data Quality Issues')
                    ]
                    
                    # Create tabs
                    tab_labels = [label for _, label in tab_config]
                    tabs = st.tabs(tab_labels)
                    
                    # Populate each tab
                    for idx, (key, label) in enumerate(tab_config):
                        with tabs[idx]:
                            if key in gaps:
                                items = gaps[key]
                                if len(items) > 0:
                                    for item in items:
                                        st.markdown(f"• {item}")
                                else:
                                    st.info("No data available")
                            else:
                                st.info("No data available")
                
                if result.get('recommendations'):
                    with st.expander("💡 Recommendations"):
                        import json
                        recommendations = result['recommendations']
                        if isinstance(recommendations, str):
                            recommendations = json.loads(recommendations)
                        st.json(recommendations)
                
                if result.get('knowledge'):
                    with st.expander("📚 Vector Search Results (HEDIS Guidelines)"):
                        knowledge = result['knowledge']
                        if knowledge:
                            st.success(f"Found {len(knowledge)} relevant guideline documents")
                            for i, doc in enumerate(knowledge, 1):
                                st.markdown(f"**Document {i}:**")
                                if isinstance(doc, list) and len(doc) >= 3:
                                    st.markdown(f"- **Doc ID**: {doc[0]}")
                                    st.markdown(f"- **Title**: {doc[1]}")
                                    st.markdown(f"- **Content**: {doc[2][:500]}...")  # First 500 chars
                                st.markdown("---")
                        else:
                            st.info("No knowledge base results available")
                
            except Exception as e:
                st.error(f"Error: {e}")
                import traceback
                with st.expander("Error Details"):
                    st.code(traceback.format_exc())

# Info section
with st.expander("ℹ️ How it works"):
    st.markdown("""
    **StateGraph Workflow:**
    1. **Intent Classification** - Determines query type (analysis, improvement, Q&A)
    2. **Conditional Routing** - Routes to appropriate pipeline
    3. **Pipeline Execution** - Calls UC functions + vector search
    4. **Response Synthesis** - Combines results into coherent answer
    
    **Supported Query Types:**
    - **Measure Analysis**: "Why is this low?", "What are the problems?"
    - **Improvement**: "How can we improve?", "What interventions work?"
    - **Q&A**: "What is this measure?", "Explain the requirements"
    """)

st.markdown("---")
st.caption("⭐ CMS Star Ratings Analytics | Built with LangGraph StateGraph + Unity Catalog")
