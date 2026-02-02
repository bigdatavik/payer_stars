"""
Star Ratings Calculator
Interactive calculator for CMS Star Ratings with weighted scoring and what-if scenarios
"""

import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

st.title("🌟 Star Ratings Calculator")

st.markdown("""
Calculate your plan's overall CMS Star Rating using the official weighted methodology.
Model "what-if" scenarios to see how improving specific measures impacts your rating.
""")

# Configuration
CATALOG = os.getenv("CATALOG_NAME", "payer_stars_dev")
SCHEMA = os.getenv("SCHEMA_NAME", "star_ratings")
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "148ccb90800933a1")

st.markdown("---")

# CMS Cut Points for Star Ratings (2026 methodology)
st.markdown("### 📐 CMS Star Rating Cut Points")

col1, col2 = st.columns(2)

with col1:
    st.info("""
    **Overall Star Rating Thresholds:**
    - ⭐⭐⭐⭐⭐ 5 Stars: ≥4.25
    - ⭐⭐⭐⭐ 4 Stars: 3.75 - 4.24
    - ⭐⭐⭐ 3 Stars: 3.25 - 3.74
    - ⭐⭐ 2 Stars: 2.75 - 3.24
    - ⭐ 1 Star: <2.75
    """)

with col2:
    st.info("""
    **CMS 2026 Measure Weights:**
    - 🎯 **Outcomes Measures**: 3x weight
    - 👥 **Experience/Access**: 2x weight
    - 🛡️ **Preventive Care**: 1x weight
    """)

# Methodology Explainer
with st.expander("📖 How Are Star Ratings Calculated? (Click to Learn)", expanded=False):
    st.markdown("""
    ### CMS Star Ratings Calculation Methodology
    
    The overall star rating is calculated using a **weighted average** of all individual measure performances.
    
    #### Step-by-Step Process:
    
    **1️⃣ Each Measure Gets a Star Rating (1-5)**
    
    Individual HEDIS measures receive stars based on performance thresholds set by CMS.
    
    **2️⃣ Apply Category Weights**
    
    CMS assigns different weights to emphasize clinical outcomes:
    - **Outcomes/Part D measures**: 3x weight (highest priority)
    - **Experience/Access measures**: 2x weight (medium priority)
    - **Preventive measures**: 1x weight (baseline)
    
    **3️⃣ Calculate Weighted Average**
    
    ```
    Overall Rating = Σ(Measure Stars × Weight) / Σ(Total Weights)
    ```
    
    **4️⃣ Convert to Star Tier**
    
    The decimal rating is mapped to a tier (1-5 stars) using CMS cut points.
    
    ---
    
    ### 📝 Example Calculation:
    
    Let's say you have 3 measures:
    
    | Measure | Stars | Weight | Weighted Score |
    |---------|-------|--------|----------------|
    | Diabetes Control (Outcome) | 3.5 | 3x | 3.5 × 3 = **10.5** |
    | Member Experience | 4.0 | 2x | 4.0 × 2 = **8.0** |
    | Flu Vaccination (Preventive) | 4.5 | 1x | 4.5 × 1 = **4.5** |
    
    **Calculation:**
    ```
    Total Weighted Score = 10.5 + 8.0 + 4.5 = 23.0
    Total Weight = 3 + 2 + 1 = 6
    Overall Rating = 23.0 ÷ 6 = 3.83 ⭐⭐⭐⭐ (4 Stars)
    ```
    
    ---
    
    ### 💡 Why Weights Matter:
    
    **Impact of 0.5 Star Improvement:**
    - Improving a **3x weighted** measure by 0.5 stars → **+0.5 × 3 = +1.5** to weighted score
    - Improving a **1x weighted** measure by 0.5 stars → **+0.5 × 1 = +0.5** to weighted score
    
    **Bottom Line:** Focusing on high-weight measures (Outcomes, Part D) provides **3x more impact** on your overall rating!
    
    ---
    
    ### 💰 Financial Impact:
    
    - **5 Stars (≥4.25)**: Enhanced Quality Bonus Payments + Member growth
    - **4 Stars (3.75-4.24)**: Quality Bonus Payments
    - **3 Stars or below**: No bonus payments, risk of losing members
    
    Even a **0.1 point improvement** near the 4.25 threshold can mean **millions in bonus revenue**!
    """)

st.markdown("---")

# Current Performance
st.markdown("### 📊 Current Star Rating Calculation")

