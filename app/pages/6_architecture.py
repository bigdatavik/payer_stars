"""
Architecture & Data Flow Visualization
Shows how data flows through the system from user query to results
"""

import streamlit as st

st.set_page_config(layout="wide", page_title="Architecture", page_icon="🏗️")

st.title("🏗️ Medicare Advantage Star Ratings System for Payers")
st.subheader("System Architecture & Data Flow")

st.markdown("""
This page explains how the AI-powered Star Ratings system works behind the scenes.
Use this to understand the technology and data flow before diving into the demo.
""")

# Show Databricks Platform Overview
st.markdown("---")
st.markdown("### 🏢 Databricks Data Intelligence Platform Overview")

# Load and display the platform diagram
import os
from pathlib import Path

app_dir = Path(__file__).parent.parent
platform_image_path = app_dir / "assets" / "databricks_platform.png"

if platform_image_path.exists():
    st.image(str(platform_image_path), 
             caption="Complete Databricks Data Intelligence Platform - This project leverages Unity Catalog, AI Functions, Vector Search, Genie, and Databricks Apps",
             use_column_width=True)
else:
    st.info("This project is built on the Databricks Data Intelligence Platform, utilizing multiple components including Unity Catalog, AI Functions, Vector Search, Genie, and Databricks Apps.")

# Technology Stack FIRST
st.markdown("---")
st.header("🛠️ Technology Stack")

st.markdown("""
The system is built on **Databricks Lakehouse Platform**. Here's what we're using:
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### Data Platform
    - **Unity Catalog** - Data governance & security
    - **Delta Lake** - ACID transactions, time travel
    - **SQL Warehouse** - Query execution engine
    - **Volumes** - File storage for PDFs
    """)

with col2:
    st.markdown("""
    ### AI & ML
    - **Claude Sonnet 4.5** - Foundation LLM
    - **LangGraph StateGraph** - AI orchestration
    - **Vector Search** - Semantic embeddings
    - **UC AI Functions** - Serverless inference
    """)

with col3:
    st.markdown("""
    ### Application Layer
    - **Streamlit** - Interactive dashboards
    - **Databricks Apps** - Managed hosting
    - **Python 3.10+** - Backend logic
    - **Plotly** - Data visualizations
    """)

st.info("💡 **Single Platform:** Everything runs on Databricks - no data movement, unified governance, consistent security.")

# DATA PIPELINE & ETL FLOW (NEW SECTION)
st.markdown("---")
st.header("📊 Data Pipeline & ETL Flow")

st.markdown("""
Before the AI can analyze anything, we need to **load and prepare the data**. Here's the complete ETL pipeline that runs during setup:
""")

st.markdown("### Setup Job: 15 Tasks in Sequence")
st.markdown("When you run `./deploy_with_config.sh dev`, this is what happens:")

st.info("**SETUP JOB EXECUTION** - 15 Tasks, ~18 minutes total")

st.markdown("""
**TASK 1: CLEANUP (1 min)**
- Drop existing catalog (if exists)
- Drop existing vector indexes
- Clean slate for fresh deployment

**TASK 2: CREATE CATALOG & SCHEMA (1 min)**
- `CREATE CATALOG payer_stars_dev`
- `CREATE SCHEMA payer_stars_dev.star_ratings`
- Set up Unity Catalog governance

**TASK 3: LOAD HEDIS MEASURES DATA (2 min)**
- Generate 42 HEDIS measures (Medicare-focused)
- Measure categories: Part D (3x), Outcomes (3x), Preventive (1x)
- Performance rates, targets, gaps, weights
- `INSERT INTO star_ratings.measures`

**TASK 4: LOAD MEMBER DATA (2 min)**
- Generate 50,000 Medicare members
- Demographics: avg age 73, 80% with chronic conditions
- Enrollment status, risk scores, gaps in care
- `INSERT INTO star_ratings.members`

**TASKS 5-8: CREATE UC AI FUNCTIONS (4 min)**
- TASK 5: `star_classify` (intent classification)
- TASK 6: `star_gap_analyze` (root cause analysis)
- TASK 7: `star_improvement_recommend` (interventions)
- TASK 8: `star_explain` (Q&A explanations)
- Each function deployed as serverless UC function

**TASK 9: CREATE KNOWLEDGE BASE (1 min)**
- Generate 1,000+ pages HEDIS guidelines
- Technical specifications, best practices, evidence
- `INSERT INTO star_ratings.knowledge_base`

**TASK 10: CHUNK KNOWLEDGE BASE (2 min)**
- Split guidelines into semantic chunks
- Each chunk: ~500 tokens, overlap for context
- `INSERT INTO star_ratings.knowledge_chunks`

**TASK 11: CREATE VECTOR SEARCH INDEX (10 min)** ⬅️ **LONGEST**
- Embed all knowledge chunks using LLM
- Build vector index: `hedis_guidelines_index`
- Sync status: PROVISIONING → ONLINE
- Ready for semantic search

**TASK 12: CREATE ANALYSIS TABLE (1 min)**
- Table for storing AI-generated analysis results
- `star_ratings.measure_analysis`

**TASK 13: BATCH ANALYZE MEASURES (2 min)**
- Run AI analysis on all 42 measures
- Call `star_gap_analyze` for each measure
- Store results for fast retrieval

**TASK 14: CREATE PREDICTIONS TABLE (1 min)**
- Generate star rating predictions
- Model what-if scenarios
- `star_ratings.star_predictions`

**TASK 15: CREATE GENIE SPACE (1 min)**
- Set up Genie for natural language queries
- Configure table access and permissions
""")

