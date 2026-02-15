# Databricks notebook source
# MAGIC %md
# MAGIC # UC Function: star_improvement_recommend
# MAGIC
# MAGIC Generates improvement recommendations for HEDIS measures.
# MAGIC All configuration from config.yaml.

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
from shared.config import get_config

env_from_widget = dbutils.widgets.get("environment")
cfg = get_config(environment=env_from_widget)
print(f"Creating function in: {cfg.catalog}.{cfg.schema}")
print(f"Using LLM: {cfg.llm_endpoint}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Drop Existing Function

# COMMAND ----------

spark.sql(f"DROP FUNCTION IF EXISTS {cfg.catalog}.{cfg.schema}.star_improvement_recommend")
print("✅ Dropped existing function (if any)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create UC Function

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {cfg.catalog}.{cfg.schema}.star_improvement_recommend(
  measure_data STRING,
  gap_context STRING
)
RETURNS STRUCT<
  interventions: ARRAY<STRING>,
  priority_actions: ARRAY<STRING>,
  estimated_impact: DOUBLE,
  timeline: STRING,
  resources: ARRAY<STRING>
>
COMMENT 'Generates actionable improvement recommendations for HEDIS measures'
RETURN 
  FROM_JSON(
    TRIM(REGEXP_REPLACE(REGEXP_REPLACE(
      AI_QUERY(
        'databricks-claude-sonnet-4-5',
        CONCAT(
          'You are a healthcare quality improvement consultant. Generate actionable recommendations. Return ONLY a JSON object.\\n\\n',
          'MEASURE DATA: ', measure_data, '\\n\\n',
          'GAP CONTEXT: ', gap_context, '\\n\\n',
          'Provide improvement recommendations:\\n',
          '1. interventions: List 3-5 specific interventions (e.g., "Member outreach campaign", "Provider education", "Care management program")\\n',
          '2. priority_actions: List top 3 immediate actions to take this quarter\\n',
          '3. estimated_impact: Estimated improvement in performance rate if implemented (0.0 to 1.0)\\n',
          '4. timeline: Realistic implementation timeline ("3 months", "6 months", "12 months")\\n',
          '5. resources: List 2-3 key resources needed (e.g., "Care coordinators", "Outreach budget", "Analytics support")\\n\\n',
          'Return this JSON: {{"interventions": ["int1", "int2", ...], "priority_actions": ["action1", "action2", "action3"], "estimated_impact": 0.0-1.0, "timeline": "X months", "resources": ["res1", "res2", ...]}}\\n\\n',
          'Return ONLY the JSON object, no other text.'
        )
      ), '```json', ''), '```', '')),
    'STRUCT<interventions:ARRAY<STRING>,priority_actions:ARRAY<STRING>,estimated_impact:DOUBLE,timeline:STRING,resources:ARRAY<STRING>>'
  )
""")

print(f"✅ Function created: {cfg.catalog}.{cfg.schema}.star_improvement_recommend")
print(f"✅ Using LLM: databricks-claude-sonnet-4-5")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test Function

# COMMAND ----------

test_result = spark.sql(f"""
SELECT {cfg.catalog}.{cfg.schema}.star_improvement_recommend(
  'Breast Cancer Screening (BCS): Performance 62%, Target 75%, Gap 13%',
  'Root causes: Low outreach, Provider engagement gaps. Affected: Women 50-74, Rural members.'
) as recommendations
""").collect()[0]

print("✅ Test Result:")
print("=" * 70)
print(f"Interventions: {test_result.recommendations.interventions}")
print(f"Priority Actions: {test_result.recommendations.priority_actions}")
print(f"Estimated Impact: +{test_result.recommendations.estimated_impact:.1%}")
print(f"Timeline: {test_result.recommendations.timeline}")
print(f"Resources: {test_result.recommendations.resources}")
print("=" * 70)

# COMMAND ----------

print("=" * 80)
print("✅ UC FUNCTION CREATED SUCCESSFULLY!")
print("=" * 80)
print(f"Function: {cfg.catalog}.{cfg.schema}.star_improvement_recommend")
print(f"Purpose: Generate actionable improvement recommendations")
print("=" * 80)
