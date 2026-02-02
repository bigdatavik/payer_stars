"""
Member Outreach Page - Care Manager Portal
Identify and export members with HEDIS gaps for targeted outreach campaigns
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
import random

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

# Initialize session state
if 'outreach_selected_measure' not in st.session_state:
    st.session_state.outreach_selected_measure = None
if 'outreach_members_df' not in st.session_state:
    st.session_state.outreach_members_df = None

# Static measure data (like other pages)
MEASURES_DATA = {
    "BCS - Breast Cancer Screening": {
        "measure_id": "BCS",
        "gap_severity": "Critical",
        "gap_pct": 13.0,
        "performance_pct": 62.0,
        "target_pct": 75.0,
        "eligible_members": 10000,
        "domain": "Preventive",
        "weight": 1,
        "eligibility": "Women aged 50-74"
    },
    "CDC - Comprehensive Diabetes Care": {
        "measure_id": "CDC",
        "gap_severity": "Moderate",
        "gap_pct": 12.0,
        "performance_pct": 68.0,
        "target_pct": 80.0,
        "eligible_members": 15000,
        "domain": "Outcomes",
        "weight": 3,
        "eligibility": "Members with Diabetes Type 2"
    },
    "CBP - Controlling High Blood Pressure": {
        "measure_id": "CBP",
        "gap_severity": "Critical",
        "gap_pct": 13.0,
        "performance_pct": 65.0,
        "target_pct": 78.0,
        "eligible_members": 20000,
        "domain": "Outcomes",
        "weight": 3,
        "eligibility": "Members with Hypertension"
    },
    "MPM - Medication Adherence for Diabetes": {
        "measure_id": "MPM",
        "gap_severity": "Moderate",
        "gap_pct": 10.0,
        "performance_pct": 72.0,
        "target_pct": 82.0,
        "eligible_members": 12000,
        "domain": "Part D",
        "weight": 3,
        "eligibility": "Members with Diabetes Type 2"
    },
    "COL - Colorectal Cancer Screening": {
        "measure_id": "COL",
        "gap_severity": "Moderate",
        "gap_pct": 9.0,
        "performance_pct": 66.0,
        "target_pct": 75.0,
        "eligible_members": 18000,
        "domain": "Preventive",
        "weight": 1,
        "eligibility": "Adults aged 50-75"
    }
}

# Generate sample member data
def generate_sample_members(measure_id, num_members=100):
    """Generate realistic sample member data for demo"""
    random.seed(42)  # Consistent data
    
    members = []
    for i in range(num_members):
        # Base demographics
        age = random.randint(50, 85)
        gender = random.choice(['M', 'F'])
        state = random.choice(['CA', 'FL', 'TX', 'NY', 'PA', 'OH', 'IL', 'AZ'])
        plan_type = random.choice(['HMO', 'PPO', 'SNP'])
        
        # Chronic conditions
        all_conditions = ['Diabetes Type 2', 'Hypertension', 'Hyperlipidemia', 
                         'COPD', 'Asthma', 'Coronary Artery Disease']
        num_conditions = random.randint(1, 4)
        conditions = random.sample(all_conditions, num_conditions)
        
        # Apply measure-specific eligibility
        if measure_id == 'BCS':
            gender = 'F'
            age = random.randint(50, 74)
        elif measure_id in ['CDC', 'MPM']:
            if 'Diabetes Type 2' not in conditions:
                conditions.append('Diabetes Type 2')
                num_conditions = len(conditions)
        elif measure_id == 'CBP':
            if 'Hypertension' not in conditions:
                conditions.append('Hypertension')
                num_conditions = len(conditions)
        elif measure_id == 'COL':
            age = random.randint(50, 75)
        
        risk_score = round(1.0 + (age - 50)/30 + num_conditions * 0.3 + random.uniform(-0.2, 0.3), 2)
        
        members.append({
            'member_id': f'MEM-{10000 + i:05d}',
            'age': age,
            'gender': gender,
            'state': state,
            'plan_type': plan_type,
            'conditions': conditions,
            'num_conditions': num_conditions,
            'risk_score': risk_score,
            'gap_severity': random.choice(['Critical', 'Moderate', 'Minor'])
        })
    
    # Sort by risk score descending
    members.sort(key=lambda x: x['risk_score'], reverse=True)
    
    return pd.DataFrame(members)
# Measure selection
st.markdown("---")
st.markdown("### 📊 Step 1: Select HEDIS Measure")

col1, col2 = st.columns([3, 1])

with col1:
    selected_display = st.selectbox(
        "Select measure to target for outreach:",
        options=list(MEASURES_DATA.keys()),
        help="Measures with performance gaps for targeted outreach"
    )
    
selected_measure = MEASURES_DATA[selected_display]
selected_measure_id = selected_measure['measure_id']
st.session_state.outreach_selected_measure = selected_measure_id
    
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
    
# Show measure-specific eligibility info  
st.info(f"ℹ️ 👥 Eligible Population: {selected_measure['eligibility']} (automatic eligibility filter applied)")

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
            value=(65, 85),
            help="Filter members by age"
        )
        
        risk_score_range = st.slider(
            "Risk Score Range",
            min_value=0.5,
            max_value=5.0,
            value=(1.0, 5.0),
            step=0.1,
            help="HCC-based risk score"
        )
    
    with filter_col2:
        selected_states = st.multiselect(
            "States",
            options=["CA", "FL", "TX", "NY", "PA", "OH", "IL", "AZ"],
            default=None,
            help="Filter by member state"
        )
        
        selected_plan_types = st.multiselect(
            "Plan Type",
            options=["HMO", "PPO", "SNP"],
            default=None,
            help="Filter by plan type"
        )
    
    with filter_col3:
        selected_conditions = st.multiselect(
            "Chronic Conditions",
            options=["Diabetes Type 2", "Hypertension", "Hyperlipidemia", "COPD", "Asthma", "Coronary Artery Disease"],
            default=None,
            help="Members must have ALL selected conditions"
        )
        
        min_conditions = st.number_input(
            "Min. Chronic Conditions",
            min_value=0,
            max_value=10,
            value=0,
            help="Minimum number of chronic conditions"
        )

# Load members button
if st.button("🔍 Load Member List", type="primary", use_container_width=True):
    with st.spinner("Loading members..."):
        # Generate sample members for selected measure
        members_df = generate_sample_members(selected_measure_id, num_members=200)
        
        # Apply filters
        filtered_df = members_df.copy()
        
        # Age filter
        filtered_df = filtered_df[(filtered_df['age'] >= age_range[0]) & (filtered_df['age'] <= age_range[1])]
        
        # Risk score filter
        filtered_df = filtered_df[(filtered_df['risk_score'] >= risk_score_range[0]) & (filtered_df['risk_score'] <= risk_score_range[1])]
        
        # State filter
        if selected_states:
            filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]
        
        # Plan type filter
        if selected_plan_types:
            filtered_df = filtered_df[filtered_df['plan_type'].isin(selected_plan_types)]
        
        # Conditions filter
        if selected_conditions:
            for condition in selected_conditions:
                filtered_df = filtered_df[filtered_df['conditions'].apply(lambda x: condition in x)]
        
        # Min conditions filter
        filtered_df = filtered_df[filtered_df['num_conditions'] >= min_conditions]
        
        st.session_state.outreach_members_df = filtered_df
        st.success(f"✅ Loaded {len(filtered_df):,} members for outreach")
    
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
    
    # Display with default columns
    st.dataframe(
        display_df[[
            'member_id', 'age', 'gender', 'state', 'plan_type',
            'num_conditions', 'risk_score', 'gap_severity', 'conditions'
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
            'gap_severity': 'Gap',
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
