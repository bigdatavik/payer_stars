# Databricks notebook source
# MAGIC %md
# MAGIC # Generate HEDIS Measures Data
# MAGIC
# MAGIC Generates realistic synthetic HEDIS measure data for CMS Star Ratings.
# MAGIC All configuration from config.yaml via shared.config module.

# COMMAND ----------

# Ensure Environment widget exists (use current value so job-injected value is preserved)
try:
    _current = dbutils.widgets.get("environment")
except Exception:
    _current = "dev"
dbutils.widgets.dropdown("environment", _current, ["dev", "staging", "prod"], "Environment")
print(f"Environment: {_current} (change the dropdown if needed, then re-run the next cell)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Import Configuration

# COMMAND ----------

import sys
import os
sys.path.append(os.path.abspath('..'))
from shared.config import get_config, print_config

env_from_widget = dbutils.widgets.get("environment")
cfg = get_config(environment=env_from_widget)
print_config(cfg)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate HEDIS Measures Data

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import *
import random
from datetime import datetime

# HEDIS Measures for Medicare Advantage CMS Star Ratings
# Focuses on measures relevant to seniors (65+) with CMS 2026 weights
HEDIS_MEASURES = {
    # Effectiveness of Care - Screening (Weight: 1x)
    "BCS": {"name": "Breast Cancer Screening", "domain": "Effectiveness of Care", "weight": 1, "star_category": "Preventive"},
    "COL": {"name": "Colorectal Cancer Screening", "domain": "Effectiveness of Care", "weight": 1, "star_category": "Preventive"},
    
    # Effectiveness of Care - Diabetes (Weight: 3x - Outcomes)
    "CDC": {"name": "Comprehensive Diabetes Care", "domain": "Effectiveness of Care", "weight": 3, "star_category": "Outcomes"},
    "HBD": {"name": "Hemoglobin A1c Control for Diabetes", "domain": "Effectiveness of Care", "weight": 3, "star_category": "Outcomes"},
    "KED": {"name": "Kidney Health Evaluation for Diabetes", "domain": "Effectiveness of Care", "weight": 3, "star_category": "Outcomes"},
    "EED": {"name": "Eye Exam for Diabetes", "domain": "Effectiveness of Care", "weight": 3, "star_category": "Outcomes"},
    
    # Effectiveness of Care - Cardiovascular (Weight: 3x - Outcomes)
    "CBP": {"name": "Controlling High Blood Pressure", "domain": "Effectiveness of Care", "weight": 3, "star_category": "Outcomes"},
    "PBH": {"name": "Persistence of Beta-Blocker Treatment", "domain": "Effectiveness of Care", "weight": 3, "star_category": "Outcomes"},
    "SPC": {"name": "Statin Therapy for Cardiovascular Disease", "domain": "Effectiveness of Care", "weight": 3, "star_category": "Outcomes"},
    
    # Effectiveness of Care - Respiratory (Weight: 3x - Outcomes)
    "AMR": {"name": "Asthma Medication Ratio", "domain": "Effectiveness of Care", "weight": 3, "star_category": "Outcomes"},
    "PCE": {"name": "Pharmacotherapy for COPD Exacerbation", "domain": "Effectiveness of Care", "weight": 3, "star_category": "Outcomes"},
    
    # Intermediate Outcomes (Weight: 3x)
    "HBD_2": {"name": "HbA1c Poor Control (>9%)", "domain": "Intermediate Outcomes", "weight": 3, "star_category": "Outcomes"},
    "CBP_2": {"name": "Blood Pressure Control (<140/90)", "domain": "Intermediate Outcomes", "weight": 3, "star_category": "Outcomes"},
    
    # Access/Availability of Care (Weight: 2x)
    "AAP": {"name": "Adults Access to Preventive Care", "domain": "Access/Availability", "weight": 2, "star_category": "Access"},
    "AWC": {"name": "Annual Wellness Visit", "domain": "Access/Availability", "weight": 2, "star_category": "Access"},
    
    # Experience of Care - CAHPS (Weight: 2x)
    "GRS": {"name": "Getting Needed Care", "domain": "Experience of Care", "weight": 2, "star_category": "Experience"},
    "GAC": {"name": "Getting Appointments and Care Quickly", "domain": "Experience of Care", "weight": 2, "star_category": "Experience"},
    "CCC": {"name": "Customer Service", "domain": "Experience of Care", "weight": 2, "star_category": "Experience"},
    "OHP": {"name": "Overall Rating of Health Plan", "domain": "Experience of Care", "weight": 2, "star_category": "Experience"},
    "OHC": {"name": "Overall Rating of Healthcare", "domain": "Experience of Care", "weight": 2, "star_category": "Experience"},
    "CTM": {"name": "Care Coordination", "domain": "Experience of Care", "weight": 2, "star_category": "Experience"},
    
    # Health Plan Descriptive Information (Weight: 3x - Outcomes)
    "MRP": {"name": "Medication Reconciliation Post-Discharge", "domain": "Descriptive", "weight": 3, "star_category": "Outcomes"},
    "PCR": {"name": "Plan All-Cause Readmissions", "domain": "Descriptive", "weight": 3, "star_category": "Outcomes"},
    "FUA": {"name": "Follow-Up After Hospitalization", "domain": "Descriptive", "weight": 3, "star_category": "Outcomes"},
    
    # Medicare Part D Measures (Weight: 3x - Outcomes - CRITICAL FOR MA PLANS)
    "MPM": {"name": "Medication Adherence for Diabetes (Part D)", "domain": "Part D", "weight": 3, "star_category": "Outcomes"},
    "MPA": {"name": "Medication Adherence for Hypertension (Part D)", "domain": "Part D", "weight": 3, "star_category": "Outcomes"},
    "MPC": {"name": "Medication Adherence for Cholesterol (Part D)", "domain": "Part D", "weight": 3, "star_category": "Outcomes"},
    "SMD": {"name": "Statin Use in Diabetes (Part D)", "domain": "Part D", "weight": 3, "star_category": "Outcomes"},
    "SPD": {"name": "Statin Use in CVD (Part D)", "domain": "Part D", "weight": 3, "star_category": "Outcomes"},
    "DRR": {"name": "Drug-Drug Interaction Risk (Part D)", "domain": "Part D", "weight": 3, "star_category": "Outcomes"},
    "HRM": {"name": "High-Risk Medication Use in Elderly (Part D)", "domain": "Part D", "weight": 3, "star_category": "Outcomes"},
    
    # Additional Medicare-Specific Quality Measures (Weight: 3x - Outcomes)
    "OMW": {"name": "Osteoporosis Management in Women", "domain": "Effectiveness of Care", "weight": 3, "star_category": "Outcomes"},
    "FUM": {"name": "Follow-Up After ED Visit for Mental Health", "domain": "Effectiveness of Care", "weight": 3, "star_category": "Outcomes"},
    "FUI": {"name": "Follow-Up After ED Visit for Substance Abuse", "domain": "Effectiveness of Care", "weight": 3, "star_category": "Outcomes"},
    "AMM": {"name": "Antidepressant Medication Management", "domain": "Effectiveness of Care", "weight": 3, "star_category": "Outcomes"},
    "SMC": {"name": "Statin Medication Compliance", "domain": "Effectiveness of Care", "weight": 3, "star_category": "Outcomes"},
    "SSD": {"name": "Diabetes Screening for Schizophrenia", "domain": "Effectiveness of Care", "weight": 3, "star_category": "Outcomes"},
    
    # Preventive Care for Seniors (Weight: 1x)
    "FVA": {"name": "Flu Vaccinations for Adults 65+", "domain": "Preventive", "weight": 1, "star_category": "Preventive"},
    "PVA": {"name": "Pneumonia Vaccinations for Adults 65+", "domain": "Preventive", "weight": 1, "star_category": "Preventive"},
    "GSV": {"name": "Shingles Vaccination for Adults 65+", "domain": "Preventive", "weight": 1, "star_category": "Preventive"},
    
    # Care Coordination (Weight: 2x)
    "TRC": {"name": "Transitions of Care", "domain": "Care Coordination", "weight": 2, "star_category": "Access"}
}

print(f"✅ Defined {len(HEDIS_MEASURES)} HEDIS measures")

# Generate measure performance data
def generate_measure_performance(measure_id, measure_info):
    """Generate realistic performance data for a HEDIS measure"""
    
    # Generate performance rate (40-95% range, varies by measure type)
    if "Screening" in measure_info["name"]:
        # Screening measures typically 50-80%
        performance_rate = random.uniform(0.50, 0.80)
        target = random.uniform(0.70, 0.85)
    elif "Diabetes" in measure_info["name"] or "Cardiovascular" in measure_info["domain"]:
        # Clinical measures typically 60-85%
        performance_rate = random.uniform(0.60, 0.85)
        target = random.uniform(0.75, 0.90)
    elif "Experience" in measure_info["domain"]:
        # CAHPS measures typically 70-90%
        performance_rate = random.uniform(0.70, 0.90)
        target = random.uniform(0.80, 0.92)
    elif "Part D" in measure_info["domain"]:
        # Medication adherence typically 65-85%
        performance_rate = random.uniform(0.65, 0.85)
        target = random.uniform(0.75, 0.88)
    else:
        # Other measures
        performance_rate = random.uniform(0.55, 0.85)
        target = random.uniform(0.70, 0.88)
    
    # Calculate gap
    gap = max(0, target - performance_rate)
    
    # Determine gap severity
    if gap >= 0.15:
        gap_severity = "Critical"
    elif gap >= 0.08:
        gap_severity = "Moderate"
    elif gap >= 0.03:
        gap_severity = "Minor"
    else:
        gap_severity = "None"
    
    # Generate member counts (realistic for Medicare Advantage plans)
    denominator = random.randint(5000, 50000)
    numerator = int(denominator * performance_rate)
    
    # Calculate star rating impact (1-5 stars)
    if performance_rate >= 0.85:
        star_rating = 5.0
    elif performance_rate >= 0.75:
        star_rating = 4.0
    elif performance_rate >= 0.65:
        star_rating = 3.0
    elif performance_rate >= 0.55:
        star_rating = 2.0
    else:
        star_rating = 1.0
    
    # Add some randomness to star rating
    star_rating += random.uniform(-0.3, 0.3)
    star_rating = max(1.0, min(5.0, star_rating))
    
    return {
        "measure_id": measure_id,
        "measure_name": measure_info["name"],
        "domain": measure_info["domain"],
        "weight": measure_info["weight"],
        "star_category": measure_info["star_category"],
        "performance_rate": round(performance_rate, 4),
        "target_benchmark": round(target, 4),
        "gap": round(gap, 4),
        "gap_severity": gap_severity,
        "numerator": numerator,
        "denominator": denominator,
        "member_count": denominator,
        "star_rating": round(star_rating, 2),
        "weighted_score": round(star_rating * measure_info["weight"], 2),
        "measurement_year": 2024,
        "plan_id": "H1234-001",  # Sample Medicare Advantage plan ID
        "last_updated": datetime.now()
    }

print(f"Generating performance data for {len(HEDIS_MEASURES)} measures...")

# Generate all measures
measures_data = []
for measure_id, measure_info in HEDIS_MEASURES.items():
    measures_data.append(generate_measure_performance(measure_id, measure_info))

print(f"✅ Generated {len(measures_data)} measure records")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create DataFrame and Table

# COMMAND ----------

# Define schema
schema = StructType([
    StructField("measure_id", StringType(), False),
    StructField("measure_name", StringType(), False),
    StructField("domain", StringType(), False),
    StructField("weight", IntegerType(), False),
    StructField("star_category", StringType(), False),
    StructField("performance_rate", DoubleType(), False),
    StructField("target_benchmark", DoubleType(), False),
    StructField("gap", DoubleType(), False),
    StructField("gap_severity", StringType(), False),
    StructField("numerator", IntegerType(), False),
    StructField("denominator", IntegerType(), False),
    StructField("member_count", IntegerType(), False),
    StructField("star_rating", DoubleType(), False),
    StructField("weighted_score", DoubleType(), False),
    StructField("measurement_year", IntegerType(), False),
    StructField("plan_id", StringType(), False),
    StructField("last_updated", TimestampType(), False)
])

# Create DataFrame
measures_df = spark.createDataFrame(measures_data, schema=schema)

# Write to Delta table
measures_df.write.mode("overwrite").saveAsTable(cfg.measures_table)

print(f"✅ Created table: {cfg.measures_table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Data

# COMMAND ----------

# Show statistics
print("=" * 80)
print("HEDIS MEASURES DATA STATISTICS")
print("=" * 80)

stats = spark.sql(f"""
SELECT 
    COUNT(*) as total_measures,
    COUNT(DISTINCT domain) as domains,
    SUM(CASE WHEN gap_severity = 'Critical' THEN 1 ELSE 0 END) as critical_gaps,
    SUM(CASE WHEN gap_severity = 'Moderate' THEN 1 ELSE 0 END) as moderate_gaps,
    SUM(CASE WHEN gap_severity = 'Minor' THEN 1 ELSE 0 END) as minor_gaps,
    ROUND(AVG(performance_rate), 3) as avg_performance,
    ROUND(AVG(target_benchmark), 3) as avg_target,
    ROUND(AVG(gap), 3) as avg_gap,
    ROUND(AVG(star_rating), 2) as avg_star_rating
FROM {cfg.measures_table}
""").collect()[0]

print(f"Total Measures:       {stats['total_measures']}")
print(f"Domains:              {stats['domains']}")
print(f"Critical Gaps:        {stats['critical_gaps']}")
print(f"Moderate Gaps:        {stats['moderate_gaps']}")
print(f"Minor Gaps:           {stats['minor_gaps']}")
print(f"Avg Performance:      {stats['avg_performance']:.1%}")
print(f"Avg Target:           {stats['avg_target']:.1%}")
print(f"Avg Gap:              {stats['avg_gap']:.1%}")
print(f"Avg Star Rating:      {stats['avg_star_rating']:.2f}/5.0")
print("=" * 80)

# Show measures by domain
print("\nMeasures by domain:")
spark.sql(f"""
SELECT 
    domain,
    COUNT(*) as measure_count,
    ROUND(AVG(performance_rate), 3) as avg_performance,
    ROUND(AVG(gap), 3) as avg_gap,
    ROUND(AVG(star_rating), 2) as avg_star_rating
FROM {cfg.measures_table}
GROUP BY domain
ORDER BY measure_count DESC
""").show()

# Show critical gap measures
print("\nMeasures with critical gaps:")
spark.sql(f"""
SELECT measure_id, measure_name, domain, 
       performance_rate, target_benchmark, gap, star_rating
FROM {cfg.measures_table}
WHERE gap_severity = 'Critical'
ORDER BY gap DESC
LIMIT 10
""").show()

# COMMAND ----------

print("=" * 80)
print("DATA GENERATION COMPLETE!")
print("=" * 80)
print(f"✅ Table created: {cfg.measures_table}")
print(f"✅ Total measures: {len(HEDIS_MEASURES)}")
print(f"✅ Domains: {len(set(m['domain'] for m in HEDIS_MEASURES.values()))}")
print("=" * 80)
