# Databricks notebook source
# MAGIC %md
# MAGIC # UC Function: star_gap_analyze
# MAGIC
# MAGIC Analyzes performance gaps in HEDIS measures for root cause analysis.
# MAGIC All configuration from config.yaml.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Import Configuration

# COMMAND ----------

import sys
import os
sys.path.append(os.path.abspath('..'))
from shared.config import get_config

cfg = get_config()
print(f"Creating function in: {cfg.catalog}.{cfg.schema}")
print(f"Using LLM: {cfg.llm_endpoint}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Drop Existing Function

# COMMAND ----------

spark.sql(f"DROP FUNCTION IF EXISTS {cfg.catalog}.{cfg.schema}.star_gap_analyze")
print("✅ Dropped existing function (if any)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create UC Function

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {cfg.catalog}.{cfg.schema}.star_gap_analyze(measure_data STRING)
RETURNS STRUCT<
  root_causes: ARRAY<STRING>,
  affected_populations: ARRAY<STRING>,
  performance_barriers: ARRAY<STRING>,
  data_quality_issues: ARRAY<STRING>
>
COMMENT 'Analyzes performance gaps to identify root causes and barriers'
RETURN 
  FROM_JSON(
    TRIM(REGEXP_REPLACE(REGEXP_REPLACE(
      AI_QUERY(
        'databricks-claude-sonnet-4-5',
        CONCAT(
          'You are a healthcare quality improvement expert analyzing HEDIS measure performance gaps. Return ONLY a JSON object.\\n\\n',
          'MEASURE DATA: ', measure_data, '\\n\\n',
          'Analyze the performance gap and identify:\\n',
          '1. root_causes: List 2-4 likely root causes (e.g., "Low outreach", "Provider engagement", "Member barriers", "System issues")\\n',
          '2. affected_populations: List 2-3 member populations most affected (e.g., "Dual eligible", "Rural members", "High-risk diabetics")\\n',
          '3. performance_barriers: List 2-3 key barriers preventing target achievement (e.g., "Access to care", "Health literacy", "Care coordination")\\n',
          '4. data_quality_issues: List 1-2 potential data quality concerns (e.g., "Incomplete claims", "Coding accuracy")\\n\\n',
          'Return this JSON: {{"root_causes": ["cause1", "cause2", ...], "affected_populations": ["pop1", "pop2", ...], "performance_barriers": ["barrier1", "barrier2", ...], "data_quality_issues": ["issue1", "issue2", ...]}}\\n\\n',
          'Return ONLY the JSON object, no other text.'
        )
      ), '```json', ''), '```', '')),
    'STRUCT<root_causes:ARRAY<STRING>,affected_populations:ARRAY<STRING>,performance_barriers:ARRAY<STRING>,data_quality_issues:ARRAY<STRING>>'
  )
""")

print(f"✅ Function created: {cfg.catalog}.{cfg.schema}.star_gap_analyze")
print(f"✅ Using LLM: databricks-claude-sonnet-4-5")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test Function

# COMMAND ----------

test_result = spark.sql(f"""
SELECT {cfg.catalog}.{cfg.schema}.star_gap_analyze(
  'Comprehensive Diabetes Care (CDC): Performance rate 58%, Target 78%, Gap 20%, Critical gap severity. Low HbA1c testing rates, poor medication adherence.'
) as analysis
""").collect()[0]

print("✅ Test Result:")
print("=" * 70)
print(f"Root Causes: {test_result.analysis.root_causes}")
print(f"Affected Populations: {test_result.analysis.affected_populations}")
print(f"Performance Barriers: {test_result.analysis.performance_barriers}")
print(f"Data Quality Issues: {test_result.analysis.data_quality_issues}")
print("=" * 70)

# COMMAND ----------

print("=" * 80)
print("✅ UC FUNCTION CREATED SUCCESSFULLY!")
print("=" * 80)
print(f"Function: {cfg.catalog}.{cfg.schema}.star_gap_analyze")
print(f"Purpose: Root cause analysis of performance gaps")
print("=" * 80)