# Sample data - in production this would come from the database
current_measures = [
    {"measure": "MPM - Med Adherence Diabetes", "domain": "Part D", "weight": 3, "stars": 3.5},
    {"measure": "MPA - Med Adherence HTN", "domain": "Part D", "weight": 3, "stars": 4.0},
    {"measure": "MPC - Med Adherence Cholesterol", "domain": "Part D", "weight": 3, "stars": 3.8},
    {"measure": "HRM - High-Risk Medication", "domain": "Part D", "weight": 3, "stars": 4.2},
    {"measure": "PCR - Plan Readmissions", "domain": "Outcomes", "weight": 3, "stars": 3.2},
    {"measure": "CBP - Blood Pressure Control", "domain": "Outcomes", "weight": 3, "stars": 3.6},
    {"measure": "CDC - Diabetes Care", "domain": "Outcomes", "weight": 3, "stars": 3.8},
    {"measure": "KED - Kidney Health Diabetes", "domain": "Outcomes", "weight": 3, "stars": 3.7},
    {"measure": "GRS - Getting Needed Care", "domain": "Experience", "weight": 2, "stars": 4.1},
    {"measure": "GAC - Getting Appts Quickly", "domain": "Experience", "weight": 2, "stars": 3.9},
    {"measure": "OHP - Overall Health Plan", "domain": "Experience", "weight": 2, "stars": 4.0},
    {"measure": "BCS - Breast Cancer Screening", "domain": "Preventive", "weight": 1, "stars": 3.5},
    {"measure": "COL - Colorectal Screening", "domain": "Preventive", "weight": 1, "stars": 3.3},
    {"measure": "FVA - Flu Vaccination 65+", "domain": "Preventive", "weight": 1, "stars": 4.2},
]

# Calculate weighted average
total_weighted_score = sum(m["stars"] * m["weight"] for m in current_measures)
total_weight = sum(m["weight"] for m in current_measures)
overall_rating = round(total_weighted_score / total_weight, 2)

# Display current rating
col1, col2, col3 = st.columns([2, 2, 2])

with col1:
    st.metric("Current Overall Star Rating", f"{overall_rating} ⭐", 
              delta=None, delta_color="off")

with col2:
    if overall_rating >= 4.25:
        rating_label = "5 Stars 🌟"
        color = "green"
    elif overall_rating >= 3.75:
        rating_label = "4 Stars ⭐"
        color = "normal"
    elif overall_rating >= 3.25:
        rating_label = "3 Stars"
        color = "normal"
    elif overall_rating >= 2.75:
        rating_label = "2 Stars"
        color = "normal"
    else:
        rating_label = "1 Star"
        color = "normal"
    
    st.metric("Rating Tier", rating_label)

with col3:
    gap_to_next = 4.25 - overall_rating if overall_rating < 4.25 else 0
    st.metric("Gap to 5 Stars", f"{gap_to_next:.2f} points")

# Show breakdown by category
st.markdown("### 📋 Rating Breakdown by Category")

df = pd.DataFrame(current_measures)

# Group by domain and calculate weighted averages
domain_stats = df.groupby('domain').agg({
    'stars': lambda x: round(sum(x * df.loc[x.index, 'weight']) / sum(df.loc[x.index, 'weight']), 2),
    'weight': 'first'
}).reset_index()
domain_stats.columns = ['Category', 'Avg Stars', 'Weight']

# Sort by weight descending
domain_stats = domain_stats.sort_values('Weight', ascending=False)

col1, col2, col3, col4 = st.columns(4)

for i, row in domain_stats.iterrows():
    with [col1, col2, col3, col4][i]:
        st.metric(
            row['Category'],
            f"{row['Avg Stars']} ⭐",
            delta=f"Weight: {row['Weight']}x"
        )

# Detailed measure table
st.markdown("### 📊 Detailed Measure Performance")

df_display = df.copy()
df_display['Weighted Score'] = df_display['stars'] * df_display['weight']
df_display = df_display.sort_values('Weighted Score', ascending=True)

st.dataframe(
    df_display[['measure', 'domain', 'weight', 'stars', 'Weighted Score']].rename(columns={
        'measure': 'Measure',
        'domain': 'Category',
        'weight': 'Weight',
        'stars': 'Star Rating'
    }),
    use_container_width=True,
    height=400
)

st.markdown("---")

# What-If Scenario Builder
st.markdown("### 🔮 What-If Scenario Builder")

st.markdown("""
Model the impact of improving specific measures on your overall star rating.
Simulate targeted improvement initiatives to see which measures provide the best ROI.
""")

col1, col2 = st.columns(2)

with col1:
    selected_measure = st.selectbox(
        "Select measure to improve:",
        [m["measure"] for m in current_measures],
        key="scenario_measure"
    )
    
    current_star = next(m["stars"] for m in current_measures if m["measure"] == selected_measure)
    st.metric("Current Stars", f"{current_star} ⭐")

