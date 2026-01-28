# Databricks notebook source
# MAGIC %md
# MAGIC # Create Vector Search Index
# MAGIC
# MAGIC Creates vector search index for semantic search of HEDIS guidelines.
# MAGIC All configuration from config.yaml.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Install Dependencies

# COMMAND ----------

# MAGIC %pip install databricks-vectorsearch --quiet
dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Import Configuration

# COMMAND ----------

import sys
import os
sys.path.append(os.path.abspath('..'))
from shared.config import get_config

from databricks.sdk import WorkspaceClient
from databricks.vector_search.client import VectorSearchClient
import time

cfg = get_config()

print(f"Vector Endpoint:    {cfg.vector_endpoint}")
print(f"Knowledge Base:     {cfg.hedis_guidelines_kb}")
print(f"Vector Index:       {cfg.hedis_guidelines_index}")
print(f"Embedding Model:    {cfg.embedding_model}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create/Check Vector Search Endpoint

# COMMAND ----------

w = WorkspaceClient()
vsc = VectorSearchClient(disable_notice=True)

print(f"Checking vector search endpoint: {cfg.vector_endpoint}")

endpoint_exists = False
try:
    endpoint = vsc.get_endpoint(cfg.vector_endpoint)
    endpoint_exists = True
    print(f"✅ Endpoint exists: {cfg.vector_endpoint}")
    print(f"   Status: {endpoint.get('endpoint_status', {}).get('state', 'UNKNOWN')}")
except Exception as e:
    print(f"Endpoint does not exist, will create it")

# Create endpoint if it doesn't exist
if not endpoint_exists:
    print(f"Creating vector search endpoint: {cfg.vector_endpoint}")
    print("⚠️  This takes 10-15 minutes for first-time creation...")
    
    try:
        vsc.create_endpoint(
            name=cfg.vector_endpoint,
            endpoint_type="STANDARD"
        )
        print(f"✅ Endpoint creation started: {cfg.vector_endpoint}")
        
        # Wait for endpoint to be ready
        print("Waiting for endpoint to become ready...")
        max_wait = 900  # 15 minutes
        wait_time = 0
        while wait_time < max_wait:
            try:
                endpoint = vsc.get_endpoint(cfg.vector_endpoint)
                state = endpoint.get('endpoint_status', {}).get('state', 'UNKNOWN')
                if state == 'ONLINE':
                    print(f"✅ Endpoint is ONLINE")
                    break
                print(f"   Status: {state} (waited {wait_time}s)")
                time.sleep(30)
                wait_time += 30
            except:
                time.sleep(30)
                wait_time += 30
    except Exception as e:
        print(f"Error creating endpoint: {e}")
        print("You may need to create it manually in the UI")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Vector Search Index

# COMMAND ----------

print(f"Checking if vector search index exists: {cfg.hedis_guidelines_index}")

# Check if index already exists by listing all indexes
index_exists = False
try:
    # Try to get the index directly
    existing_index = vsc.get_index(cfg.hedis_guidelines_index)
    if existing_index:
        index_exists = True
        status = existing_index.get('status', {}).get('detailed_state', 'UNKNOWN')
        print(f"✅ Index already exists: {cfg.hedis_guidelines_index}")
        print(f"   Status: {status}")
        print(f"   Source: {cfg.hedis_guidelines_kb}")
        print(f"   Embedding model: {cfg.embedding_model}")
        print("\nℹ️  Skipping index creation (already exists)")
        print("   To recreate the index, delete it manually first:")
        print(f"   - Go to Databricks UI > Compute > Vector Search")
        print(f"   - Or run: vsc.delete_index('{cfg.hedis_guidelines_index}')")
        
        # Trigger sync on existing index
        print("\nTriggering sync on existing index...")
        try:
            vsc.get_index(index_name=cfg.hedis_guidelines_index).sync()
            print("✅ Sync triggered successfully")
        except Exception as e:
            print(f"⚠️  Could not trigger sync: {e}")
except Exception as get_error:
    # If get_index fails, try listing all indexes to check
    print(f"get_index failed: {get_error}")
    print("Checking by listing all indexes...")
    try:
        # List all indexes on the endpoint
        indexes_response = w.api_client.do('GET', f'/api/2.0/vector-search/endpoints/{cfg.vector_endpoint}/indexes')
        if indexes_response and 'vector_indexes' in indexes_response:
            for idx in indexes_response['vector_indexes']:
                if idx.get('name') == cfg.hedis_guidelines_index:
                    index_exists = True
                    print(f"✅ Index found in list: {cfg.hedis_guidelines_index}")
                    print("   Skipping creation")
                    break
    except Exception as list_error:
        print(f"Could not list indexes: {list_error}")
    
    if not index_exists:
        print(f"Index confirmed not to exist, will create it")

# Create new index only if it doesn't exist
if not index_exists:
    try:
        index = vsc.create_delta_sync_index(
            endpoint_name=cfg.vector_endpoint,
            source_table_name=cfg.hedis_guidelines_kb,
            index_name=cfg.hedis_guidelines_index,
            pipeline_type="TRIGGERED",
            primary_key="doc_id",
            embedding_source_column="content",
            embedding_model_endpoint_name=cfg.embedding_model
        )
        
        print(f"✅ Index creation started: {cfg.hedis_guidelines_index}")
        print(f"   Endpoint: {cfg.vector_endpoint}")
        print(f"   Source: {cfg.hedis_guidelines_kb}")
        print(f"   Embedding model: {cfg.embedding_model}")
        
        # Wait for index to be ready
        print("\nWaiting for index to be ready (this takes 2-5 minutes)...")
        max_wait = 300
        wait_time = 0
        while wait_time < max_wait:
            try:
                index_info = vsc.get_index(index_name=cfg.hedis_guidelines_index)
                status = index_info.get('status', {}).get('detailed_state', 'UNKNOWN')
                if status == 'ONLINE_TRIGGERED_UPDATE' or status == 'ONLINE':
                    print(f"✅ Index is ready: {status}")
                    break
                print(f"   Status: {status} (waited {wait_time}s)")
                time.sleep(20)
                wait_time += 20
            except Exception as e:
                print(f"   Waiting... ({wait_time}s)")
                time.sleep(20)
                wait_time += 20
        
        # Trigger initial sync
        print("\nTriggering initial sync...")
        vsc.get_index(index_name=cfg.hedis_guidelines_index).sync()
        time.sleep(10)
        
    except Exception as e:
        print(f"❌ Error creating index: {e}")
        raise e
else:
    print(f"\n✅ Vector index handling complete (existing index reused)")


# COMMAND ----------

# MAGIC %md
# MAGIC ## Test Vector Search

# COMMAND ----------

print("Testing vector search...")

try:
    results = vsc.get_index(index_name=cfg.hedis_guidelines_index).similarity_search(
        query_text="How to improve breast cancer screening rates?",
        columns=["doc_id", "doc_type", "title", "content"],
        num_results=3
    )
    
    docs = results.get('result', {}).get('data_array', [])
    print(f"\n✅ Vector search working! Found {len(docs)} results:")
    
    for i, doc in enumerate(docs, 1):
        print(f"\n{i}. {doc[2]}")  # title
        print(f"   Type: {doc[1]}")  # doc_type
        print(f"   Content preview: {doc[3][:150]}...")  # content preview
        
except Exception as e:
    print(f"⚠️  Vector search test failed: {e}")
    print("The index may still be syncing. Try testing again in a few minutes.")

# COMMAND ----------

print("=" * 80)
print("VECTOR SEARCH INDEX CREATED!")
print("=" * 80)
print(f"✅ Endpoint: {cfg.vector_endpoint}")
print(f"✅ Index: {cfg.hedis_guidelines_index}")
print(f"✅ Source: {cfg.hedis_guidelines_kb}")
print(f"✅ Embedding model: {cfg.embedding_model}")
print("=" * 80)