st.success("✅ **SETUP COMPLETE:** All data loaded, AI ready to use")

# Show the actual job timeline from a real run
st.markdown("### 📸 Actual Job Timeline from Recent Run")

# Try to load the image with proper path handling
import os
from pathlib import Path

# Get the app directory path
app_dir = Path(__file__).parent.parent
image_path = app_dir / "assets" / "job_timeline.png"

if image_path.exists():
    st.image(str(image_path), caption="Real execution timeline showing all 15 tasks with dependencies and timing. Note: create_vector_index takes ~6 minutes (longest task)", use_column_width=True)
else:
    st.warning(f"Job timeline image not found at: {image_path}")
    st.info("The setup job executes 15 tasks sequentially with dependencies. The vector index creation (Task 11) is the longest-running task at approximately 6 minutes.")

st.success("""
**Key ETL Principles:**
- ✅ **Dependencies managed** - Tasks run in correct order (e.g., catalog before tables)
- ✅ **Idempotent** - Cleanup ensures fresh run every time
- ✅ **Parallel where possible** - Independent tasks can run concurrently
- ✅ **Fully automated** - One command deploys everything
- ✅ **Validated** - Each task checks for success before proceeding
""")

# Show the data model
st.markdown("---")
st.subheader("📋 Data Model: Unity Catalog Tables")

st.markdown("""
After ETL completes, here's what's in Unity Catalog:

| Table | Rows | Purpose | Key Columns |
|-------|------|---------|-------------|
| **measures** | 42 | HEDIS measure performance | measure_id, performance_rate, target, gap, weight |
| **members** | 50,000 | Medicare Advantage enrollees | member_id, age, risk_score, chronic_conditions |
| **knowledge_base** | 1,000+ | HEDIS guideline documents | doc_id, title, content, category |
| **knowledge_chunks** | 5,000+ | Chunked & embedded docs | chunk_id, doc_id, embedding_vector |
| **measure_analysis** | 42 | Pre-computed AI analysis | measure_id, root_causes, recommendations |
| **star_predictions** | 100+ | What-if scenarios | scenario_id, projected_score, interventions |
| **config_genie** | 1 | Genie Space configuration | config_key, config_value |
""")

st.info("💾 **Storage:** All tables use Delta Lake format - ACID transactions, time travel, schema evolution")

# Show data lineage
st.markdown("---")
st.subheader("🔗 Data Lineage: How Data Flows")

