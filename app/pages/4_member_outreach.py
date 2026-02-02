"""
Member Outreach Page - Care Manager Portal
Identify and export members with HEDIS gaps for targeted outreach campaigns
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from databricks import sql
from databricks.sdk.core import Config

# Set wide layout
st.set_page_config(layout="wide", page_title="Member Outreach")

st.title("📞 Member Outreach Portal")

st.markdown("""
Identify members with HEDIS measure gaps for targeted care management outreach.
Select a measure, apply filters, and export member lists for outreach campaigns.
""")

# Configuration
CATALOG = os.getenv("CATALOG_NAME", "payer_stars_dev")
SCHEMA = os.getenv("SCHEMA_NAME", "star_ratings")
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "148ccb90800933a1")

# Initialize session state
if 'outreach_selected_measure' not in st.session_state:
    st.session_state.outreach_selected_measure = None
if 'outreach_members_df' not in st.session_state:
    st.session_state.outreach_members_df = None

# Database connection - EXACT SAME PATTERN as Performance Dashboard
def get_sql_connection():
    """Create Databricks SQL connection - same pattern as Performance Dashboard"""
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

def execute_query(query):
    """Execute SQL query and return DataFrame"""
    try:
        conn = get_sql_connection()
        if conn is None:
            return None
        
        with conn.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
        
        return pd.DataFrame(results, columns=columns)
    except Exception as e:
        st.error(f"Query execution failed: {e}")
        return None

# Load measures from database
st.markdown("---")
st.markdown("### 📊 Step 1: Select HEDIS Measure")

with st.spinner("Loading measures with gaps..."):
    measures_query = f"""
    SELECT 
        measure_id,
        measure_name,
        gap_severity,
        ROUND(gap * 100, 1) as gap_pct,
        ROUND(performance_rate * 100, 1) as performance_pct,
        ROUND(target_benchmark * 100, 1) as target_pct,
        denominator as eligible_members
    FROM {CATALOG}.{SCHEMA}.measures_data
    WHERE gap_severity IN ('Critical', 'Moderate', 'Minor')
    ORDER BY 
        CASE gap_severity 
            WHEN 'Critical' THEN 1 
            WHEN 'Moderate' THEN 2 
            WHEN 'Minor' THEN 3 
        END,
        gap DESC
    LIMIT 10
    """
    
    measures_df = execute_query(measures_query)

if measures_df is not None and len(measures_df) > 0:
    # Create measure display options
    measure_options = {}
    for _, row in measures_df.iterrows():
        display_name = f"{row['measure_id']} - {row['measure_name']} ({row['gap_severity']}, {row['gap_pct']}% gap)"
        measure_options[display_name] = row['measure_id']
    
    # Measure selection
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_display = st.selectbox(
            "Select measure to target for outreach:",
            options=list(measure_options.keys()),
            help="Measures sorted by gap severity and size"
        )
        selected_measure_id = measure_options[selected_display]
        st.session_state.outreach_selected_measure = selected_measure_id
    
    # Get selected measure details
    selected_measure = measures_df[measures_df['measure_id'] == selected_measure_id].iloc[0]
    # Display measure metrics
    st.markdown("#### Measure Performance")
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric("Current Performance", f"{selected_measure['performance_pct']:.1f}%")
    with metric_col2:
        st.metric("Target", f"{selected_measure['target_pct']:.1f}%")
    with metric_col3:
        st.metric("Gap", f"{selected_measure['gap_pct']:.1f}%", 
                 delta=f"-{selected_measure['gap_pct']:.1f}%", delta_color="inverse")
    with metric_col4:
        severity_emoji = {"Critical": "🔴", "Moderate": "🟡", "Minor": "🟢"}
        st.metric("Severity", f"{severity_emoji.get(selected_measure['gap_severity'], '')} {selected_measure['gap_severity']}")
    
# Show eligibility note
st.info(f"ℹ️ 👥 Showing sample of eligible members for outreach (filtered by measure eligibility)")

# Filters section
st.markdown("---")
st.markdown("### 🔍 Step 2: Apply Filters (Optional)")

with st.expander("Advanced Filters", expanded=False):
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        age_range = st.slider(
            "Age Range",
            min_value=18,
            max_value=95,
            value=(50, 85),
            help="Filter members by age"
        )
        
        risk_score_range = st.slider(
            "Risk Score Range",
            min_value=0.5,
            max_value=5.0,
            value=(1.5, 5.0),
            step=0.1,
            help="HCC-based risk score"
        )
    
    with filter_col2:
        selected_states = st.multiselect(
            "States (optional)",
            options=["CA", "FL", "TX", "NY", "PA", "OH", "IL", "AZ"],
            default=None,
            help="Filter by member state"
        )
        
        selected_plan_types = st.multiselect(
            "Plan Type (optional)",
            options=["HMO", "PPO", "SNP", "PFFS", "MSA"],
            default=None,
            help="Filter by plan type"
        )
    
    with filter_col3:
        min_conditions = st.number_input(
            "Min. Chronic Conditions",
            min_value=0,
            max_value=10,
            value=2,
            help="Minimum number of chronic conditions"
        )

# Load members button
if st.button("🔍 Load Member List", type="primary", use_container_width=True):
    with st.spinner("Loading members..."):
        # Build WHERE clause with filters
        where_conditions = [
            "m.star_eligible = true",
            "m.enrollment_status = 'Active'",
            f"m.age BETWEEN {age_range[0]} AND {age_range[1]}",
            f"m.risk_score BETWEEN {risk_score_range[0]} AND {risk_score_range[1]}",
            f"m.num_conditions >= {min_conditions}"
        ]
        
        # Add state filter
        if selected_states:
            states_str = "', '".join(selected_states)
            where_conditions.append(f"m.state IN ('{states_str}')")
        
        # Add plan type filter
        if selected_plan_types:
            plans_str = "', '".join(selected_plan_types)
            where_conditions.append(f"m.plan_type IN ('{plans_str}')")
        
        where_clause = " AND ".join(where_conditions)
        
        # Query members
        members_query = f"""
        SELECT 
            m.member_id,
            m.age,
            m.gender,
            m.state,
            m.plan_type,
            m.conditions,
            m.num_conditions,
            ROUND(m.risk_score, 2) as risk_score
        FROM {CATALOG}.{SCHEMA}.member_enrollments m
        WHERE {where_clause}
        ORDER BY m.risk_score DESC, m.num_conditions DESC
        LIMIT 200
        """
        
        members_result_df = execute_query(members_query)
        
        if members_result_df is not None:
            st.session_state.outreach_members_df = members_result_df
            st.success(f"✅ Loaded {len(members_result_df):,} members for outreach")
        else:
            st.error("Failed to load members")
    
    # Display results
    if st.session_state.outreach_members_df is not None:
        members_df_display = st.session_state.outreach_members_df
        
        st.markdown("---")
        st.markdown("### 📋 Step 3: Review Member List")
        
        # Summary metrics
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
        
        with summary_col1:
            st.metric("Total Members", f"{len(members_df_display):,}")
        with summary_col2:
            avg_risk = members_df_display['risk_score'].mean()
            st.metric("Avg Risk Score", f"{avg_risk:.2f}")
        with summary_col3:
            avg_conditions = members_df_display['num_conditions'].mean()
            st.metric("Avg Conditions", f"{avg_conditions:.1f}")
        with summary_col4:
            eligible = selected_measure['eligible_members']
            pct_eligible = (len(members_df_display) / eligible * 100) if eligible > 0 else 0
            st.metric("% of Eligible", f"{pct_eligible:.1f}%")
    
    # Display table
    st.markdown("#### Member Details")
    
    # Format display DataFrame
    display_df = members_df_display.copy()
    display_df['conditions'] = display_df['conditions'].apply(lambda x: ', '.join(x) if isinstance(x, list) else str(x))
    
    # Display with column config
    st.dataframe(
        display_df[[
            'member_id', 'age', 'gender', 'state', 'plan_type',
            'num_conditions', 'risk_score', 'conditions'
        ]],
        use_container_width=True,
        height=400,
        column_config={
            'member_id': 'Member ID',
            'age': 'Age',
            'gender': 'Gender',
            'state': 'State',
            'plan_type': 'Plan',
            'num_conditions': '# Conditions',
            'risk_score': 'Risk Score',
            'conditions': 'Chronic Conditions'
        }
    )
    
    # Export section
    st.markdown("---")
    st.markdown("### 📥 Step 4: Export Member List")
    
    export_col1, export_col2 = st.columns([3, 1])
    
    with export_col1:
        st.info(f"""
        **Export Details:**
        - Total members: {len(members_df_display):,}
        - Measure: {selected_measure['measure_name']}
        - Gap Severity: {selected_measure['gap_severity']}
        - Format: CSV (comma-separated values)
        """)
    
    with export_col2:
        # Generate CSV
        csv_data = members_df_display.to_csv(index=False)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"member_outreach_{selected_measure_id}_{timestamp}.csv"
        
        st.download_button(
            label="⬇️ Download CSV",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            type="primary",
            use_container_width=True
        )
    
    # Outreach recommendations
    with st.expander("💡 Outreach Recommendations"):
        st.markdown(f"""
        **Recommended Outreach Strategy for {selected_measure['measure_name']}:**
        
        1. **Prioritization**
           - Start with high-risk members (risk score > 3.0)
           - Focus on members with multiple chronic conditions
           - Target members in states with highest gaps
        
        2. **Outreach Methods**
           - Phone calls for high-risk members
           - Text messages for appointment reminders
           - Mailings for education materials
           - Care manager home visits for complex cases
        
        3. **Success Metrics**
           - Response rate target: 60%
           - Completion rate target: 40%
           - Gap closure target: {selected_measure['gap_pct']:.1f} percentage points
        
        4. **Timeline**
           - Week 1-2: Initial outreach and scheduling
           - Week 3-6: Appointments and interventions
           - Week 7-8: Follow-up and documentation
        
        5. **Resources Needed**
           - Care managers: {max(1, len(members_df_display) // 100)} FTE
           - Budget estimate: ${len(members_df_display) * 50:,.0f} (at $50/member)
        """)

# Help section
st.markdown("---")
with st.expander("ℹ️ How to Use This Page"):
    st.markdown("""
    **Member Outreach Portal User Guide:**
    
    1. **Select Measure**: Choose a HEDIS measure that has a performance gap
       - Measures are sorted by gap severity (Critical → Moderate → Minor)
       - Review the measure's current performance, target, and gap size
    
    2. **Apply Filters** (Optional): Narrow down your outreach list
       - Age and risk score ranges to focus on specific populations
       - Geographic filters (state) for regional campaigns
       - Chronic condition filters for targeted interventions
    
    3. **Load Member List**: Click to generate the member list
       - Shows up to 1,000 members (sorted by risk score)
       - Displays demographics and clinical characteristics
       - Includes gap severity for context
    
    4. **Export to CSV**: Download the member list
       - Use for mail merge, phone dialer, or care management system import
       - Contains all member details for outreach tracking
       - Filename includes measure ID and timestamp
    
    **Best Practices:**
    - Start with Critical gaps for highest impact
    - Use filters to create focused, manageable outreach lists
    - Prioritize high-risk members first
    - Track outreach outcomes to measure program effectiveness
    
    **Data Notes:**
    - Sample data generated for demonstration purposes
    - Measure-specific eligibility filters applied automatically (e.g., women 50-74 for BCS, diabetics for CDC)
    - In production, this would query actual member gap data from claims/clinical systems
    - Filters help create focused, targeted outreach campaigns
    """)

st.markdown("---")
st.caption("⭐ CMS Star Ratings Analytics | Member Outreach Portal")
