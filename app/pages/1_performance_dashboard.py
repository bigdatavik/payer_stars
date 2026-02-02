"""
Performance Dashboard - CMS Star Ratings Overview
Includes natural language queries via Databricks Genie
"""

import streamlit as st
import os
from databricks import sql
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

st.set_page_config(layout="wide")

st.title("📈 Performance Dashboard")

st.markdown("""
View your organization's CMS Star Ratings performance across all HEDIS measures.
""")

# Configuration from environment
CATALOG = os.getenv("CATALOG_NAME", "payer_stars_dev")
SCHEMA = os.getenv("SCHEMA_NAME", "star_ratings")
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "148ccb90800933a1")

# Initialize clients
@st.cache_resource
def get_workspace_client():
    """Initialize Databricks WorkspaceClient"""
    try:
        return WorkspaceClient()
    except Exception as e:
        st.error(f"Failed to initialize Databricks client: {e}")
        return None

def get_sql_connection():
    """Create Databricks SQL connection - called lazily when needed"""
    try:
        cfg = Config()
        return sql.connect(
            server_hostname=cfg.host,
            http_path=f"/sql/1.0/warehouses/{WAREHOUSE_ID}",
            credentials_provider=lambda: cfg.authenticate,
        )
    except Exception as e:
        st.error(f"SQL Connection error: {e}")
        return None

w = get_workspace_client()

# Get Genie Space ID - DATABASE-FIRST with config.yaml override
def get_genie_space_id():
    """
    Get Genie Space ID from multiple sources (in priority order):
    1. Environment variable (manual override from config.yaml)
    2. config_genie table (automatic discovery - PRIMARY SOURCE)
    
    This allows automatic discovery without manual config updates.
    """
    # Try environment variable first (manual override)
    env_genie_id = os.getenv("GENIE_SPACE_ID")
    if env_genie_id:
        return env_genie_id
    
    # Fall back to querying config_genie table (PRIMARY SOURCE)
    try:
        sql_conn = get_sql_connection()
        if sql_conn:
            with sql_conn.cursor() as cursor:
                cursor.execute(f"""
                    SELECT config_value 
                    FROM {CATALOG}.{SCHEMA}.config_genie 
                    WHERE config_key = 'genie_space_id'
                """)
                result = cursor.fetchone()
                if result and result[0]:
                    return result[0]
    except Exception as e:
        # Silently fail - will show warning in UI
        pass
    
    return None

GENIE_SPACE_ID = get_genie_space_id()

# Summary metrics
st.markdown("### Overall Performance")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Current Star Rating", "3.5", delta="+0.5 vs last year", delta_color="normal")

with col2:
    st.metric("Measures at Target", "12/25", delta="+3", delta_color="normal")

with col3:
    st.metric("Avg Gap to Target", "8.2%", delta="-1.3%", delta_color="inverse")

with col4:
    st.metric("Improvement Trend", "↗️ Improving")

st.markdown("---")

# Key measures at risk
st.markdown("### 🚨 Measures Requiring Attention")

risk_measures = {
    "BCS - Breast Cancer Screening": {"current": 62, "target": 75, "gap": 13, "trend": "📉 Declining"},
    "CDC - Diabetes Care (HbA1c)": {"current": 68, "target": 80, "gap": 12, "trend": "➡️ Stable"},
    "CBP - Blood Pressure Control": {"current": 65, "target": 78, "gap": 13, "trend": "📈 Improving"},
    "COL - Colorectal Screening": {"current": 58, "target": 72, "gap": 14, "trend": "📉 Declining"},
}

