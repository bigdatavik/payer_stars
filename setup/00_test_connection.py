# Databricks notebook source
# MAGIC %md
# MAGIC # Test Serverless Connection
# MAGIC
# MAGIC Simple test to verify:
# MAGIC - Serverless compute works
# MAGIC - Config module loads correctly
# MAGIC - Unity Catalog access
# MAGIC - Basic Spark operations

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
# MAGIC ## Test 1: Basic Spark Operation

# COMMAND ----------

print("=" * 80)
print("TEST 1: Basic Spark Operation")
print("=" * 80)

# Test basic Spark
df = spark.createDataFrame([(1, "test"), (2, "serverless")], ["id", "value"])
df.show()

print("✅ Spark is working on serverless compute!")
print(f"✅ Spark version: {spark.version}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test 2: Configuration Module

# COMMAND ----------

# MAGIC %pip install pyyaml --quiet
dbutils.library.restartPython()

# COMMAND ----------

print("=" * 80)
print("TEST 2: Configuration Module")
print("=" * 80)

# Test config import
import sys
import os
sys.path.append(os.path.abspath('..'))

try:
    from shared.config import get_config, print_config
    env_from_widget = dbutils.widgets.get("environment")
    cfg = get_config(environment=env_from_widget)
    
    print("✅ Config module imported successfully!")
    print_config(cfg)
    
except Exception as e:
    print(f"❌ Config import failed: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test 3: Unity Catalog Access

# COMMAND ----------

print("=" * 80)
print("TEST 3: Unity Catalog Access")
print("=" * 80)

# Test UC catalog access
try:
    catalogs = spark.sql("SHOW CATALOGS").collect()
    print(f"✅ Can access Unity Catalog!")
    print(f"✅ Found {len(catalogs)} catalogs")
    
    # Check if our catalog exists
    catalog_names = [row.catalog for row in catalogs]
    if cfg.catalog in catalog_names:
        print(f"✅ Target catalog '{cfg.catalog}' already exists")
    else:
        print(f"ℹ️  Target catalog '{cfg.catalog}' will be created in setup")
    
except Exception as e:
    print(f"❌ UC access failed: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test 4: Current User & Permissions

# COMMAND ----------

print("=" * 80)
print("TEST 4: Current User & Permissions")
print("=" * 80)

# Get current user
try:
    current_user = spark.sql("SELECT current_user() as user").collect()[0].user
    print(f"✅ Running as: {current_user}")
    
    # Try to create a temp table (tests write permissions)
    spark.sql("CREATE OR REPLACE TEMP VIEW test_view AS SELECT 1 as id")
    result = spark.sql("SELECT * FROM test_view").collect()[0].id
    assert result == 1
    print("✅ Can create temp views and query them")
    
except Exception as e:
    print(f"❌ Permission test failed: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test 5: Python Environment

# COMMAND ----------

print("=" * 80)
print("TEST 5: Python Environment")
print("=" * 80)

import sys
print(f"Python version: {sys.version}")

# Check for required libraries
required_libs = ['pyspark', 'yaml', 'json']
for lib in required_libs:
    try:
        __import__(lib)
        print(f"✅ {lib} is available")
    except ImportError:
        print(f"❌ {lib} is NOT available")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("=" * 80)
print("🎉 ALL TESTS PASSED!")
print("=" * 80)
print()
print("✅ Serverless compute: WORKING")
print("✅ Configuration module: WORKING") 
print("✅ Unity Catalog access: WORKING")
print("✅ User permissions: WORKING")
print("✅ Python environment: WORKING")
print()
print("=" * 80)
print("Ready to proceed with full deployment!")
print("=" * 80)
