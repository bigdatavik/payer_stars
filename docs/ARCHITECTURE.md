# 🏗️ System Architecture Documentation
## CMS Star Ratings AI Analytics Platform

**Version:** 1.0  
**Last Updated:** January 2026  
**Platform:** Databricks Data Intelligence Platform

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Component Breakdown](#component-breakdown)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Design Decisions](#design-decisions)
7. [Deployment Architecture](#deployment-architecture)
8. [Security & Governance](#security--governance)
9. [Scalability & Performance](#scalability--performance)
10. [Integration Points](#integration-points)

---

## Architecture Overview

### System Purpose

An intelligent Medicare Star Ratings analysis and improvement system that:
- Analyzes HEDIS measure performance gaps in 60 seconds (vs 3 weeks manually)
- Provides AI-powered root cause analysis and recommendations
- Enables natural language data exploration
- Models what-if scenarios for star rating improvements
- Delivers evidence-based insights with full citations

### Core Capabilities

**AI-Powered Analysis:**
- LangGraph StateGraph orchestration with conditional routing
- Unity Catalog AI Functions (Claude Sonnet 4.5) for serverless LLM inference
- Vector Search over HEDIS guideline knowledge base

**Natural Language Interface:**
- Databricks Genie for SQL-free data exploration
- Conversational analytics for quality teams

**Strategic Planning:**
- Interactive Star Ratings calculator with CMS 2026 methodology
- What-if scenario modeling with real-time impact calculation
- Prioritized action plans with ROI ranking

**Unified Platform:**
- Single Databricks lakehouse (no data movement)
- Governed by Unity Catalog
- Serverless auto-scaling
- One-command deployment

---

## High-Level Architecture

### Architecture Diagram

![Databricks Data Intelligence Platform Architecture](../linkedin/screenshots/15_architecture_diagram.png)

*Reference: Adapted from [Microsoft Azure Databricks Lakehouse Reference Architecture](https://learn.microsoft.com/en-us/azure/databricks/lakehouse-architecture/reference)*

### Conceptual Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  Streamlit Dashboards (Databricks Apps)                     │
│  - Measure Analysis  - Performance Dashboard                │
│  - Star Calculator   - Architecture Viz                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   ORCHESTRATION LAYER                        │
│  LangGraph StateGraph                                        │
│  - Intent Classification  - Conditional Routing             │
│  - Function Calling      - State Management                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      AI LAYER                                │
│  Unity Catalog AI Functions                                  │
│  - uc_star_classify    - uc_star_analyze                    │
│  - uc_star_recommend   - uc_star_explain                    │
│                                                              │
│  Vector Search                                               │
│  - HEDIS Guidelines Index (databricks-bge-large-en)         │
│  - Semantic retrieval with citations                        │
│                                                              │
│  Databricks Genie                                            │
│  - Natural language to SQL                                   │
│  - Conversation API with context                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER                               │
│  Unity Catalog: HEDIS measures, members, guidelines         │
│  - measures_data (41 HEDIS measures)                        │
│  - members_data (synthetic population)                      │
│  - star_analysis (AI outputs)                               │
│  - hedis_guidelines (knowledge base)                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  GOVERNANCE LAYER                            │
│  Unity Catalog                                               │
│  - Fine-grained access control                              │
│  - Audit logging & lineage                                  │
│  - Service Principal authentication                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. Presentation Layer (Streamlit)

#### Streamlit Dashboards

**Location:** `app/pages/*.py`

**Pages:**
1. **Home (`app.py`):** Welcome page with quick links and overview
2. **Measure Analysis (`1_measure_analysis.py`):** AI-powered gap analysis interface
3. **Performance Dashboard (`2_performance_dashboard.py`):** Overall metrics + Genie
4. **Star Ratings Calculator (`4_star_ratings_calculator.py`):** Scenario modeling
5. **Architecture (`0_architecture.py`):** System visualization
6. **Setup Resources (`5_setup_resources.py`):** Quick links to notebooks/jobs

**Key Features:**
- Wide layout for maximum screen utilization
- Tab-based UI for organized information display
- Quick question buttons for common queries
- Service Principal authentication via environment variables
- Real-time chart generation (Plotly)

**Technology:**
- **Streamlit:** Python-based web framework
- **Databricks Apps:** Managed deployment platform
- **Authentication:** Service Principal (no manual login)

#### User Experience Flow

```
User Opens App
    ↓
Home Page (Overview)
    ↓
User Selects Measure → Measure Analysis Page
    ↓
Clicks "Analyze with StateGraph Agent"
    ↓
45-60 second wait (loading spinner)
    ↓
Results Display:
    - 4-tab gap analysis
    - Vector search results
    - Recommendations
```

---

### 2. Orchestration Layer (LangGraph)

#### StateGraph Workflow

**Location:** `app/utils/state_graph_agent.py`

**Architecture Pattern:** State machine with conditional routing

**Workflow Definition:**

```python
workflow = StateGraph(State)

# Nodes (discrete steps)
workflow.add_node("classify_intent", classify_intent)
workflow.add_node("gap_analysis", analyze_gaps)
workflow.add_node("recommendations", generate_recommendations)
workflow.add_node("knowledge_search", search_guidelines)

# Conditional edges (routing logic)
workflow.add_conditional_edges(
    "classify_intent",
    route_to_pipeline,
    {
        "gap_analysis": "gap_analysis",
        "recommendations": "recommendations",
        "knowledge_only": "knowledge_search"
    }
)

# Entry point
workflow.set_entry_point("classify_intent")

# Compile
app = workflow.compile()
```

**State Schema:**

```python
class State(TypedDict):
    query: str                    # User input
    measure_data: str            # Measure performance metrics
    intent: str                  # Classified intent
    classification: dict         # Measure classification
    gaps: dict                   # Gap analysis results
    recommendations: list        # AI recommendations
    knowledge: list             # Retrieved guidelines
    error: Optional[str]        # Error handling
```

**Why StateGraph?**
- **Conditional Logic:** Route based on intent (not just linear chains)
- **Modularity:** Each node is independently testable
- **Transparency:** Full execution trace for debugging
- **Flexibility:** Easy to add new nodes/pipelines

---

### 3. AI Layer

#### A. Unity Catalog AI Functions

**Purpose:** Serverless LLM inference with governance

**Function Definitions:**

**1. `uc_star_classify` - Intent Classification**

```sql
CREATE FUNCTION uc_star_classify(
  measure_data STRING,
  user_query STRING
)
RETURNS STRING
LANGUAGE PYTHON
AS $$
  # Classify query intent
  # Returns: JSON with intent + entities
  
  import anthropic
  client = anthropic.Anthropic(api_key=...)
  
  response = client.messages.create(
    model="claude-sonnet-4.5",
    messages=[{
      "role": "user",
      "content": f"Classify: {user_query}"
    }]
  )
  
  return response.content[0].text
$$
```

**2. `uc_star_analyze` - Gap Analysis**

```sql
CREATE FUNCTION uc_star_analyze(
  measure_data STRING,
  user_query STRING
)
RETURNS STRING
LANGUAGE PYTHON
AS $$
  # Analyze performance gaps
  # Returns: JSON with root_causes, populations, barriers, data_quality
$$
```

**3. `uc_star_recommend` - Recommendations**

```sql
CREATE FUNCTION uc_star_recommend(
  measure_data STRING,
  gap_analysis STRING,
  knowledge_context STRING
)
RETURNS STRING
LANGUAGE PYTHON
AS $$
  # Generate evidence-based recommendations
  # Returns: JSON with prioritized interventions
$$
```

**4. `uc_star_explain` - Explanations**

```sql
CREATE FUNCTION uc_star_explain(
  measure_data STRING,
  recommendation STRING
)
RETURNS STRING
LANGUAGE PYTHON
AS $$
  # Explain recommendation rationale
  # Returns: Plain text explanation
$$
```

**Benefits:**
- ✅ **Governed:** Unity Catalog access control
- ✅ **Serverless:** Auto-scaling, no ops
- ✅ **Audited:** Every call logged
- ✅ **No API Keys:** Managed authentication
- ✅ **Co-located:** Same platform as data

#### B. Vector Search

**Purpose:** Semantic search over HEDIS guideline knowledge base

**Index Configuration:**

```python
# Vector Search Index
index_name = "hedis_guidelines_index"
embedding_model = "databricks-bge-large-en"
endpoint = "one-env-shared-endpoint-2"

# Source table
source_table = f"{catalog}.{schema}.hedis_guidelines"
columns = ["doc_id", "doc_title", "text_chunk"]
```

**Knowledge Base:**
- **500+ pages** of HEDIS technical specifications
- **Chunked:** 512-1024 tokens per chunk
- **Embeddings:** BGE-large-en (best-in-class for semantic search)
- **Index Type:** Delta Sync (auto-updates with source table)

**Query Pattern:**

```sql
SELECT 
  doc_id,
  doc_title,
  text_chunk,
  similarity_score
FROM VECTOR_SEARCH(
  index => 'hedis_guidelines_index',
  query => 'best practices for breast cancer screening',
  num_results => 3
)
ORDER BY similarity_score DESC
```

**Why SQL Function?**
- Service Principal authentication (works in Databricks Apps)
- No SDK complexity
- SQL is universally supported
- Easier to debug

#### C. Databricks Genie

**Purpose:** Natural language to SQL interface

**Configuration:**

```python
genie_space_id = os.getenv("GENIE_SPACE_ID")
catalog = "payer_stars_dev"
schema = "star_ratings"
```

**Conversation Flow:**

```python
# Start conversation
response = requests.post(
    f"{workspace_url}/api/2.0/genie/spaces/{space_id}/start-conversation",
    json={"content": user_query}
)
conversation_id = response.json()["conversation_id"]
message_id = response.json()["message_id"]

# Poll for results
while True:
    status = requests.get(
        f"{workspace_url}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}"
    )
    if status.json()["status"] == "COMPLETED":
        break
    time.sleep(2)

# Get results
results = status.json()["attachments"]
# Returns: text_response, sql_query, query_result
```

**Capabilities:**
- Translates natural language to SQL
- Understands Unity Catalog schema
- Maintains conversation context
- Returns formatted results
- Validates queries before execution

---

### 4. Data Layer

#### Unity Catalog Tables

**Catalog Structure:**

```
payer_stars_dev (catalog)
└── star_ratings (schema)
    ├── measures_data          # 41 HEDIS measures
    ├── members_data           # Synthetic member population
    ├── star_analysis          # AI analysis outputs
    ├── star_predictions       # Predictive models
    ├── hedis_guidelines       # Knowledge base
    ├── config_app             # App configuration
    └── config_genie           # Genie space configuration
```

**Table: `measures_data`**

```sql
CREATE TABLE measures_data (
  measure_id STRING,              -- BCS, COL, CDC, etc.
  measure_name STRING,            -- Full measure name
  domain STRING,                  -- Effectiveness, Part D, etc.
  weight INT,                     -- 1, 2, or 3
  star_category STRING,           -- Outcomes, Experience, Preventive
  performance_rate DOUBLE,        -- Current performance (0-1)
  target_benchmark DOUBLE,        -- Target performance (0-1)
  gap DOUBLE,                     -- target - performance
  gap_severity STRING,            -- Critical, Moderate, Minor, None
  numerator INT,                  -- Members meeting criteria
  denominator INT,                -- Eligible members
  star_rating DOUBLE,             -- Individual measure stars (1-5)
  weighted_score DOUBLE,          -- star_rating × weight
  measurement_year INT,           -- 2024
  plan_id STRING,                 -- H1234-001
  last_updated TIMESTAMP
)
USING DELTA
LOCATION 's3://...'
```

**Table: `hedis_guidelines`**

```sql
CREATE TABLE hedis_guidelines (
  doc_id STRING,                  -- Unique document ID
  doc_title STRING,               -- Document title
  text_chunk STRING,              -- Content chunk (512-1024 tokens)
  chunk_index INT,                -- Chunk sequence number
  embedding ARRAY<DOUBLE>,        -- BGE-large-en embedding (1024 dims)
  source_file STRING,             -- Original PDF filename
  page_number INT,                -- Page in original document
  created_at TIMESTAMP
)
USING DELTA
```

**Table: `star_analysis`**

```sql
CREATE TABLE star_analysis (
  analysis_id STRING,             -- UUID
  measure_id STRING,              -- BCS, CDC, etc.
  user_query STRING,              -- Original question
  classification JSON,            -- Intent classification
  root_causes JSON,               -- Gap analysis - causes
  affected_populations JSON,      -- Gap analysis - populations
  barriers JSON,                  -- Gap analysis - barriers
  data_quality JSON,              -- Gap analysis - data issues
  recommendations JSON,           -- Prioritized interventions
  knowledge_docs JSON,            -- Retrieved guidelines
  created_at TIMESTAMP,
  created_by STRING               -- Service Principal
)
USING DELTA
```

#### Data Volume (Sample)

| Table | Rows | Size | Update Frequency |
|-------|------|------|-----------------|
| measures_data | 41 | ~100 KB | Monthly (real: nightly) |
| members_data | 50,000 | ~50 MB | Annual |
| star_analysis | ~1,000 | ~10 MB | Per query |
| hedis_guidelines | ~2,000 | ~500 MB | Annually |

---

### 5. Governance Layer

#### Unity Catalog

**Purpose:** Centralized governance for data and AI assets

**Key Features:**

**1. Fine-Grained Access Control:**

```sql
-- Grant read access to quality team
GRANT SELECT ON TABLE measures_data TO `quality_team`;

-- Grant function execution to analysts
GRANT EXECUTE ON FUNCTION uc_star_analyze TO `quality_analysts`;

-- Deny access to PII columns
DENY SELECT(member_id, member_name) ON TABLE members_data TO `contractors`;
```

**2. Audit Logging:**

All access is logged:
- Who accessed what data
- When it was accessed
- What queries were run
- What functions were called

```sql
-- Query audit logs
SELECT 
  user_name,
  action_name,
  request_params,
  event_time
FROM system.access.audit
WHERE table_name = 'measures_data'
ORDER BY event_time DESC
LIMIT 100
```

**3. Data Lineage:**

Automatic lineage tracking:
- Table → Function → Analysis output
- Vector Search → Recommendations
- Genie queries → Dashboards

**4. Service Principal Authentication:**

```python
# No user credentials in code
# Service Principal auth via environment variables
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
```

---

## Data Flow

### End-to-End Flow: Gap Analysis Query

**Step-by-Step:**

```
1. USER ACTION
   └─> User selects "BCS - Breast Cancer Screening"
   └─> Clicks "Analyze with StateGraph Agent"
   
2. STREAMLIT APP
   └─> Prepares measure_data (performance metrics)
   └─> Calls state_graph_agent.analyze_measure()
   
3. LANGGRAPH STATEGRAPH
   └─> Entry: classify_intent(query)
   │   └─> Calls uc_star_classify() UC Function
   │   └─> Returns: {intent: "gap_analysis"}
   │
   └─> Route: conditional_edge → "gap_analysis"
   │
   └─> Node: analyze_gaps()
   │   └─> Calls uc_star_analyze() UC Function
   │   └─> Returns: {root_causes, populations, barriers, data_quality}
   │
   └─> Node: search_guidelines()
   │   └─> Executes VECTOR_SEARCH() SQL function
   │   └─> Returns: Top 3 relevant guideline chunks
   │
   └─> Node: generate_recommendations()
       └─> Calls uc_star_recommend() UC Function
       └─> Passes: measure_data + gap_analysis + guideline_context
       └─> Returns: Prioritized intervention list

4. RESPONSE TO STREAMLIT
   └─> Structured JSON result
   
5. UI DISPLAY
   └─> Parse JSON → Render 4 tabs
   │   ├─> Root Causes tab
   │   ├─> Affected Populations tab
   │   ├─> Performance Barriers tab
   │   └─> Data Quality Issues tab
   │
   └─> Display Vector Search results (expandable)
   └─> Show Recommendations list
   
6. AUDIT & LINEAGE
   └─> Unity Catalog logs:
       - Function calls
       - Data access
       - User actions
       - Timestamps

Total Time: 45-60 seconds
```

### Data Pipeline: Setup to Runtime

```
SETUP PHASE (One-time):
├─> 1. Generate synthetic data (setup/02_generate_measures_data.py)
│   └─> Create 41 HEDIS measures with realistic performance
│
├─> 2. Create Unity Catalog AI Functions (setup/04-07_uc_*.py)
│   └─> Deploy 4 functions: classify, analyze, recommend, explain
│
├─> 3. Build Vector Search Index (setup/08_create_knowledge_base.py)
│   └─> Ingest HEDIS PDFs → Chunk → Embed → Index
│
├─> 4. Configure Genie (setup/14_create_genie_space.py)
│   └─> Create Genie space → Link to catalog
│
└─> 5. Deploy Streamlit App (databricks bundle deploy)
    └─> Package app → Upload to Databricks Apps → Start

RUNTIME PHASE (Per query):
├─> User query → Streamlit
├─> Streamlit → LangGraph
├─> LangGraph → UC Functions + Vector Search
├─> Results → Streamlit → User
└─> All actions logged in Unity Catalog
```

---

## Technology Stack

### Core Platform

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Data Platform** | Databricks Lakehouse | Unified data + AI platform |
| **Governance** | Unity Catalog | Access control, audit, lineage |
| **Storage** | Delta Lake | ACID transactions, time travel |
| **Compute** | Serverless | Auto-scaling compute |

### AI/ML Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | Claude Sonnet 4.5 | Natural language understanding |
| **Orchestration** | LangGraph StateGraph | Conditional workflow routing |
| **RAG** | Vector Search (BGE-large-en) | Semantic guideline retrieval |
| **NL-to-SQL** | Databricks Genie | Natural language queries |

### Application Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit | Interactive dashboards |
| **Deployment** | Databricks Apps | Managed hosting |
| **Auth** | Service Principal | Secure authentication |
| **Visualization** | Plotly | Charts and graphs |

### Development Tools

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **IaC** | Databricks Asset Bundles | Infrastructure-as-code |
| **Config** | YAML | Centralized configuration |
| **Language** | Python 3.10+ | Application code |
| **Testing** | pytest | Unit and integration tests |

---

## Design Decisions

### Decision 1: Why Databricks (vs Multi-Tool Stack)?

**Alternative Considered:**
```
Snowflake (data) + OpenAI (LLM) + Pinecone (vectors) + 
Tableau (BI) + AWS (hosting)
```

**Why Databricks:**
- ✅ **No Data Movement:** Data + AI on same platform
- ✅ **Unified Governance:** One catalog for all assets
- ✅ **Lower Latency:** Co-located compute and storage
- ✅ **Simpler Architecture:** 1 platform vs 5+ tools
- ✅ **Better Debugging:** Single pane of glass
- ✅ **Cost:** Avoid data egress fees

**Trade-offs:**
- ❌ Vendor lock-in (mitigated by Delta Lake open format)
- ❌ Learning curve for Databricks-specific features

### Decision 2: Why LangGraph (vs LangChain)?

**Alternative Considered:**
```python
# LangChain sequential chain
chain = (
    classify_prompt | llm | parse_json |
    analyze_prompt | llm | parse_json |
    recommend_prompt | llm
)
```

**Why LangGraph:**
- ✅ **Conditional Routing:** Route based on intent (if/else logic)
- ✅ **State Management:** Shared state across nodes
- ✅ **Modularity:** Independently testable nodes
- ✅ **Transparency:** Full execution trace
- ✅ **Cycles:** Support for iterative reasoning

**Trade-offs:**
- ❌ More complex than simple chains
- ✅ But necessary for real-world workflows

### Decision 3: Why Unity Catalog Functions (vs Direct API)?

**Alternative Considered:**
```python
# Direct OpenAI API calls
import openai
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": query}]
)
```

**Why UC Functions:**
- ✅ **Governance:** Fine-grained access control
- ✅ **Audit:** Every call logged
- ✅ **No API Keys:** Managed authentication
- ✅ **Cost Tracking:** Per-function usage metrics
- ✅ **Compliance:** Data never leaves Databricks

**Trade-offs:**
- ❌ Databricks-specific (not portable to other clouds easily)
- ✅ But critical for healthcare/regulated industries

### Decision 4: Why Vector Search SQL Function (vs SDK)?

**Alternative Considered:**
```python
from databricks.vector_search.client import VectorSearchClient
client = VectorSearchClient()
results = client.search(index, query, num_results=3)
```

**Why SQL Function:**
- ✅ **Auth-Friendly:** Works with Service Principal in Databricks Apps
- ✅ **Simpler:** No SDK version conflicts
- ✅ **Universal:** SQL works everywhere
- ✅ **Debuggable:** Easy to test in SQL editor

**Trade-offs:**
- ❌ Less feature-rich than SDK
- ✅ But sufficient for our use case

### Decision 5: Why Streamlit (vs React/Vue)?

**Alternative Considered:**
- React + Flask backend
- Vue.js + FastAPI
- Dash (Plotly)

**Why Streamlit:**
- ✅ **Python-Native:** No JavaScript needed
- ✅ **Rapid Development:** 10x faster than React
- ✅ **Databricks Apps:** First-class deployment support
- ✅ **Good Enough UI:** Sufficient for internal tools
- ✅ **Easy Maintenance:** Less code to maintain

**Trade-offs:**
- ❌ Limited customization vs React
- ❌ Refresh-based (not SPA)
- ✅ But perfect for data/analytics apps

---

## Deployment Architecture

### Databricks Asset Bundles (DAB)

**File Structure:**

```
payer_stars/
├── databricks.yml           # Bundle configuration
├── config.yaml             # Environment configs
├── app/                    # Streamlit app
├── setup/                  # Setup notebooks
└── generate_app_yaml.py    # App config generator
```

**Bundle Configuration:**

```yaml
# databricks.yml
bundle:
  name: payer_star_ratings

environments:
  dev:
    mode: development
    workspace:
      host: ${DATABRICKS_HOST}
      profile: ${DATABRICKS_PROFILE}
    
resources:
  jobs:
    setup_pipeline:
      name: "Payer Stars Setup Pipeline"
      tasks:
        - task_key: generate_data
          notebook_task:
            notebook_path: ./setup/02_generate_measures_data
        - task_key: create_functions
          depends_on:
            - task_key: generate_data
          notebook_task:
            notebook_path: ./setup/04_uc_star_classify
```

**Deployment Commands:**

```bash
# Validate configuration
databricks bundle validate

# Deploy to dev environment
databricks bundle deploy -t dev

# Deploy to production
databricks bundle deploy -t prod

# Run setup job
databricks bundle run setup_pipeline -t dev
```

### Multi-Environment Support

**Environments:**

| Environment | Purpose | Configuration |
|-------------|---------|---------------|
| **dev** | Development & testing | `config.yaml` → `environments.dev` |
| **staging** | Pre-production validation | `config.yaml` → `environments.staging` |
| **prod** | Production workloads | `config.yaml` → `environments.prod` |

**Configuration Pattern:**

```yaml
# config.yaml
environments:
  dev:
    catalog: payer_stars_dev
    warehouse_id: dev-warehouse-id
    llm_endpoint: databricks-claude-sonnet-4-5
    
  prod:
    catalog: payer_stars_prod
    warehouse_id: prod-warehouse-id
    llm_endpoint: databricks-claude-sonnet-4-5
```

**Environment Variables:**

```bash
# Generated by generate_app_yaml.py
CATALOG_NAME=payer_stars_dev
SCHEMA_NAME=star_ratings
DATABRICKS_WAREHOUSE_ID=148ccb90800933a1
LLM_ENDPOINT=databricks-claude-sonnet-4-5
VECTOR_ENDPOINT=one-env-shared-endpoint-2
GENIE_SPACE_ID=01234567-89ab-cdef-0123-456789abcdef
```

---

## Security & Governance

### Authentication

**Service Principal:**

```python
# Configured via Databricks Apps
# No hardcoded credentials
token = os.getenv("DATABRICKS_TOKEN")
host = os.getenv("DATABRICKS_HOST")

# Workspace client
w = WorkspaceClient(
    host=host,
    token=token
)
```

**Benefits:**
- ✅ No user passwords
- ✅ Rotatable tokens
- ✅ Scoped permissions
- ✅ Audit trail

### Authorization

**Unity Catalog Permissions:**

```sql
-- Data access
GRANT SELECT ON TABLE measures_data TO `quality_team`;
GRANT SELECT ON SCHEMA star_ratings TO `quality_team`;

-- Function execution
GRANT EXECUTE ON FUNCTION uc_star_analyze TO `quality_team`;

-- Vector search
GRANT SELECT ON TABLE hedis_guidelines TO `quality_team`;
```

### Data Protection

**PII Handling:**
- Member data is **synthetic** (no real PHI/PII)
- In production: Use Delta Lake column masking
- Example:
  ```sql
  CREATE TABLE members_data (
    member_id STRING MASK hash,  -- Hash member IDs
    member_name STRING MASK null, -- Redact names
    ...
  )
  ```

**Data Retention:**
- Analysis results: 90 days
- Audit logs: 2 years (compliance requirement)
- Raw data: 7 years (CMS requirement)

### Compliance

**HIPAA Considerations:**
- Data encrypted at rest (Delta Lake default)
- Encrypted in transit (TLS)
- Audit logs for all access
- Access controls enforced

**SOC 2 / ISO 27001:**
- Databricks platform certified
- Unity Catalog provides controls
- Regular security reviews

---

## Scalability & Performance

### Compute Scaling

**Serverless Compute:**
- Auto-scales from 0 to 100s of workers
- No cluster management
- Pay-per-use pricing

**Performance Characteristics:**

| Component | Latency | Throughput |
|-----------|---------|------------|
| **UC Function Call** | 2-5 seconds | 100s concurrent |
| **Vector Search** | <500ms | 1000s QPS |
| **Genie Query** | 5-15 seconds | 10s concurrent |
| **Streamlit Page Load** | 1-2 seconds | 100s users |

### Data Scaling

**Current Scale (Demo):**
- 41 measures
- 50K members
- 2K guideline chunks

**Production Scale (Estimates):**
- 46 measures (CMS full set)
- 1-5M members (typical MA plan)
- 10K guideline chunks (expanded knowledge base)

**Scaling Strategy:**
- Delta Lake: Handles petabyte scale
- Vector Search: Auto-sharding for large indexes
- UC Functions: Serverless, scales automatically

### Optimization Techniques

**1. Vector Search:**
- Pre-filtered queries (by doc_type)
- Chunking strategy (512-1024 tokens)
- Top-K retrieval (limit=3)

**2. Data Queries:**
- Delta Z-ordering on frequently filtered columns
- Partition pruning where applicable
- Broadcast joins for small dimension tables

**3. Caching:**
- Streamlit session state for user data
- Vector index cached in memory
- Genie conversation context preserved

---

## Integration Points

### External Systems

**Inbound Data:**

| Source | Integration Method | Frequency |
|--------|-------------------|-----------|
| **Claims Data** | Lakeflow Connect / ETL | Daily |
| **EMR Data** | HL7 FHIR ingest | Real-time |
| **Pharmacy Data** | PBM partner API | Daily |
| **CMS Data** | File drop → Auto Loader | Monthly |

**Outbound Data:**

| Destination | Integration Method | Purpose |
|-------------|-------------------|---------|
| **BI Tools** | Databricks SQL | Dashboards |
| **Data Warehouse** | Lakehouse Federation | Legacy reporting |
| **Quality Systems** | REST API | Export analysis results |

### APIs

**Databricks REST API:**

```python
# Genie Conversation API
POST /api/2.0/genie/spaces/{space_id}/start-conversation
GET /api/2.0/genie/spaces/{space_id}/conversations/{id}/messages/{msg_id}

# SQL Warehouse API
POST /api/2.0/sql/statements
GET /api/2.0/sql/statements/{statement_id}

# Jobs API
POST /api/2.1/jobs/run-now
GET /api/2.1/jobs/runs/get
```

### Future Integrations

**Planned:**
- Slack bot for natural language queries
- Email alerts for measure thresholds
- PowerBI direct query connector
- Tableau dashboard templates

---

## Appendix

### File Structure Reference

```
payer_stars/
├── README.md                      # Project overview
├── databricks.yml                # Databricks Asset Bundle config
├── config.yaml                   # Environment configurations
├── generate_app_yaml.py          # App config generator
├── .gitignore                    # Git ignore patterns
│
├── app/                          # Streamlit application
│   ├── app.py                    # Home page
│   ├── app.yaml                  # Generated app config
│   ├── assets/                   # Static assets (images, etc.)
│   ├── pages/                    # Streamlit pages
│   │   ├── 0_architecture.py
│   │   ├── 1_measure_analysis.py
│   │   ├── 2_performance_dashboard.py
│   │   ├── 4_star_ratings_calculator.py
│   │   └── 5_setup_resources.py
│   └── utils/                    # Utility modules
│       └── state_graph_agent.py  # LangGraph orchestration
│
├── setup/                        # Setup notebooks (Databricks)
│   ├── 00_test_connection.py
│   ├── 01_create_catalog_schema.py
│   ├── 02_generate_measures_data.py
│   ├── 03_generate_members_data.py
│   ├── 04_uc_star_classify.py
│   ├── 05_uc_star_analyze.py
│   ├── 06_uc_star_recommend.py
│   ├── 07_uc_star_explain.py
│   ├── 08_create_knowledge_base.py
│   ├── 09_create_vector_search_index.py
│   ├── 10_create_config_tables.py
│   ├── 11_create_analysis_table.py
│   ├── 12_batch_analyze_measures.py
│   ├── 13_create_predictions.py
│   ├── 14_create_genie_space.py
│   └── 99_validate_system.py
│
├── docs/                         # User-facing documentation
│   ├── SETUP_RESOURCES_CONFIG.md # Setup configuration guide
│   ├── QUICK_REF_SETUP_RESOURCES.md # Quick reference
│   └── ARCHITECTURE.md           # This file
│
└── linkedin/                     # LinkedIn content (gitignored)
    ├── screenshots/              # Demo screenshots
    │   └── optimized/            # Optimized for web
    └── docs/                     # Blog articles (private)
```

### Resource Estimates

**Development Costs (DBUs):**
- Setup pipeline: ~10 DBUs (~$40)
- Vector index build: ~5 DBUs (~$20)
- UC function creation: ~2 DBUs (~$8)
- **Total one-time: ~$70**

**Runtime Costs (per month):**
- Serverless compute: ~50 DBUs (~$200)
- Vector search: ~20 DBUs (~$80)
- SQL warehouse: ~30 DBUs (~$120)
- **Total monthly: ~$400** (for 100 users, 1000 queries/month)

**Scaling:**
- 10x users = ~2-3x cost (caching helps)
- 10x data = ~1.5x cost (mostly storage)

### Useful Links

- **Databricks Lakehouse Architecture:** https://learn.microsoft.com/en-us/azure/databricks/lakehouse-architecture/reference
- **Unity Catalog Docs:** https://docs.databricks.com/en/data-governance/unity-catalog/index.html
- **LangGraph Documentation:** https://langchain-ai.github.io/langgraph/
- **Databricks Apps Guide:** https://docs.databricks.com/en/apps/index.html
- **Vector Search Guide:** https://docs.databricks.com/en/generative-ai/vector-search.html

---

**For questions or issues, please refer to the main README or open a GitHub issue.**

**Last Updated:** January 2026
