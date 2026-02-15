# Databricks notebook source
# MAGIC %md
# MAGIC # Create Predictions Table
# MAGIC
# MAGIC Creates table for star ratings predictions.

# COMMAND ----------

# Ensure Environment widget exists (use current value so job-injected value is preserved)
try:
    _current = dbutils.widgets.get("environment")
except Exception:
    _current = "dev"
dbutils.widgets.dropdown("environment", _current, ["dev", "staging", "prod"], "Environment")
print(f"Environment: {_current} (change the dropdown if needed, then re-run the next cell)")

# COMMAND ----------

import sys
import os
sys.path.append(os.path.abspath('..'))
from shared.config import get_config

env_from_widget = dbutils.widgets.get("environment")
cfg = get_config(environment=env_from_widget)

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE TABLE {cfg.predictions_table} (
    prediction_id STRING,
    measure_id STRING,
    current_performance DOUBLE,
    predicted_performance DOUBLE,
    confidence_interval STRUCT<
        lower: DOUBLE,
        upper: DOUBLE
    >,
    prediction_date TIMESTAMP,
    model_version STRING
)
USING DELTA
COMMENT 'Star ratings performance predictions'
""")

print(f"✅ Created table: {cfg.predictions_table}")

# COMMAND ----------

# Generate simple predictions (current + estimated impact)
predictions_data = spark.sql(f"""
SELECT 
    uuid() as prediction_id,
    measure_id,
    performance_rate as current_performance,
    performance_rate + (gap * 0.5) as predicted_performance,
    named_struct(
        'lower', performance_rate + (gap * 0.3),
        'upper', performance_rate + (gap * 0.7)
    ) as confidence_interval,
    current_timestamp() as prediction_date,
    'baseline_v1.0' as model_version
FROM {cfg.measures_table}
WHERE gap > 0.05
""")

predictions_data.write.mode("overwrite").saveAsTable(cfg.predictions_table)

print(f"✅ Generated predictions for measures with gaps")
