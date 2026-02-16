# Databricks notebook source
# MAGIC %md
# MAGIC # Generate Member Enrollment Data
# MAGIC
# MAGIC Generates realistic synthetic member enrollment data for Medicare Advantage plans.
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

# MAGIC %pip install pyyaml --quiet
dbutils.library.restartPython()

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
# MAGIC ## Generate Member Enrollment Data

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import *
import random
from datetime import datetime, timedelta

# Medicare Advantage member profiles
CONDITIONS = [
    "Diabetes Type 2",
    "Hypertension",
    "Hyperlipidemia",
    "COPD",
    "Asthma",
    "Coronary Artery Disease",
    "Congestive Heart Failure",
    "Chronic Kidney Disease",
    "Atrial Fibrillation",
    "Depression",
    "Osteoarthritis",
    "Osteoporosis"
]

PLAN_TYPES = [
    "HMO",
    "PPO",
    "SNP",  # Special Needs Plan
    "PFFS",  # Private Fee-for-Service
    "MSA"   # Medical Savings Account
]

def generate_member(member_id):
    """Generate a single realistic Medicare Advantage member"""
    
    # Medicare eligible (65+) or younger with disability
    if random.random() < 0.85:
        age = random.randint(65, 95)
    else:
        age = random.randint(18, 64)  # Younger with disability
    
    # Gender
    gender = random.choice(["M", "F"])
    
    # Generate 1-4 chronic conditions (typical for Medicare population)
    num_conditions = min(random.choice([0, 1, 1, 2, 2, 2, 3, 3, 4]), len(CONDITIONS))
    conditions = random.sample(CONDITIONS, num_conditions) if num_conditions > 0 else []
    
    # Plan type
    plan_type = random.choice(PLAN_TYPES)
    
    # Enrollment status
    enrollment_status = random.choices(
        ["Active", "Inactive", "Pending"],
        weights=[0.92, 0.06, 0.02]
    )[0]
    
    # Enrollment date (within last 3 years)
    days_enrolled = random.randint(30, 1095)
    enrollment_date = datetime.now() - timedelta(days=days_enrolled)
    
    # Risk score (HCC-based, higher for more conditions and older age)
    base_risk = 1.0
    age_factor = (age - 65) / 100 if age >= 65 else 0.5
    condition_factor = num_conditions * 0.3
    risk_score = max(0.5, min(5.0, base_risk + age_factor + condition_factor + random.uniform(-0.2, 0.2)))
    
    # Star ratings eligibility (most members, but not all)
    star_eligible = enrollment_status == "Active" and days_enrolled >= 180  # 6 months minimum
    
    # Location (state)
    state = random.choice([
        "CA", "FL", "TX", "NY", "PA", "OH", "IL", "MI", "NC", "GA",
        "AZ", "WA", "MA", "TN", "IN", "MO", "MD", "WI", "MN", "CO"
    ])
    
    # Premium (based on plan type and risk score)
    if plan_type == "HMO":
        base_premium = random.uniform(0, 50)  # Many HMOs have $0 premium
    elif plan_type == "PPO":
        base_premium = random.uniform(20, 100)
    elif plan_type == "SNP":
        base_premium = random.uniform(0, 30)
    else:
        base_premium = random.uniform(30, 150)
    
    monthly_premium = round(base_premium * risk_score, 2)
    
    return {
        "member_id": f"MEM-{member_id:08d}",
        "age": age,
        "gender": gender,
        "conditions": conditions,
        "num_conditions": num_conditions,
        "plan_type": plan_type,
        "plan_id": "H1234-001",  # Sample plan ID
        "enrollment_status": enrollment_status,
        "enrollment_date": enrollment_date,
        "state": state,
        "risk_score": round(risk_score, 3),
        "star_eligible": star_eligible,
        "monthly_premium": monthly_premium,
        "last_updated": datetime.now()
    }

# Generate members (using cfg.num_measures * 1000 for realistic member base)
num_members = 50000  # Typical medium-sized MA plan
print(f"Generating {num_members:,} member enrollment records...")

members_data = []
for i in range(1, num_members + 1):
    members_data.append(generate_member(i))
    
    # Progress indicator
    if i % 10000 == 0:
        print(f"  Generated {i:,} members...")

print(f"✅ Generated {len(members_data):,} member records")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create DataFrame and Table

# COMMAND ----------