st.markdown("""
### Source → Transform → Load → Analyze

```
┌─────────────────────┐
│  SOURCE DATA        │
├─────────────────────┤
│ • CMS HEDIS specs   │  ─┐
│ • Measure targets   │   │
│ • CMS weights       │   ├─→ TASK 3: Generate measures table
└─────────────────────┘   │
                          │
┌─────────────────────┐   │
│  ENROLLMENT DATA    │   │
├─────────────────────┤   │
│ • Member demographics│ ─┼─→ TASK 4: Generate members table
│ • Risk scores       │   │
└─────────────────────┘   │
                          │
┌─────────────────────┐   │
│  HEDIS GUIDELINES   │   │
├─────────────────────┤   │
│ • Tech specs (PDF)  │ ─┼─→ TASK 9: Load knowledge base
│ • Best practices    │   │
└─────────────────────┘   │
                          │
                          ▼
              ┌───────────────────────┐
              │  UNITY CATALOG        │
              │  Delta Lake Tables    │
              └──────────┬────────────┘
                         │
                         ▼
              ┌───────────────────────┐
              │  TRANSFORM            │
              ├───────────────────────┤
              │ • TASK 10: Chunk docs │
              │ • TASK 11: Embed      │
              │ • TASK 13: Analyze    │
              └──────────┬────────────┘
                         │
                         ▼
              ┌───────────────────────┐
              │  VECTOR INDEX         │
              │  AI ANALYSIS RESULTS  │
              └──────────┬────────────┘
                         │
                         ▼
              ┌───────────────────────┐
              │  STREAMLIT APP        │
              │  Query & Display      │
              └───────────────────────┘
```
""")

# Now show the runtime architecture
st.markdown("---")
st.header("🏗️ Runtime Architecture")

st.markdown("""
Once data is loaded, here's how the system operates when users interact with it:
""")

st.markdown("""
### System Layers

```
┌─────────────────────────────────────────────────────────────┐
│                   👤 USER INTERFACE                         │
│                   Streamlit Dashboard                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                🤖 AI ORCHESTRATION                          │
│         LangGraph StateGraph + Routing Logic               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                🧠 AI INFERENCE LAYER                        │
│    UC Functions (classify, analyze, recommend, explain)    │
│              Claude Sonnet 4.5 LLM Backend                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            📚 KNOWLEDGE & SEARCH LAYER                      │
│    Vector Search (HEDIS Guidelines) + Genie (NL to SQL)    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    💾 DATA LAYER                            │
│       Unity Catalog (Measures, Members, Guidelines)        │
└─────────────────────────────────────────────────────────────┘
```
""")

st.info("💡 **Tip:** Data flows top-down from user query through AI orchestration, UC functions, knowledge retrieval, and back to the UI with results.")

# Detailed Data Flow
st.markdown("---")
st.header("🔄 Detailed Data Flow: Measure Analysis Query")

st.markdown("""
Let's trace a specific query: **"Why is breast cancer screening underperforming?"**
""")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("""
    **Step-by-Step Flow:**
    
    1️⃣ **User Input**
    - Query entered in Streamlit
    - Measure data provided
    
    2️⃣ **Intent Classification**
    - LangGraph receives query
    - Routes to classification node
    - Calls `star_classify` UC function
    
    3️⃣ **Conditional Routing**
    - Identifies as "measure_analysis"
    - Routes to gap analysis pipeline
    
    4️⃣ **Gap Analysis**
    - Calls `star_gap_analyze` UC function
    - Claude analyzes measure data
    - Returns structured output
    
    5️⃣ **Knowledge Retrieval**
    - Vector Search queries HEDIS guidelines
    - Semantic similarity matching
    - Returns top 3 relevant documents
    
    6️⃣ **Results Synthesis**
    - LangGraph combines all results
    - Formats for display
    
    7️⃣ **UI Display**
    - Streamlit renders 4-tab Gap Analysis
    - Shows Vector Search results
    - Displays citations
    """)

with col2:
    st.markdown("""
    **Sequence Flow:**
    
    ```
    User
     │
     ▼
    Streamlit App
     │ (query + measure data)
     ▼
    LangGraph StateGraph
     │
     ├─→ UC: star_classify()
     │    └─→ Claude: "measure_analysis"
     │
     ├─→ UC: star_gap_analyze()
     │    ├─→ Claude: Analyze data
     │    └─→ Return: root_causes, 
     │                populations, barriers
     │
     ├─→ Vector Search
     │    └─→ HEDIS guidelines (top 3)
     │
     ▼
    Synthesize Results
     │
     ▼
    Streamlit Display
     └─→ User sees 4-tab analysis
    ```
    """)

# UC Functions Deep Dive
st.markdown("---")
st.header("🧠 Unity Catalog AI Functions")

