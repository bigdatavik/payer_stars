# Databricks notebook source
# MAGIC %md
# MAGIC # Setup: Create Catalog, Schema, and Volume
# MAGIC
# MAGIC Reads ALL configuration from config.yaml via shared.config module.
# MAGIC
# MAGIC **Run this first before deploying other resources.**

# COMMAND ----------

# MAGIC %md
# MAGIC ## Import Configuration

# COMMAND ----------

# Import shared configuration
import sys
import os

# Add parent directory to path (works in both interactive and job clusters)
sys.path.append(os.path.abspath('..'))

from shared.config import get_config, print_config

# Get configuration (auto-detects environment)
cfg = get_config()

# Print configuration for verification
print_config(cfg)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Catalog

# COMMAND ----------

# Create catalog - uses cfg.catalog from config.yaml
spark.sql(f"""
CREATE CATALOG IF NOT EXISTS {cfg.catalog}
COMMENT 'AI-Powered Payer Star Ratings System for Medicare Advantage'
""")

print(f"✅ Catalog '{cfg.catalog}' is ready")

# COMMAND ----------

# Use the catalog
spark.sql(f"USE CATALOG {cfg.catalog}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Schema

# COMMAND ----------

# Create schema
spark.sql(f"""
CREATE SCHEMA IF NOT EXISTS {cfg.catalog}.{cfg.schema}
COMMENT 'Star ratings schema with HEDIS measures, UC functions, and analytics'
""")

print(f"✅ Schema '{cfg.schema}' is ready")

# COMMAND ----------

# Use the schema
spark.sql(f"USE SCHEMA {cfg.schema}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Volume for Knowledge Base Documents

# COMMAND ----------

# Create volume for storing HEDIS guideline documents
spark.sql(f"""
CREATE VOLUME IF NOT EXISTS {cfg.catalog}.{cfg.schema}.{cfg.volume}
COMMENT 'HEDIS guidelines and CMS policy documents for vector search'
""")

print(f"✅ Volume '{cfg.volume}' is ready")
print(f"📁 Volume path: {cfg.volume_path}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Setup

# COMMAND ----------

# Show all tables in the schema
print("Current tables in schema:")
spark.sql(f"SHOW TABLES IN {cfg.catalog}.{cfg.schema}").show()

# COMMAND ----------

print("=" * 80)
print("SETUP COMPLETE!")
print("=" * 80)
print(f"✅ Catalog: {cfg.catalog}")
print(f"✅ Schema: {cfg.schema}")
print(f"✅ Volume: {cfg.volume}")
print(f"✅ Volume Path: {cfg.volume_path}")
print("=" * 80)
print("\nNext steps:")
print("1. Run 02_generate_measures_data to create HEDIS measures")
print("2. Run 03_generate_member_data to create member enrollments")
print("3. Run 04-07 to create UC AI functions")
print("4. Run 08-10 to setup vector search")
print("=" * 80)