# Define schema
schema = StructType([
    StructField("member_id", StringType(), False),
    StructField("age", IntegerType(), False),
    StructField("gender", StringType(), False),
    StructField("conditions", ArrayType(StringType()), True),
    StructField("num_conditions", IntegerType(), False),
    StructField("plan_type", StringType(), False),
    StructField("plan_id", StringType(), False),
    StructField("enrollment_status", StringType(), False),
    StructField("enrollment_date", TimestampType(), False),
    StructField("state", StringType(), False),
    StructField("risk_score", DoubleType(), False),
    StructField("star_eligible", BooleanType(), False),
    StructField("monthly_premium", DoubleType(), False),
    StructField("last_updated", TimestampType(), False)
])

# Create DataFrame
members_df = spark.createDataFrame(members_data, schema=schema)

# Write to Delta table
members_df.write.mode("overwrite").saveAsTable(cfg.member_table)

print(f"✅ Created table: {cfg.member_table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Data

# COMMAND ----------

# Show statistics
print("=" * 80)
print("MEMBER ENROLLMENT DATA STATISTICS")
print("=" * 80)

stats = spark.sql(f"""
SELECT 
    COUNT(*) as total_members,
    COUNT(DISTINCT plan_type) as plan_types,
    SUM(CASE WHEN star_eligible THEN 1 ELSE 0 END) as star_eligible_members,
    SUM(CASE WHEN enrollment_status = 'Active' THEN 1 ELSE 0 END) as active_members,
    ROUND(AVG(age), 1) as avg_age,
    ROUND(AVG(num_conditions), 2) as avg_conditions,
    ROUND(AVG(risk_score), 3) as avg_risk_score,
    ROUND(AVG(monthly_premium), 2) as avg_premium
FROM {cfg.member_table}
""").collect()[0]

print(f"Total Members:        {stats['total_members']:,}")
print(f"Plan Types:           {stats['plan_types']}")
print(f"Star Eligible:        {stats['star_eligible_members']:,} ({stats['star_eligible_members']/stats['total_members']*100:.1f}%)")
print(f"Active Members:       {stats['active_members']:,} ({stats['active_members']/stats['total_members']*100:.1f}%)")
print(f"Avg Age:              {stats['avg_age']:.1f} years")
print(f"Avg Conditions:       {stats['avg_conditions']:.2f}")
print(f"Avg Risk Score:       {stats['avg_risk_score']:.3f}")
print(f"Avg Monthly Premium:  ${stats['avg_premium']:.2f}")
print("=" * 80)

# Show members by plan type
print("\nMembers by plan type:")
plan_type_df = spark.sql(f"""
SELECT 
    plan_type,
    COUNT(*) as member_count,
    ROUND(AVG(age), 1) as avg_age,
    ROUND(AVG(risk_score), 3) as avg_risk_score,
    ROUND(AVG(monthly_premium), 2) as avg_premium
FROM {cfg.member_table}
GROUP BY plan_type
ORDER BY member_count DESC
""")
plan_type_df.show()

# Show members by state (top 10)
print("\nMembers by state (top 10):")
state_df = spark.sql(f"""
SELECT 
    state,
    COUNT(*) as member_count,
    ROUND(AVG(risk_score), 3) as avg_risk_score
FROM {cfg.member_table}
GROUP BY state
ORDER BY member_count DESC
LIMIT 10
""")
state_df.show()

# Show age distribution
print("\nAge distribution:")
age_df = spark.sql(f"""
SELECT 
    CASE
        WHEN age < 65 THEN 'Under 65 (Disabled)'
        WHEN age BETWEEN 65 AND 74 THEN '65-74'
        WHEN age BETWEEN 75 AND 84 THEN '75-84'
        ELSE '85+'
    END as age_group,
    COUNT(*) as member_count,
    ROUND(AVG(num_conditions), 2) as avg_conditions,
    ROUND(AVG(risk_score), 3) as avg_risk_score
FROM {cfg.member_table}
GROUP BY 
    CASE
        WHEN age < 65 THEN 'Under 65 (Disabled)'
        WHEN age BETWEEN 65 AND 74 THEN '65-74'
        WHEN age BETWEEN 75 AND 84 THEN '75-84'
        ELSE '85+'
    END
ORDER BY 
    CASE age_group
        WHEN 'Under 65 (Disabled)' THEN 1
        WHEN '65-74' THEN 2
        WHEN '75-84' THEN 3
        ELSE 4
    END
""")
age_df.show()

# COMMAND ----------

print("=" * 80)
print("DATA GENERATION COMPLETE!")
print("=" * 80)
print(f"✅ Table created: {cfg.member_table}")
print(f"✅ Total members: {num_members:,}")
print(f"✅ Star eligible: {stats['star_eligible_members']:,}")
print("=" * 80)
