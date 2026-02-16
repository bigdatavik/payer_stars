# Databricks notebook source
# MAGIC %md
# MAGIC # UC Function: star_explain
# MAGIC
# MAGIC Generates human-readable explanations for HEDIS measure analysis.
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

spark.sql(f"DROP FUNCTION IF EXISTS {cfg.catalog}.{cfg.schema}.star_explain")
print("✅ Dropped existing function (if any)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create UC Function

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {cfg.catalog}.{cfg.schema}.star_explain(
  measure_data STRING,
  context STRING
)
RETURNS STRING
COMMENT 'Generates human-readable explanations for HEDIS measure performance'
RETURN 
  TRIM(REGEXP_REPLACE(REGEXP_REPLACE(
    AI_QUERY(
      'databricks-claude-sonnet-4-5',
      CONCAT(
        'You are explaining HEDIS measure performance to healthcare executives. Provide a clear, concise explanation.\\n\\n',
        'MEASURE DATA: ', measure_data, '\\n\\n',
        'CONTEXT: ', context, '\\n\\n',
        'Provide a 3-4 sentence explanation that:\\n',
        '1. States the current performance vs target\\n',
        '2. Explains why this matters for Star Ratings\\n',
        '3. Highlights the key issue or opportunity\\n',
        '4. Suggests the impact of addressing it\\n\\n',
        'Write in clear, professional language. Do NOT use JSON format. Return only the explanation text.'
      )
    ), '```', ''), '\\n\\n', ' '))
""")

print(f"✅ Function created: {cfg.catalog}.{cfg.schema}.star_explain")
print(f"✅ Using LLM: databricks-claude-sonnet-4-5")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test Function

# COMMAND ----------

test_result = spark.sql(f"""
SELECT {cfg.catalog}.{cfg.schema}.star_explain(
  'Controlling High Blood Pressure (CBP): Performance 68%, Target 80%, Gap 12%, Affects 15,000 members',
  'This is a 4-star measure with high member impact. Gap is moderate but closing it would add 0.3 to overall plan rating.'
) as explanation
""").collect()[0]

print("✅ Test Result:")
print("=" * 70)
print(test_result.explanation)
print("=" * 70)

# COMMAND ----------

print("=" * 80)
print("✅ UC FUNCTION CREATED SUCCESSFULLY!")
print("=" * 80)
print(f"Function: {cfg.catalog}.{cfg.schema}.star_explain")
print(f"Purpose: Human-readable explanations for executives")
print("=" * 80)