for measure, data in risk_measures.items():
    with st.expander(f"**{measure}** - Gap: {data['gap']}% | {data['trend']}"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Rate", f"{data['current']}%")
        with col2:
            st.metric("Target Rate", f"{data['target']}%")
        with col3:
            st.metric("Gap", f"{data['gap']}%")
        
        st.markdown(f"""
        **Quick Actions:**
        - 🎯 [Analyze Root Causes](/measure_analysis?measure={measure.split('-')[0].strip()})
        - 💡 [Get Improvement Plan](/improvement_planner?measure={measure.split('-')[0].strip()})
        - 📊 [View Member List](#{measure.lower().replace(' ', '-')})
        """)

st.markdown("---")

# Top performing measures
st.markdown("### ⭐ Top Performing Measures")

top_measures = {
    "MPM - Medication Adherence for Diabetes": {"rate": 89, "target": 80, "above": 9, "weight": 3},
    "KED - Kidney Health Evaluation for Diabetes": {"rate": 87, "target": 78, "above": 9, "weight": 3},
    "SPC - Statin Therapy for CVD": {"rate": 91, "target": 85, "above": 6, "weight": 3},
}

cols = st.columns(3)
for i, (measure, data) in enumerate(top_measures.items()):
    with cols[i]:
        st.success(f"**{measure}**")
        st.metric("Performance", f"{data['rate']}%", delta=f"+{data['above']}% above target")
        st.caption(f"⭐ Weight: {data['weight']}x (Outcomes Measure)")

st.markdown("---")

# Genie Natural Language Interface
st.subheader("💬 Ask Genie - Natural Language Queries")

if GENIE_SPACE_ID:
    st.markdown("""
    Ask questions about your Star Ratings data in plain English. Genie will automatically generate SQL and return results.
    """)
    
    # Initialize session state for query
    if 'genie_selected_query' not in st.session_state:
        st.session_state.genie_selected_query = ""
    
    # Example questions (Medicare-focused)
    example_questions = [
        "Show me all HEDIS measures with performance below target",
        "What is the average performance rate by domain?",
        "Which Part D measures have the largest gaps?",
        "Show me trends for diabetes and medication adherence measures",
        "What's our weighted star rating by measure category?",
        "Which measures declined the most this quarter?",
        "Show readmissions and high-risk medication rates",
        "What percentage of members 65+ completed preventive screenings?"
    ]
    
    # User input
    user_question = st.text_input(
        "Your question:",
        value=st.session_state.genie_selected_query,
        placeholder="e.g., Show me all measures with gaps over 10%",
        help="Ask any question about your Star Ratings data"
    )
    
    # Quick question buttons in a grid
    st.markdown("**Quick Questions:**")
    col1, col2, col3 = st.columns(3)
    
    for i, question in enumerate(example_questions):
        col_idx = i % 3
        with [col1, col2, col3][col_idx]:
            if st.button(question, key=f"q_{i}", use_container_width=True):
                st.session_state.genie_selected_query = question
                st.rerun()
    
    if user_question:
        with st.spinner("🤔 Genie is thinking..."):
            try:
                # Start conversation using official Genie API pattern
                start_response = w.api_client.do(
                    'POST',
                    f'/api/2.0/genie/spaces/{GENIE_SPACE_ID}/start-conversation',
                    body={'content': user_question}
                )
                
                conversation_id = start_response.get('conversation_id')
                message_id = start_response.get('message_id')
                
                if not conversation_id or not message_id:
                    st.error("Failed to start Genie conversation")
                else:
                    # Poll for result
                    max_attempts = 30  # 30 * 2 = 60 seconds max
                    attempt = 0
                    
                    while attempt < max_attempts:
                        time.sleep(2)  # Wait 2 seconds between polls
                        attempt += 1
                        
                        # Get message status
                        message_response = w.api_client.do(
                            'GET',
                            f'/api/2.0/genie/spaces/{GENIE_SPACE_ID}/conversations/{conversation_id}/messages/{message_id}'
                        )
                        
                        status = message_response.get('status')
                        
                        if status == 'COMPLETED':
                            # Extract results
                            attachments = message_response.get('attachments', [])
                            
                            if attachments:
                                attachment = attachments[0]
                                text_response = attachment.get('text', {}).get('content', '')
                                query = attachment.get('query', {}).get('query', '')
                                
                                # Display text response
                                if text_response:
                                    st.success("**Genie's Response:**")
                                    st.markdown(text_response)
                                
                                # Display generated SQL
                                if query:
                                    with st.expander("🔍 View Generated SQL"):
                                        st.code(query, language="sql")
                                    
                                    # Get query results
                                    try:
                                        attachment_id = attachment.get('query', {}).get('attachment_id') or attachment.get('attachment_id')
                                        if attachment_id:
                                            result_response = w.api_client.do(
                                                'GET',
                                                f'/api/2.0/genie/spaces/{GENIE_SPACE_ID}/conversations/{conversation_id}/messages/{message_id}/query-result/{attachment_id}'
                                            )
                                            
                                            # Extract data from statement_response
                                            stmt_response = result_response.get('statement_response', {})
                                            
                                            if stmt_response:
                                                # Get schema from manifest
                                                manifest = stmt_response.get('manifest', {})
                                                schema = manifest.get('schema', {})
                                                columns = schema.get('columns', [])
                                                column_names = [col.get('name') for col in columns]
                                                
                                                # Get data rows from result
                                                result_obj = stmt_response.get('result', {})
                                                data_array = result_obj.get('data_array', [])
                                                
                                                if data_array and column_names:
                                                    # Create DataFrame directly from data_array
                                                    df = pd.DataFrame(data_array, columns=column_names)
                                                    
                                                    st.success(f"✅ Found {len(df)} results")
                                                    st.dataframe(df, use_container_width=True)
                                                    
                                                    # Auto-generate chart if applicable
                                                    if len(df.columns) == 2 and len(df) > 1 and len(df) < 50:
                                                        st.markdown("**📊 Visualization:**")
                                                        fig = px.bar(df, x=df.columns[0], y=df.columns[1])
                                                        st.plotly_chart(fig, use_container_width=True)
                                                else:
                                                    st.info("Query executed successfully but returned no results.")
                                            else:
                                                st.warning("No statement_response in query result")
                                    except Exception as e:
                                        st.warning(f"Could not fetch query results: {e}")
                            else:
                                st.info("Query completed but no results available.")
                            break
                            
                        elif status == 'FAILED':
                            error = message_response.get('error', {})
                            st.error(f"Query failed: {error}")
                            break
                        elif status == 'CANCELLED':
                            st.warning("Query was cancelled")
                            break
                    
                    if attempt >= max_attempts:
                        st.warning("Query timed out. Please try a simpler question.")
                    
            except Exception as e:
                st.error(f"Error executing Genie query: {e}")
                st.info("💡 Make sure you've granted **Can Run** permissions to the app's service principal on the Genie Space.")
else:
    st.warning("⚠️ Genie Space not configured. The Genie natural language interface is currently unavailable.")
    st.markdown("""
    **To enable Genie:**
    1. Genie Space is automatically created during setup
    2. Grant **Can Run** permission to your app's service principal on the Genie Space
    3. See README for detailed instructions
    """)

st.markdown("---")

# Action items
st.markdown("### 📋 Recommended Actions")

st.markdown("""
1. **Immediate Focus**: Address 4 measures with gaps >10%
2. **Member Outreach**: 15,000 members need screening reminders  
3. **Provider Engagement**: 3 practices need quality improvement support
4. **Data Quality**: Review 200 claims with missing codes

**Next Review**: End of quarter (in 45 days)
""")

st.markdown("---")
st.caption("⭐ CMS Star Ratings Analytics | Performance data updated daily")
