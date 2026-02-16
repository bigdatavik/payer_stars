# Databricks notebook source
# MAGIC %md
# MAGIC # Create Genie Space for Star Ratings Analytics
# MAGIC
# MAGIC Creates Genie Space programmatically using Databricks Genie API.
# MAGIC All configuration from config.yaml.
# MAGIC
# MAGIC Reference: https://docs.databricks.com/api/workspace/genie/createspace

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

from databricks.sdk import WorkspaceClient
import json
import uuid

env_from_widget = dbutils.widgets.get("environment")
cfg = get_config(environment=env_from_widget)
print_config(cfg)

w = WorkspaceClient()

print(f"Using workspace: {cfg.workspace_host}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Check for Existing Genie Space

# COMMAND ----------

print("Checking for existing Genie spaces...")

try:
    # List spaces using WorkspaceClient API
    response = w.api_client.do(
        'GET',
        '/api/2.0/genie/spaces'
    )
    existing_spaces = response.get('spaces', [])
    
    # Look for space with matching title and DELETE it
    for space in existing_spaces:
        if space.get('title') == cfg.genie_display_name:
            old_space_id = space.get('space_id')
            print(f"🗑️  Found existing space: {old_space_id}")
            print(f"   Title: {space.get('title')}")
            print(f"   Deleting to create fresh...")
            
            # Delete the existing space
            try:
                w.api_client.do(
                    'DELETE',
                    f'/api/2.0/genie/spaces/{old_space_id}'
                )
                print(f"✅ Deleted existing space: {old_space_id}")
            except Exception as delete_error:
                print(f"⚠️  Could not delete space: {delete_error}")
                print(f"   You may need to manually delete it from the UI")
    
    print("✅ Ready to create new Genie space")
        
except Exception as e:
    print(f"Error checking/deleting spaces: {e}")
    print("Will proceed with creation...")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Fresh Genie Space

# COMMAND ----------

print(f"Creating new Genie Space: {cfg.genie_display_name}")

try:
    # Create serialized space configuration with properly structured instructions
    # Instructions must be an OBJECT at root level (not inside config, not a string)
    serialized_space = {
        "version": 1,
        "config": {
            "sample_questions": [
                {
                    "id": str(uuid.uuid4()).replace('-', ''),
                    "question": ["Show me measures with critical gaps"]
                },
                {
                    "id": str(uuid.uuid4()).replace('-', ''),
                    "question": ["What is the average star rating by domain?"]
                },
                {
                    "id": str(uuid.uuid4()).replace('-', ''),
                    "question": ["Which measures need the most improvement?"]
                },
                {
                    "id": str(uuid.uuid4()).replace('-', ''),
                    "question": ["Show performance trends by plan type"]
                }
            ]
        },
        "instructions": {
            "text_instructions": [
                {
                    "id": str(uuid.uuid4()).replace('-', ''),
                    "content": [f"""This space analyzes CMS Star Ratings for Medicare Advantage plans across 2 tables:
1. {cfg.catalog}.{cfg.schema}.measures_data - HEDIS measures with performance rates (gap_severity: CRITICAL/HIGH/MODERATE/LOW)
2. {cfg.catalog}.{cfg.schema}.star_analysis - AI analysis results (classification, priority, recommendations)

Use these relationships:
- measures_data.measure_id = star_analysis.measure_id (1:1)
- measures_data has: performance_rate, target_benchmark, gap, current_stars, member_count
- star_analysis has: classification, root_causes, recommendations, priority

Common filters:
- WHERE gap_severity = 'Critical' (urgent gaps)
- WHERE current_stars < 3 (low-performing measures)
- WHERE domain IN ('Clinical Care', 'Member Experience', 'Access')
- WHERE plan_type IN ('HMO', 'PPO', 'SNP')
- ORDER BY gap DESC (prioritize largest gaps)"""]
                }
            ]
        },
        "data_sources": {
            "tables": [
                {"identifier": f"{cfg.catalog}.{cfg.schema}.measures_data"},
                {"identifier": f"{cfg.catalog}.{cfg.schema}.star_analysis"}
            ]
        }
    }
    
    print(f"✅ Using properly structured instructions object")
    
    # Create space using WorkspaceClient API
    payload = {
        "title": cfg.genie_display_name,
        "description": cfg.genie_description,
        "warehouse_id": cfg.warehouse_id,
        "serialized_space": json.dumps(serialized_space)
    }
    
    response = w.api_client.do(
        'POST',
        '/api/2.0/genie/spaces',
        body=payload
    )
    
    GENIE_SPACE_ID = response.get('space_id')
    print(f"✅ Genie Space created: {GENIE_SPACE_ID}")
    print(f"   Title: {cfg.genie_display_name}")
    
except Exception as e:
    print(f"❌ Error creating space: {e}")
    raise e

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configure Genie Space

# COMMAND ----------

print(f"Configuring Genie Space {GENIE_SPACE_ID}...")

try:
    # Update space with warehouse using WorkspaceClient API
    payload = {
        "title": cfg.genie_display_name,
        "description": cfg.genie_description,
        "warehouse_id": cfg.warehouse_id
    }
    
    response = w.api_client.do(
        'PATCH',
        f'/api/2.0/genie/spaces/{GENIE_SPACE_ID}',
        body=payload
    )
    
    print(f"✅ Space configured with SQL Warehouse: {cfg.warehouse_id}")
    
except Exception as e:
    print(f"⚠️  Could not update space config: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Save Genie Space ID to Config Table

# COMMAND ----------

# Create config table if it doesn't exist (matches existing schema with created_at)
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {cfg.config_table} (
  config_key STRING NOT NULL,
  config_value STRING NOT NULL,
  created_at TIMESTAMP NOT NULL,
  CONSTRAINT config_pk PRIMARY KEY(config_key)
)
USING DELTA
COMMENT 'Configuration values for star ratings system'
""")

# Save Genie Space ID using explicit column references
spark.sql(f"""
MERGE INTO {cfg.config_table} t
USING (
  SELECT 
    'genie_space_id' as config_key,
    '{GENIE_SPACE_ID}' as config_value,
    current_timestamp() as created_at
) s
ON t.config_key = s.config_key
WHEN MATCHED THEN UPDATE SET 
  t.config_value = s.config_value,
  t.created_at = s.created_at
WHEN NOT MATCHED THEN INSERT (config_key, config_value, created_at)
  VALUES (s.config_key, s.config_value, s.created_at)
""")

print(f"✅ Genie Space ID saved to {cfg.config_table}")

# Verify
saved_id = spark.sql(f"""
SELECT config_value 
FROM {cfg.config_table} 
WHERE config_key = 'genie_space_id'
""").collect()[0][0]

print(f"   Verified saved ID: {saved_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Grant Service Principal Permissions (MANUAL STEP)

# COMMAND ----------

print("=" * 80)
print("GRANT SERVICE PRINCIPAL PERMISSIONS (ONE-TIME MANUAL STEP)")
print("=" * 80)
print("")
print("ℹ️  NOTE: Databricks does not provide a programmatic API to grant")
print("   Genie Space permissions. This is a one-time manual step.")
print("")
print("🎯 WHAT YOU'RE DOING:")
print("   Granting your Databricks APP permission to query this Genie Space.")
print("   The app runs as a SERVICE PRINCIPAL (like a robot user).")
print("")
print("📋 STEP-BY-STEP INSTRUCTIONS:")
print("")
print(f"1. Open Genie Space in your browser:")
print(f"   {cfg.workspace_host}/#genie/{GENIE_SPACE_ID}")
print("")
print(f"2. Click the 'Share' button (top-right corner)")
print("")
print(f"3. In the search box, type: payerstars-dev")
print(f"   ☝️  This is your APP'S SERVICE PRINCIPAL name")
print(f"   (Look for 'app-...' prefix, e.g., 'app-xxxxx payerstars-dev')")
print("")
print(f"4. Select it from the dropdown")
print(f"   (It will show as a service principal, not a user)")
print("")
print(f"5. Set permission level to: 'Can Run'")
print(f"   ⚠️  IMPORTANT: Select 'Can Run' NOT 'Can Use' from the dropdown!")
print("")
print(f"6. Click 'Add' or 'Save'")
print("")
print(f"✅ DONE! The Performance Dashboard will now be able to query Genie.")
print(f"   This is a ONE-TIME setup per environment (dev/prod).")
print("")
print("=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Genie Space Instructions

# COMMAND ----------

instructions = f"""
# CMS Star Ratings Analytics - Data Guide

## Available Data

**Main Tables:**
- {cfg.catalog}.{cfg.schema}.measures_data
- {cfg.catalog}.{cfg.schema}.star_analysis

## Schema - measures_data

### Core Fields
- **measure_id**: Unique measure identifier (STRING)
- **measure_name**: Full measure name (STRING)
- **domain**: HEDIS domain (e.g., Clinical Care, Access) (STRING)
- **measure_type**: Type of measure (Outcome, Process, Intermediate) (STRING)

### Performance Metrics
- **performance_rate**: Current performance rate (0-100) (DOUBLE)
- **target_benchmark**: Target benchmark to achieve (DOUBLE)
- **gap**: Performance gap (target - performance) (DOUBLE)
- **gap_severity**: Severity level (Critical, High, Moderate, Low) (STRING)

### Star Rating
- **current_stars**: Current star rating (1-5) (DOUBLE)
- **target_stars**: Target star rating (DOUBLE)
- **weight**: Measure weight for overall score (DOUBLE)

### Member Impact
- **member_count**: Number of members affected (INTEGER)
- **plan_type**: Plan type (HMO, PPO, SNP) (STRING)

## Common Queries

### Performance Analysis
- "Show me all measures with critical gaps"
- "What measures have less than 3 stars?"
- "Which measures have the largest performance gaps?"
- "Show star ratings by domain"

### Gap Analysis
- "List measures with gaps greater than 10 points"
- "Show the worst performing measures"
- "Which domains have the most critical issues?"
- "Performance trends by plan type"

### Member Impact
- "Which measures affect the most members?"
- "Show high-impact measures with large gaps"
- "Member count by gap severity"

### Domain Analysis
- "Average performance by HEDIS domain"
- "Clinical Care measures with low stars"
- "Access/Availability measures needing improvement"

### Plan Type Analysis
- "Compare HMO vs PPO performance"
- "SNP plan measures with gaps"
- "Star ratings by plan type"

## SQL Tips

- Use `WHERE gap_severity = 'Critical'` for urgent issues
- Filter by `domain` for category analysis
- Use `current_stars < 3` for low-performing measures
- Sort by `gap DESC` to prioritize improvements
- Join with `star_analysis` for AI insights

## Example Queries

```sql
-- Critical gap measures
SELECT 
  measure_id,
  measure_name,
  domain,
  performance_rate,
  target_benchmark,
  gap,
  member_count
FROM {cfg.catalog}.{cfg.schema}.measures_data
WHERE gap_severity = 'Critical'
ORDER BY gap DESC
LIMIT 10;

-- Star rating distribution
SELECT 
  FLOOR(current_stars) as star_level,
  COUNT(*) as measure_count,
  AVG(gap) as avg_gap
FROM {cfg.catalog}.{cfg.schema}.measures_data
GROUP BY FLOOR(current_stars)
ORDER BY star_level DESC;

-- High-impact improvement opportunities
SELECT 
  measure_id,
  measure_name,
  member_count,
  gap,
  (member_count * gap) as impact_score
FROM {cfg.catalog}.{cfg.schema}.measures_data
WHERE gap > 10
ORDER BY impact_score DESC
LIMIT 10;
```
"""

print("=" * 80)
print("GENIE SPACE INSTRUCTIONS")
print("=" * 80)
print(instructions)
print("=" * 80)
print("\n💡 TIP: You can add these instructions to the Genie Space via the UI")
print(f"   Open: {cfg.workspace_host}/#genie/{GENIE_SPACE_ID}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verification

# COMMAND ----------

print("=" * 80)
print("GENIE SPACE SETUP COMPLETE!")
print("=" * 80)
print(f"✅ Space ID:       {GENIE_SPACE_ID}")
print(f"✅ Title:          {cfg.genie_display_name}")
print(f"✅ Warehouse ID:   {cfg.warehouse_id}")
print(f"✅ Source Tables:  measures_data, star_analysis")
print(f"✅ Saved to:       {cfg.config_table}")
print("=" * 80)
print("\n🎉 Your Star Ratings analytics Genie Space is ready!")
print(f"\nNext steps:")
print(f"1. Open Genie Space: {cfg.workspace_host}/#genie/{GENIE_SPACE_ID}")
print(f"2. Try asking: 'Show me measures with critical gaps'")
print(f"3. Share with team members via the Share button")
print(f"4. (Optional) Add more sample questions in Genie UI")
print("=" * 80)

# Store as output for downstream tasks
try:
    dbutils.jobs.taskValues.set("genie_space_id", GENIE_SPACE_ID)
    print(f"\n✅ Set task value: genie_space_id = {GENIE_SPACE_ID}")
except:
    pass


