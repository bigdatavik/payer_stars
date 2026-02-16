# Databricks notebook source
# MAGIC %md
# MAGIC # Batch Analyze Measures
# MAGIC
# MAGIC Batch process all measures through UC functions.

# COMMAND ----------

# Ensure Environment widget exists (use current value so job-injected value is preserved)
try:
    _current = dbutils.widgets.get("environment")
except Exception:
    _current = "dev"
dbutils.widgets.dropdown("environment", _current, ["dev", "staging", "prod"], "Environment")
print(f"Environment: {_current} (change the dropdown if needed, then re-run the next cell)")

# COMMAND ----------

# MAGIC %pip install pyyaml --quiet
dbutils.library.restartPython()

# COMMAND ----------

import sys
import os
sys.path.append(os.path.abspath('..'))
from shared.config import get_config
from datetime import datetime
import uuid

env_from_widget = dbutils.widgets.get("environment")
cfg = get_config(environment=env_from_widget)

# COMMAND ----------

# Get all measures with critical or moderate gaps
measures_df = spark.sql(f"""
SELECT measure_id, measure_name, performance_rate, target_benchmark, gap, gap_severity
FROM {cfg.measures_table}
WHERE gap_severity IN ('Critical', 'Moderate')
ORDER BY gap DESC
LIMIT 10
""")

print(f"Analyzing {measures_df.count()} measures with critical/moderate gaps")

# COMMAND ----------

# Process each measure
analysis_results = []

for row in measures_df.collect():
    measure_data = f"{row.measure_name} ({row.measure_id}): Performance {row.performance_rate:.1%}, Target {row.target_benchmark:.1%}, Gap {row.gap:.1%}"
    
    # Call UC functions
    classification = spark.sql(f"""
        SELECT {cfg.catalog}.{cfg.schema}.star_measure_classify('{measure_data}') as result
    """).collect()[0].result
    
    gap_analysis = spark.sql(f"""
        SELECT {cfg.catalog}.{cfg.schema}.star_gap_analyze('{measure_data}') as result
    """).collect()[0].result
    
    analysis_results.append({
        "analysis_id": str(uuid.uuid4()),
        "measure_id": row.measure_id,
        "measure_name": row.measure_name,
        "performance_rate": row.performance_rate,
        "target_benchmark": row.target_benchmark,
        "gap": row.gap,
        "classification": classification,
        "gap_analysis": gap_analysis,
        "recommendations": None,  # Will be generated separately
        "analyzed_at": datetime.now(),
        "analysis_version": "v1.0"
    })
    
    print(f"✅ Analyzed: {row.measure_id} - {classification.gap_severity}")

# COMMAND ----------

# Write results to table
from pyspark.sql.types import *

schema = StructType([
    StructField("analysis_id", StringType()),
    StructField("measure_id", StringType()),
    StructField("measure_name", StringType()),
    StructField("performance_rate", DoubleType()),
    StructField("target_benchmark", DoubleType()),
    StructField("gap", DoubleType()),
    StructField("classification", StructType([
        StructField("performance_level", StringType()),
        StructField("gap_severity", StringType()),
        StructField("star_impact", DoubleType()),
        StructField("confidence", DoubleType())
    ])),
    StructField("gap_analysis", StructType([
        StructField("root_causes", ArrayType(StringType())),
        StructField("affected_populations", ArrayType(StringType())),
        StructField("performance_barriers", ArrayType(StringType())),
        StructField("data_quality_issues", ArrayType(StringType()))
    ])),
    StructField("recommendations", StructType([
        StructField("interventions", ArrayType(StringType())),
        StructField("priority_actions", ArrayType(StringType())),
        StructField("estimated_impact", DoubleType()),
        StructField("timeline", StringType()),
        StructField("resources", ArrayType(StringType()))
    ])),
    StructField("analyzed_at", TimestampType()),
    StructField("analysis_version", StringType())
])

analysis_df = spark.createDataFrame(analysis_results, schema)
analysis_df.write.mode("overwrite").saveAsTable(cfg.star_analysis)

print(f"✅ Wrote {len(analysis_results)} analysis results to {cfg.star_analysis}")
