# Databricks notebook source
# MAGIC %md
# MAGIC # Create Star Analysis Table
# MAGIC
# MAGIC Creates table to store star ratings measure analysis results.

# COMMAND ----------

import sys
import os
sys.path.append(os.path.abspath('..'))
from shared.config import get_config

cfg = get_config()

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE TABLE {cfg.star_analysis} (
    analysis_id STRING,
    measure_id STRING,
    measure_name STRING,
    performance_rate DOUBLE,
    target_benchmark DOUBLE,
    gap DOUBLE,
    classification STRUCT<
        performance_level: STRING,
        gap_severity: STRING,
        star_impact: DOUBLE,
        confidence: DOUBLE
    >,
    gap_analysis STRUCT<
        root_causes: ARRAY<STRING>,
        affected_populations: ARRAY<STRING>,
        performance_barriers: ARRAY<STRING>,
        data_quality_issues: ARRAY<STRING>
    >,
    recommendations STRUCT<
        interventions: ARRAY<STRING>,
        priority_actions: ARRAY<STRING>,
        estimated_impact: DOUBLE,
        timeline: STRING,
        resources: ARRAY<STRING>
    >,
    analyzed_at TIMESTAMP,
    analysis_version STRING
)
USING DELTA
COMMENT 'Star ratings measure analysis results from AI agent'
""")

print(f"✅ Created table: {cfg.star_analysis}")