st.markdown("""
The system uses **4 specialized UC Functions**, each powered by Claude Sonnet 4.5:
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 1. `star_classify` ⚡
    **Purpose:** Intent classification
    
    **Input:** User query string
    
    **Output:** 
    ```python
    {
        "query_type": "measure_analysis",
        "confidence": 0.95
    }
    ```
    
    **Use Case:** Routes queries to appropriate pipeline
    
    ---
    
    ### 2. `star_gap_analyze` 🔍
    **Purpose:** Root cause analysis
    
    **Input:** Measure performance data
    
    **Output:**
    ```python
    {
        "root_causes": ["..."],
        "affected_populations": ["..."],
        "performance_barriers": ["..."],
        "data_quality_issues": ["..."]
    }
    ```
    
    **Use Case:** 4-tab Gap Analysis display
    """)

with col2:
    st.markdown("""
    ### 3. `star_improvement_recommend` 💡
    **Purpose:** Evidence-based interventions
    
    **Input:** Gap analysis + knowledge base context
    
    **Output:**
    ```python
    {
        "interventions": [
            {
                "name": "...",
                "description": "...",
                "evidence_level": "strong",
                "estimated_impact": 5.2,
                "implementation_time": "3-6 months"
            }
        ]
    }
    ```
    
    **Use Case:** Improvement planning
    
    ---
    
    ### 4. `star_explain` 📖
    **Purpose:** Q&A and explanations
    
    **Input:** Question + context
    
    **Output:** Natural language explanation with citations
    
    **Use Case:** "What is this measure?" queries
    """)

# Vector Search Flow
st.markdown("---")
st.header("🔍 Vector Search: Semantic Guideline Retrieval")

st.markdown("""
Instead of keyword searching PDFs, we use **semantic vector search** over embedded HEDIS guidelines:
""")

st.markdown("""
### Vector Search Process

```
User Query: "Why is BCS underperforming?"
      │
      ▼
Query Embedding (converts to vector)
      │
      ▼
Vector Index (1000+ HEDIS guideline pages pre-embedded)
      │
      ▼
Cosine Similarity Search (finds semantically related docs)
      │
      ▼
Top 3 Relevant Documents Retrieved:
  • Document 1: BCS Technical Specifications
  • Document 2: Intervention Evidence  
  • Document 3: Member Outreach Best Practices
      │
      ▼
Injected into AI Context for Analysis
```
""")

st.success("""
**Why Vector Search?**
- ✅ **Semantic understanding** - Finds conceptually related content, not just keywords
- ✅ **Always current** - Update guidelines without retraining models
- ✅ **Explainable** - Every recommendation cites specific guideline sections
- ✅ **Fast** - Sub-second retrieval from 1,000+ pages
""")

# Genie Flow
st.markdown("---")
st.header("💬 Genie: Natural Language to SQL")

st.markdown("""
The Performance Dashboard uses **Databricks Genie** for self-service analytics:
""")

st.markdown("""
### Genie Query Flow

```
User Question: "Show me Part D measures with gaps over 10%"
      │
      ▼
Genie API (Natural Language Parser)
      │
      ▼
SQL Generator
  • Analyzes table schemas
  • Understands intent ("Part D" = category filter)
  • Knows "gaps over 10%" = WHERE gap > 0.10
      │
      ▼
Generated SQL:
  SELECT measure_name, performance_rate, 
         target_benchmark, gap
  FROM payer_stars_dev.star_ratings.measures
  WHERE measure_category = 'Part D' 
    AND gap > 0.10
  ORDER BY gap DESC
      │
      ▼
Execute against Unity Catalog
      │
      ▼
Results + Auto-Generated Visualization (Plotly chart)
      │
      ▼
Display in Streamlit
```
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Example Query:**
    > "Which Part D measures have the largest gaps?"
    
    **What Genie Does:**
    - Understands "Part D" refers to category filter
    - Knows "largest gaps" means ORDER BY gap DESC
    - Infers relevant columns to display
    - Auto-generates bar chart of results
    """)

with col2:
    st.markdown("""
    **Benefits:**
    ✅ No SQL knowledge required  
    ✅ Real-time queries  
    ✅ Auto-generated visualizations  
    ✅ Self-service for quality analysts  
    ✅ Reduces IT backlog  
    """)

# Security & Governance
st.markdown("---")
st.header("🔒 Security & Governance")

