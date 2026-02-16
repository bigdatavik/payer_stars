# Databricks notebook source
# MAGIC %md
# MAGIC # UC Function: star_measure_classify
# MAGIC
# MAGIC Classifies HEDIS measure performance for CMS Star Ratings.
# MAGIC All configuration from config.yaml - including LLM endpoint!

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
from shared.config import get_config

env_from_widget = dbutils.widgets.get("environment")
cfg = get_config(environment=env_from_widget)
print(f"Creating function in: {cfg.catalog}.{cfg.schema}")
print(f"Using LLM: {cfg.llm_endpoint}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Drop Existing Function

# COMMAND ----------

spark.sql(f"DROP FUNCTION IF EXISTS {cfg.catalog}.{cfg.schema}.star_measure_classify")
print("Dropped existing function (if any)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create UC Function
# MAGIC
# MAGIC Using AI_QUERY pattern - exact same as fraud project

# COMMAND ----------

# Create the star_measure_classify function with markdown stripping
spark.sql(f"""
CREATE OR REPLACE FUNCTION {cfg.catalog}.{cfg.schema}.star_measure_classify(measure_data STRING)
RETURNS STRUCT<
  performance_level: STRING,
  gap_severity: STRING,
  star_impact: DOUBLE,
  confidence: DOUBLE
>
COMMENT 'Classifies HEDIS measure performance for CMS Star Ratings using AI'
RETURN 
  FROM_JSON(
    TRIM(REGEXP_REPLACE(REGEXP_REPLACE(
      AI_QUERY(
        'databricks-claude-sonnet-4-5',
        CONCAT(
          'You are a CMS Star Ratings expert analyzing HEDIS measure performance. Return ONLY a JSON object.\\n\\n',
          'MEASURE DATA: ', measure_data, '\\n\\n',
          'Classify the measure performance:\\n',
          'performance_level: "Below Target" if performance < target, "Meeting Target" if close to target, "Exceeding Target" if above target\\n',
          'gap_severity: "Critical" if gap > 0.15, "Moderate" if gap > 0.08, "Minor" if gap > 0.03, "None" if gap <= 0.03\\n',
          'star_impact: Estimated impact on overall star rating (0.0 to 1.0), higher gap = higher impact\\n',
          'confidence: Confidence in classification (0.0 to 1.0)\\n\\n',
          'Return this JSON: {{"performance_level": "Below Target|Meeting Target|Exceeding Target", "gap_severity": "Critical|Moderate|Minor|None", "star_impact": 0.0-1.0, "confidence": 0.0-1.0}}\\n\\n',
          'Return ONLY the JSON object, no other text.'
        )
      ), '```json', ''), '```', '')),
    'STRUCT<performance_level:STRING,gap_severity:STRING,star_impact:DOUBLE,confidence:DOUBLE>'
  )
""")

print(f"✅ Function created: {cfg.catalog}.{cfg.schema}.star_measure_classify")
print(f"✅ Using LLM: databricks-claude-sonnet-4-5")
print(f"✅ Includes markdown stripping (removes ```json and ``` wrappers)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test Function

# COMMAND ----------

# Test with a sample measure
test_result = spark.sql(f"""
SELECT {cfg.catalog}.{cfg.schema}.star_measure_classify(
  'Breast Cancer Screening (BCS): Performance rate 62%, Target 75%, Gap 13%, Numerator 6200, Denominator 10000'
) as classification
""").collect()[0]

print("Test Result:")
print(f"  Performance Level: {test_result.classification.performance_level}")
print(f"  Gap Severity: {test_result.classification.gap_severity}")
print(f"  Star Impact: {test_result.classification.star_impact:.2f}")
print(f"  Confidence: {test_result.classification.confidence:.2f}")

# COMMAND ----------

print("=" * 80)
print("UC FUNCTION CREATED SUCCESSFULLY!")
print("=" * 80)
print(f"✅ Function: {cfg.catalog}.{cfg.schema}.star_measure_classify")
print(f"✅ LLM: databricks-claude-sonnet-4-5")
print(f"✅ Returns: performance_level, gap_severity, star_impact, confidence")
print("=" * 80)
