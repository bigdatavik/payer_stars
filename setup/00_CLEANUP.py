# Databricks notebook source
# MAGIC %md
# MAGIC # CLEANUP - Remove All Star Ratings Resources
# MAGIC
# MAGIC **WARNING:** This will delete:
# MAGIC - Catalog and Schema (from config.yaml)
# MAGIC - Vector Search Index (hedis_guidelines_index)
# MAGIC - All tables (measures_data, member_enrollments, hedis_guidelines_kb, star_analysis, star_predictions, config_genie)
# MAGIC - All UC functions (4 star rating functions)
# MAGIC
# MAGIC All configuration loaded from config.yaml via shared.config module.

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

print("🗑️  STAR RATINGS CLEANUP SCRIPT")
print("=" * 70)
print(f"Will delete:")
print(f"  - Catalog: {cfg.catalog}")
print(f"  - Schema: {cfg.schema}")
print(f"  - Vector Index: {cfg.hedis_guidelines_index}")
print("=" * 70)
print("\n⚠️  WARNING: This is IRREVERSIBLE!")
print()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Drop Vector Search Index

# COMMAND ----------

from databricks.sdk import WorkspaceClient

print("\n🔍 Dropping vector search index...")
w = WorkspaceClient()

# Delete HEDIS guidelines index
try:
    print(f"   Deleting: {cfg.hedis_guidelines_index}")
    w.vector_search_indexes.delete_index(index_name=cfg.hedis_guidelines_index)
    print(f"   ✅ Deleted HEDIS guidelines vector index")
except Exception as e:
    print(f"   ⚠️  Index deletion: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Drop UC Functions

# COMMAND ----------

print("\n🔧 Dropping UC Functions...")

functions = [
    "star_measure_classify",
    "star_gap_analyze",
    "star_improvement_recommend",
    "star_explain"
]

for func in functions:
    try:
        spark.sql(f"DROP FUNCTION IF EXISTS {cfg.catalog}.{cfg.schema}.{func}")
        print(f"   ✅ Dropped function: {func}")
    except Exception as e:
        print(f"   ⚠️  Function {func} deletion: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Drop Tables

# COMMAND ----------

print("\n📊 Dropping tables...")

tables = [
    "measures_data",
    "member_enrollments",
    "hedis_docs_staging",
    "hedis_guidelines_kb",
    "star_analysis",
    "star_predictions",
    "config_genie",
    "vector_search_status",
    "validation_report"
]

for table in tables:
    try:
        spark.sql(f"DROP TABLE IF EXISTS {cfg.catalog}.{cfg.schema}.{table}")
        print(f"   ✅ Dropped table: {table}")
    except Exception as e:
        print(f"   ⚠️  Table {table} deletion: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Drop Schema

# COMMAND ----------

print("\n📁 Dropping schema...")

try:
    spark.sql(f"DROP SCHEMA IF EXISTS {cfg.catalog}.{cfg.schema} CASCADE")
    print(f"   ✅ Dropped schema: {cfg.catalog}.{cfg.schema}")
except Exception as e:
    print(f"   ⚠️  Schema deletion: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Drop Catalog

# COMMAND ----------

print("\n🗂️  Dropping catalog...")

try:
    spark.sql(f"DROP CATALOG IF EXISTS {cfg.catalog} CASCADE")
    print(f"   ✅ Dropped catalog: {cfg.catalog}")
except Exception as e:
    print(f"   ⚠️  Catalog deletion: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Skip Vector Search Endpoint Deletion (Shared Resource)

# COMMAND ----------

print("\n🔌 Vector search endpoint...")

endpoint_name = cfg.vector_endpoint
print(f"   Endpoint: {endpoint_name}")
print(f"   ⚠️  SKIPPING deletion: This is a SHARED endpoint used by multiple projects")
print(f"   Note: Index was already deleted in Step 1")

# COMMAND ----------

print("\n" + "=" * 70)
print("✅ CLEANUP COMPLETE!")
print("=" * 70)
print("\nAll Star Ratings resources have been deleted.")
print("You can now redeploy from scratch using:")
print("  ./deploy_with_config.sh dev")
print("=" * 70)