st.markdown("""
Every component is governed through Unity Catalog:
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Access Control:**
    - Catalog: USE permission
    - Schema: SELECT, MODIFY permissions
    - Warehouse: CAN_USE permission
    - Vector Endpoint: CAN_USE permission
    - Service Principal authentication
    """)

with col2:
    st.markdown("""
    **Audit Trail:**
    - Who accessed what data
    - Which AI function was called
    - What recommendations were made
    - Which HEDIS guidelines were cited
    - Complete lineage tracking
    """)

st.info("""
**HIPAA Compliance:**
- ✅ All data stays within Unity Catalog (no external API calls with data)
- ✅ Role-based access control
- ✅ Complete audit trails for every AI decision
- ✅ Service principal authentication (no user credentials in app)
- ✅ Data lineage for all transformations
""")

# Performance Metrics
st.markdown("---")
st.header("⚡ Performance Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Gap Analysis Time",
        value="60 sec",
        delta="-99.9% vs manual",
        delta_color="normal"
    )

with col2:
    st.metric(
        label="Vector Search Latency",
        value="< 1 sec",
        delta="1000+ pages",
        delta_color="off"
    )

with col3:
    st.metric(
        label="Genie Query Time",
        value="10-15 sec",
        delta="Real-time SQL",
        delta_color="off"
    )

with col4:
    st.metric(
        label="UC Function Inference",
        value="2-5 sec",
        delta="Per function call",
        delta_color="off"
    )

# Deployment Architecture
st.markdown("---")
st.header("🚀 Deployment Architecture")

st.markdown("""
The entire system deploys via **Databricks Asset Bundles (DAB)**:

### Deployment Flow

```
Local Development
      │
      ▼
./deploy_with_config.sh dev
      │
      ├─→ Read config.yaml
      ├─→ Generate app.yaml
      ├─→ Deploy infrastructure (databricks bundle deploy)
      │
      ▼
Databricks Workspace
      │
      ├─→ Create Unity Catalog (catalog + schema)
      ├─→ Create Tables (measures, members, guidelines)
      ├─→ Deploy 4 UC Functions (serverless)
      ├─→ Build Vector Search Index (~10 min)
      ├─→ Create Genie Space
      ├─→ Deploy Streamlit App
      │
      ▼
✅ Fully Operational System (20 minutes)
```
""")

st.success("""
**One-Command Deployment:**
```bash
./deploy_with_config.sh dev
```

**What Gets Deployed:**
- ✅ Unity Catalog (catalog, schema, tables)
- ✅ 4 UC AI Functions (classify, analyze, recommend, explain)
- ✅ Vector Search Index (with 1000+ guideline pages)
- ✅ Genie Space (for natural language queries)
- ✅ Streamlit App (5 pages with full functionality)
- ✅ Sample Data (42 HEDIS measures, 50K members)

**Total Time: 20 minutes**
""")

# Key Takeaways
st.markdown("---")
st.header("💡 Key Architecture Principles")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 1. Unified Lakehouse
    - Single platform for data + AI
    - No data movement
    - Consistent governance
    
    ### 2. Serverless AI
    - UC Functions (no cluster management)
    - Auto-scaling inference
    - Pay per use
    
    ### 3. Explainable AI
    - Every decision cites guidelines
    - Complete audit trails
    - Transparent reasoning
    """)

with col2:
    st.markdown("""
    ### 4. Self-Service Analytics
    - Natural language queries
    - No SQL required
    - Interactive dashboards
    
    ### 5. Production-Ready
    - Asset Bundle deployment
    - Service principal auth
    - HIPAA compliant
    
    ### 6. Extensible
    - Add new measures easily
    - Update guidelines without retraining
    - Scale to millions of members
    """)

# Demo Flow Connection
st.markdown("---")
st.header("🎬 Ready for the Demo?")

st.markdown("""
Now that you understand the architecture, here's how the demo pages map to the technology:

| Demo Page | Technology Used |
|-----------|----------------|
| **Measure Analysis** | LangGraph + 4 UC Functions + Vector Search |
| **Performance Dashboard** | Genie + Unity Catalog + Plotly |
| **Improvement Planner** | UC Functions + Recommendation Engine |
| **Star Ratings Calculator** | CMS Methodology + Unity Catalog Data |

Each page demonstrates a different aspect of the unified platform.
""")

st.markdown("---")
st.caption("⭐ CMS Star Ratings Analytics | Built with Databricks Lakehouse + AI")
