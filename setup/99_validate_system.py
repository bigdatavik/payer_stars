# Databricks notebook source
# MAGIC %md
# MAGIC # System Validation & Testing
# MAGIC
# MAGIC Comprehensive validation of all payer star ratings components.
# MAGIC Tests data, UC functions, pipelines, and generates health report.

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
# MAGIC ## Setup

# COMMAND ----------

# MAGIC %pip install pyyaml --quiet
dbutils.library.restartPython()

# COMMAND ----------

import sys
import os
sys.path.append(os.path.abspath('..'))
from shared.config import get_config

import json
from datetime import datetime
from pyspark.sql import functions as F

env_from_widget = dbutils.widgets.get("environment")
cfg = get_config(environment=env_from_widget)

print("=" * 80)
print("PAYER STAR RATINGS SYSTEM VALIDATION")
print("=" * 80)
print(f"Catalog: {cfg.catalog}")
print(f"Schema: {cfg.schema}")
print(f"Warehouse: {cfg.warehouse_id}")
print("=" * 80)

# Test results tracking
test_results = []

def record_test(name, status, details="", expected="", actual=""):
    """Record a test result"""
    test_results.append({
        "test_name": name,
        "status": status,  # PASS, FAIL, WARNING
        "details": details,
        "expected": expected,
        "actual": actual,
        "timestamp": datetime.now()
    })
    
    icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{icon} {name}: {status}")
    if details:
        print(f"   {details}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test 1: Catalog & Schema Access

# COMMAND ----------

print("\n" + "=" * 80)
print("TEST 1: CATALOG & SCHEMA ACCESS")
print("=" * 80)

try:
    spark.sql(f"USE CATALOG {cfg.catalog}")
    spark.sql(f"USE SCHEMA {cfg.schema}")
    record_test("Catalog Access", "PASS", f"Successfully accessed {cfg.catalog}.{cfg.schema}")
except Exception as e:
    record_test("Catalog Access", "FAIL", f"Error: {str(e)}")

# List all tables
try:
    tables_df = spark.sql(f"SHOW TABLES IN {cfg.catalog}.{cfg.schema}")
    tables = [row.tableName for row in tables_df.collect()]
    record_test("List Tables", "PASS", f"Found {len(tables)} tables", "≥7", str(len(tables)))
    print(f"\nTables found: {', '.join(tables)}")
except Exception as e:
    record_test("List Tables", "FAIL", f"Error: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test 2: Data Tables Validation

# COMMAND ----------

print("\n" + "=" * 80)
print("TEST 2: DATA TABLES VALIDATION")
print("=" * 80)

# Expected tables and row counts
expected_tables = {
    "measures_data": 45,
    "member_enrollments": 50000,
    "hedis_docs_staging": 5,
    "hedis_guidelines_kb": 20,  # ~25 chunks
    "star_analysis": 1,  # At least 1
    "star_predictions": 1,  # At least 1
    "config_genie": 1
}

for table_name, min_expected_rows in expected_tables.items():
    try:
        count = spark.table(f"{cfg.catalog}.{cfg.schema}.{table_name}").count()
        
        if count >= min_expected_rows:
            record_test(
                f"Table: {table_name}", 
                "PASS", 
                f"Row count: {count:,}", 
                f"≥{min_expected_rows}", 
                str(count)
            )
        else:
            record_test(
                f"Table: {table_name}", 
                "WARNING", 
                f"Row count: {count:,} (expected ≥{min_expected_rows})", 
                f"≥{min_expected_rows}", 
                str(count)
            )
    except Exception as e:
        record_test(f"Table: {table_name}", "FAIL", f"Error: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test 3: Data Quality Checks

# COMMAND ----------

print("\n" + "=" * 80)
print("TEST 3: DATA QUALITY CHECKS")
print("=" * 80)

# Test measures_data
try:
    measures_df = spark.table(f"{cfg.catalog}.{cfg.schema}.measures_data")
    
    # Check for nulls in key columns
    null_checks = measures_df.select([
        F.count(F.when(F.col("measure_id").isNull(), 1)).alias("measure_id_nulls"),
        F.count(F.when(F.col("measure_name").isNull(), 1)).alias("measure_name_nulls"),
        F.count(F.when(F.col("performance_rate").isNull(), 1)).alias("performance_rate_nulls"),
        F.count(F.when(F.col("target_benchmark").isNull(), 1)).alias("target_nulls")
    ]).collect()[0]
    
    total_nulls = sum([null_checks[col] for col in null_checks.asDict().keys()])
    
    if total_nulls == 0:
        record_test("Measures: No Nulls", "PASS", "All key columns populated", "0", "0")
    else:
        record_test("Measures: No Nulls", "WARNING", f"Found {total_nulls} nulls", "0", str(total_nulls))
    
    # Check gap severity distribution
    severity_df = measures_df.groupBy("gap_severity").count()
    print(f"\nGap Severity Distribution:")
    severity_df.show()
    
    record_test("Measures: Gap Severity", "PASS", "Gap severity calculated")
    
except Exception as e:
    record_test("Measures: Data Quality", "FAIL", f"Error: {str(e)}")

# Test member_enrollments
try:
    members_df = spark.table(f"{cfg.catalog}.{cfg.schema}.member_enrollments")
    
    # Check age distribution
    age_stats = members_df.select(
        F.min("age").alias("min_age"),
        F.max("age").alias("max_age"),
        F.avg("age").alias("avg_age")
    ).collect()[0]
    
    if age_stats.min_age >= 18 and age_stats.max_age <= 120:
        record_test(
            "Members: Age Range", 
            "PASS", 
            f"Ages: {age_stats.min_age}-{age_stats.max_age} (avg: {age_stats.avg_age:.1f})",
            "18-120",
            f"{age_stats.min_age}-{age_stats.max_age}"
        )
    else:
        record_test("Members: Age Range", "WARNING", f"Unusual age range: {age_stats.min_age}-{age_stats.max_age}")
    
except Exception as e:
    record_test("Members: Data Quality", "FAIL", f"Error: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test 4: UC Functions Testing

# COMMAND ----------

print("\n" + "=" * 80)
print("TEST 4: UC FUNCTIONS TESTING")
print("=" * 80)

# Test 4.1: star_measure_classify
print("\n--- Test 4.1: star_measure_classify ---")
try:
    result = spark.sql(f"""
        SELECT {cfg.catalog}.{cfg.schema}.star_measure_classify(
            'BCS: Breast Cancer Screening, Performance 62%, Target 75%, Gap 13%, Critical severity'
        ) AS result
    """).collect()[0].result
    
    # Parse JSON result
    result_json = json.loads(result)
    
    if "classification" in result_json and "confidence" in result_json:
        record_test(
            "UC Function: classify", 
            "PASS", 
            f"Classification: {result_json['classification']}, Confidence: {result_json['confidence']}"
        )
        print(f"   Full result: {json.dumps(result_json, indent=2)}")
    else:
        record_test("UC Function: classify", "WARNING", "Missing expected fields in response")
        
except Exception as e:
    record_test("UC Function: classify", "FAIL", f"Error: {str(e)}")

# Test 4.2: star_gap_analyze
print("\n--- Test 4.2: star_gap_analyze ---")
try:
    result = spark.sql(f"""
        SELECT {cfg.catalog}.{cfg.schema}.star_gap_analyze(
            'CDC: Diabetes Care, Performance 68%, Target 80%, Gap 12%'
        ) AS result
    """).collect()[0].result
    
    result_json = json.loads(result)
    
    if "root_causes" in result_json:
        record_test(
            "UC Function: analyze", 
            "PASS", 
            f"Found {len(result_json['root_causes'])} root causes"
        )
        print(f"   Root causes: {result_json['root_causes'][:2]}")
    else:
        record_test("UC Function: analyze", "WARNING", "Missing root_causes in response")
        
except Exception as e:
    record_test("UC Function: analyze", "FAIL", f"Error: {str(e)}")

# Test 4.3: star_improvement_recommend
print("\n--- Test 4.3: star_improvement_recommend ---")
try:
    result = spark.sql(f"""
        SELECT {cfg.catalog}.{cfg.schema}.star_improvement_recommend(
            'BCS: Performance 62%, Target 75%, Gap 13%',
            '{{"root_causes": ["Low outreach", "Access barriers"]}}'
        ) AS result
    """).collect()[0].result
    
    result_json = json.loads(result)
    
    if "recommendations" in result_json:
        record_test(
            "UC Function: recommend", 
            "PASS", 
            f"Generated {len(result_json['recommendations'])} recommendations"
        )
        print(f"   First recommendation: {result_json['recommendations'][0] if result_json['recommendations'] else 'None'}")
    else:
        record_test("UC Function: recommend", "WARNING", "Missing recommendations in response")
        
except Exception as e:
    record_test("UC Function: recommend", "FAIL", f"Error: {str(e)}")

# Test 4.4: star_explain
print("\n--- Test 4.4: star_explain ---")
try:
    result = spark.sql(f"""
        SELECT {cfg.catalog}.{cfg.schema}.star_explain(
            'CBP: Blood Pressure Control, Performance 65%, Target 78%, Gap 13%',
            'High member impact measure'
        ) AS result
    """).collect()[0].result
    
    if len(result) > 50:  # Explanation should be substantial
        record_test(
            "UC Function: explain", 
            "PASS", 
            f"Generated {len(result)} character explanation"
        )
        print(f"   Preview: {result[:100]}...")
    else:
        record_test("UC Function: explain", "WARNING", "Explanation seems too short")
        
except Exception as e:
    record_test("UC Function: explain", "FAIL", f"Error: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test 5: Knowledge Base Validation

# COMMAND ----------

print("\n" + "=" * 80)
print("TEST 5: KNOWLEDGE BASE VALIDATION")
print("=" * 80)

# Check staging documents
try:
    docs_df = spark.table(f"{cfg.catalog}.{cfg.schema}.hedis_docs_staging")
    doc_types = docs_df.select("doc_type").distinct().collect()
    doc_type_list = [row.doc_type for row in doc_types]
    
    record_test(
        "KB: Staging Docs", 
        "PASS", 
        f"Found {len(doc_type_list)} document types: {', '.join(doc_type_list)}"
    )
    
    # Sample a document
    sample = docs_df.select("title", F.length("content").alias("content_length")).limit(1).collect()[0]
    print(f"   Sample doc: {sample.title} ({sample.content_length} chars)")
    
except Exception as e:
    record_test("KB: Staging Docs", "FAIL", f"Error: {str(e)}")

# Check chunked documents
try:
    chunks_df = spark.table(f"{cfg.catalog}.{cfg.schema}.hedis_guidelines_kb")
    
    # Check chunk statistics
    chunk_stats = chunks_df.select(
        F.count("*").alias("total_chunks"),
        F.avg("char_count").alias("avg_chunk_size"),
        F.min("char_count").alias("min_chunk_size"),
        F.max("char_count").alias("max_chunk_size")
    ).collect()[0]
    
    record_test(
        "KB: Chunks", 
        "PASS", 
        f"{chunk_stats.total_chunks} chunks, avg size: {chunk_stats.avg_chunk_size:.0f} chars"
    )
    
    # Check for duplicates
    duplicate_count = chunks_df.groupBy("doc_id").count().filter(F.col("count") > 1).count()
    if duplicate_count == 0:
        record_test("KB: No Duplicates", "PASS", "No duplicate chunks found", "0", "0")
    else:
        record_test("KB: No Duplicates", "WARNING", f"Found {duplicate_count} duplicate chunks")
    
except Exception as e:
    record_test("KB: Chunks", "FAIL", f"Error: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test 6: Vector Search Status

# COMMAND ----------

print("\n" + "=" * 80)
print("TEST 6: VECTOR SEARCH STATUS")
print("=" * 80)

try:
    # Check if vector search was set up
    status_df = spark.table(f"{cfg.catalog}.{cfg.schema}.vector_search_status")
    status = status_df.select("status", "message").collect()[0]
    
    if status.status == "SKIPPED":
        record_test(
            "Vector Search", 
            "WARNING", 
            "Vector search not yet configured - run notebook 10 on cluster",
            "ONLINE",
            "SKIPPED"
        )
        print(f"   Message: {status.message}")
        print(f"   Action: Run setup/10_create_vector_index on a cluster to enable")
    else:
        record_test("Vector Search", "PASS", "Vector search configured")
        
except Exception as e:
    # Table might not exist if vector search ran successfully
    record_test(
        "Vector Search", 
        "WARNING", 
        "Cannot determine status - check manually",
        "ONLINE",
        "UNKNOWN"
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test 7: Analysis Pipeline

# COMMAND ----------

print("\n" + "=" * 80)
print("TEST 7: ANALYSIS PIPELINE")
print("=" * 80)

# Check star_analysis table
try:
    analysis_df = spark.table(f"{cfg.catalog}.{cfg.schema}.star_analysis")
    analysis_count = analysis_df.count()
    
    if analysis_count > 0:
        record_test(
            "Analysis: Results", 
            "PASS", 
            f"Found {analysis_count} analyzed measures"
        )
        
        # Show sample
        print("\nSample analysis:")
        analysis_df.select("measure_id", "classification", "priority").limit(3).show(truncate=False)
    else:
        record_test("Analysis: Results", "WARNING", "No analysis results found")
        
except Exception as e:
    record_test("Analysis: Results", "FAIL", f"Error: {str(e)}")

# Check star_predictions table
try:
    predictions_df = spark.table(f"{cfg.catalog}.{cfg.schema}.star_predictions")
    prediction_count = predictions_df.count()
    
    if prediction_count > 0:
        record_test(
            "Predictions: Results", 
            "PASS", 
            f"Found {prediction_count} predictions"
        )
        
        # Show sample
        print("\nSample predictions:")
        predictions_df.select("measure_id", "current_stars", "predicted_stars").limit(3).show(truncate=False)
    else:
        record_test("Predictions: Results", "WARNING", "No predictions found")
        
except Exception as e:
    record_test("Predictions: Results", "FAIL", f"Error: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test 8: Performance Testing

# COMMAND ----------

print("\n" + "=" * 80)
print("TEST 8: PERFORMANCE TESTING")
print("=" * 80)

import time

# Test query performance
try:
    start = time.time()
    count = spark.table(f"{cfg.catalog}.{cfg.schema}.measures_data").count()
    query_time = time.time() - start
    
    if query_time < 5:
        record_test("Performance: Table Scan", "PASS", f"Query time: {query_time:.2f}s", "<5s", f"{query_time:.2f}s")
    else:
        record_test("Performance: Table Scan", "WARNING", f"Query time: {query_time:.2f}s (slow)")
        
except Exception as e:
    record_test("Performance: Table Scan", "FAIL", f"Error: {str(e)}")

# Test UC function performance
try:
    start = time.time()
    spark.sql(f"""
        SELECT {cfg.catalog}.{cfg.schema}.star_measure_classify('Test: Performance 70%, Target 80%, Gap 10%')
    """).collect()
    function_time = time.time() - start
    
    if function_time < 30:
        record_test("Performance: UC Function", "PASS", f"Response time: {function_time:.2f}s", "<30s", f"{function_time:.2f}s")
    else:
        record_test("Performance: UC Function", "WARNING", f"Response time: {function_time:.2f}s (slow)")
        
except Exception as e:
    record_test("Performance: UC Function", "FAIL", f"Error: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Validation Report

# COMMAND ----------

print("\n" + "=" * 80)
print("VALIDATION REPORT SUMMARY")
print("=" * 80)

# Count results
total_tests = len(test_results)
passed = sum(1 for t in test_results if t["status"] == "PASS")
failed = sum(1 for t in test_results if t["status"] == "FAIL")
warnings = sum(1 for t in test_results if t["status"] == "WARNING")

print(f"\nTotal Tests: {total_tests}")
print(f"✅ Passed: {passed} ({passed/total_tests*100:.1f}%)")
print(f"❌ Failed: {failed} ({failed/total_tests*100:.1f}%)")
print(f"⚠️  Warnings: {warnings} ({warnings/total_tests*100:.1f}%)")

# Calculate health score
health_score = (passed / total_tests) * 100
print(f"\n🎯 Overall Health Score: {health_score:.1f}%")

if health_score >= 90:
    print("🎉 Status: EXCELLENT - System fully operational")
elif health_score >= 75:
    print("✅ Status: GOOD - Minor issues to address")
elif health_score >= 60:
    print("⚠️  Status: FAIR - Some components need attention")
else:
    print("❌ Status: POOR - Major issues require fixing")

# Show failed/warning tests
if failed > 0 or warnings > 0:
    print("\n" + "=" * 80)
    print("ISSUES TO ADDRESS:")
    print("=" * 80)
    
    for test in test_results:
        if test["status"] in ["FAIL", "WARNING"]:
            icon = "❌" if test["status"] == "FAIL" else "⚠️"
            print(f"\n{icon} {test['test_name']}")
            print(f"   {test['details']}")

# Create report DataFrame
report_df = spark.createDataFrame(test_results)
report_df.write.mode("overwrite").saveAsTable(f"{cfg.catalog}.{cfg.schema}.validation_report")

print(f"\n✅ Detailed report saved to: {cfg.catalog}.{cfg.schema}.validation_report")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Next Steps

# COMMAND ----------

print("\n" + "=" * 80)
print("RECOMMENDED NEXT STEPS")
print("=" * 80)

next_steps = []

# Check if vector search needs setup
vector_warning = any(t["test_name"] == "Vector Search" and t["status"] == "WARNING" for t in test_results)
if vector_warning:
    next_steps.append("1. Run setup/10_create_vector_index on a cluster to enable vector search")

# Check for other warnings
if warnings > 0:
    next_steps.append(f"2. Review {warnings} warning(s) above and address as needed")

# Check for failures
if failed > 0:
    next_steps.append(f"3. Fix {failed} failed test(s) immediately")

# Always suggest these
next_steps.append(f"{len(next_steps)+1}. Deploy Streamlit app for interactive demo")
next_steps.append(f"{len(next_steps)+1}. Set up Genie Space for natural language queries (optional)")

print("\n" + "\n".join(next_steps))

print("\n" + "=" * 80)
print("VALIDATION COMPLETE!")
print("=" * 80)