with col2:
    target_star = st.slider(
        "Target star rating for this measure:",
        min_value=1.0,
        max_value=5.0,
        value=min(current_star + 0.5, 5.0),
        step=0.1,
        key="target_stars"
    )
    
    improvement = target_star - current_star
    st.metric("Improvement", f"+{improvement:.1f} stars", delta_color="normal")

# Calculate projected overall rating
if st.button("📊 Calculate Impact", type="primary"):
    # Update the measure with new star rating
    scenario_measures = current_measures.copy()
    for m in scenario_measures:
        if m["measure"] == selected_measure:
            m["stars"] = target_star
    
    # Recalculate weighted average
    scenario_weighted_score = sum(m["stars"] * m["weight"] for m in scenario_measures)
    scenario_rating = round(scenario_weighted_score / total_weight, 2)
    
    overall_improvement = scenario_rating - overall_rating
    
    st.markdown("### 📈 Projected Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Projected Overall Rating", f"{scenario_rating} ⭐", 
                  delta=f"+{overall_improvement:.2f}", delta_color="normal")
    
    with col2:
        new_gap = max(0, 4.25 - scenario_rating)
        gap_closed = gap_to_next - new_gap
        st.metric("Gap Closed to 5 Stars", f"{gap_closed:.2f} points")
    
    with col3:
        # Get measure weight
        measure_weight = next(m["weight"] for m in current_measures if m["measure"] == selected_measure)
        roi = overall_improvement / improvement if improvement > 0 else 0
        st.metric("ROI Multiplier", f"{measure_weight}x", 
                  help="Due to CMS weighting, improvements in this measure have 3x impact")
    
    # Show recommendation
    if overall_improvement >= 0.15:
        st.success(f"""
        ✅ **High Impact Opportunity!** 
        
        Improving {selected_measure} by {improvement:.1f} stars would boost your overall rating by {overall_improvement:.2f} points.
        This is a {measure_weight}x weighted measure, making it a high-priority target.
        """)
    elif overall_improvement >= 0.05:
        st.info(f"""
        💡 **Moderate Impact**
        
        This improvement would increase overall rating by {overall_improvement:.2f} points.
        Consider if this measure is easier to improve than other high-weight measures.
        """)
    else:
        st.warning(f"""
        ⚠️ **Limited Impact**
        
        This improvement would only increase overall rating by {overall_improvement:.2f} points.
        Focus on 3x weighted measures (Outcomes, Part D) for maximum impact.
        """)

st.markdown("---")

# Best opportunities
st.markdown("### 🎯 Highest Impact Opportunities")

st.markdown("""
Based on current performance, these measures offer the best opportunity for star rating improvement:
""")

# Calculate potential impact (measures with low stars but high weight)
opportunities = []
for m in current_measures:
    potential_gain = (5.0 - m["stars"]) * m["weight"]  # If we got to 5 stars
    impact_per_point = m["weight"] / total_weight
    opportunities.append({
        "Measure": m["measure"],
        "Current Stars": m["stars"],
        "Weight": m["weight"],
        "Max Potential Gain": round(potential_gain, 2),
        "Impact Per Point": round(impact_per_point, 3)
    })

opp_df = pd.DataFrame(opportunities).sort_values("Max Potential Gain", ascending=False).head(10)

st.dataframe(opp_df, use_container_width=True, hide_index=True)

st.markdown("---")

# Educational content
with st.expander("📚 Learn More About CMS Star Ratings Methodology"):
    st.markdown("""
    ### CMS Star Ratings Calculation
    
    **Weighted Average Formula:**
    ```
    Overall Rating = Σ(Measure Stars × Weight) / Σ(Weight)
    ```
    
    **Key Components:**
    1. **Individual Measure Stars**: Each HEDIS measure receives 1-5 stars based on performance thresholds
    2. **Category Weights**: CMS assigns different weights based on measure importance
       - Outcomes measures (diabetes, CVD, readmissions): 3x weight
       - Experience/Access measures (CAHPS, access): 2x weight  
       - Preventive measures (screenings, vaccinations): 1x weight
    3. **Cut Points**: Overall rating converted to star tier using fixed thresholds
    
    **Why This Matters:**
    - **5-Star Bonus**: Plans with 5 stars get enhanced rebate payments from CMS
    - **Member Growth**: Higher ratings improve member retention and acquisition
    - **Provider Networks**: Star ratings influence provider participation
    - **Quality Bonus Program**: Additional payments for 4+ star plans
    
    **Strategy Implications:**
    - Prioritize 3x weighted measures (outcomes, Part D adherence)
    - Small improvements in high-weight measures = big rating gains
    - Must balance member experience (2x) with clinical outcomes (3x)
    - Preventive measures matter but have less direct impact
    """)

st.markdown("---")
st.caption("🌟 CMS Star Ratings Calculator | Based on 2026 CMS methodology")
