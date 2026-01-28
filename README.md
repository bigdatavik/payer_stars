# ⭐ AI-Powered CMS Star Ratings System for Medicare Advantage Plans

> **⚠️ PERSONAL PROJECT DISCLAIMER**  
> This is a personal learning and demonstration project created for educational purposes.  
> It is NOT affiliated with any employer or organization.  
> This project should NOT be used in production without proper testing, compliance review, and legal approval.  
> No warranties expressed or implied. Use at your own risk.

> **Project Status**: ✅ **Complete & Ready for Deployment** | January 2026

[![Databricks](https://img.shields.io/badge/Databricks-Ready-red?logo=databricks)](https://databricks.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-blue)](https://langchain-ai.github.io/langgraph/)
[![Unity Catalog](https://img.shields.io/badge/Unity%20Catalog-AI%20Functions-orange)](https://www.databricks.com/product/unity-catalog)
[![Status](https://img.shields.io/badge/Status-Production--Ready-success)](#)

An intelligent **Medicare Advantage Star Ratings** analysis and improvement system for healthcare payers (like Humana), focused on seniors (65+) with chronic conditions. Uses LangGraph StateGraph agents, Unity Catalog AI functions, Vector Search, and Medicare-focused HEDIS guidelines.

**Target Users:** Medicare Advantage payers, quality teams managing Part D adherence, readmissions, chronic disease management, and member experience.

**Key Features:** CMS 2026 weighted scoring (3x outcomes, 2x experience, 1x preventive) | Medicare-specific measures | Part D medication adherence focus | Readmissions & transitions | Star Ratings calculator with what-if scenarios

**Medicare Focus:** 
- 🎯 **Part D Medication Adherence** (3x weight): Critical for diabetes, hypertension, cholesterol meds
- 🏥 **Readmissions & Outcomes** (3x weight): Hospital readmissions, medication reconciliation, transitions of care
- 👴 **Geriatric Population** (65+): Avg age 73, 80%+ have 2+ chronic conditions
- 💊 **High-Risk Medications** (3x weight): Beers Criteria monitoring for elderly
- 💰 **Quality Bonus Impact**: 5-star plans receive enhanced CMS rebate payments

---

## 🚀 Quick Start (2 Steps, ~20 minutes total)

```
┌────────────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT APPROACH                                 │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  1️⃣  ONE-COMMAND DEPLOY (Recommended)                                 │
│     ./deploy_with_config.sh dev                                       │
│     ✅ Fully automated | ✅ Auto-recovery built-in                    │
│                                                                        │
│  2️⃣  MANUAL STEP-BY-STEP (If you prefer control)                      │
│     Run 6 commands separately                                         │
│     ✅ Same auto-recovery in step 5                                   │
│                                                                        │
│  🔧 TROUBLESHOOTING TOOL (Only if needed)                             │
│     ./fix_app_deployment.sh dev                                       │
│     ℹ️  Not a deployment step - only for rare issues                  │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### **Step 1: Configure** (2 minutes)

Edit `config.yaml` with your Databricks details:

```bash
vim config.yaml
```

Update these values:
```yaml
environments:
  dev:
    workspace_host: "https://your-workspace.azuredatabricks.net"  # ← Your workspace URL
    profile: "DEFAULT_azure"                                       # ← Your profile name
    catalog: "payer_stars_dev"                                    # ← Leave as is (or customize)
    warehouse_id: "your-warehouse-id"                             # ← Your SQL Warehouse ID
    vector_endpoint: "one-env-shared-endpoint-2"                  # ← Your vector endpoint
    llm_endpoint: "databricks-claude-sonnet-4-5"                  # ← Your LLM endpoint
    app_name: "payerstars-dev"                                     # ← App name
```

**Where to find these values**:
- **Workspace URL**: Your Databricks workspace URL (copy from browser)
- **Profile**: Check `~/.databrickscfg` (usually `DEFAULT` or `DEFAULT_azure`)
- **Warehouse ID**: Databricks → SQL Warehouses → Copy the ID
- **Vector Endpoint**: Databricks → Compute → Vector Search → Your endpoint name
- **LLM Endpoint**: Databricks → Serving → Foundation Models → Your endpoint

---

### **Step 2: Deploy Everything** (~20 minutes - automated!)

**Option A: One-Command Deploy** (Recommended ⭐)

```bash
./deploy_with_config.sh dev
```

This automatically does **everything** with built-in safety checks:
1. ✅ **Pre-flight checks**: Validates authentication before starting
2. ✅ Generates `app/app.yaml` from config
3. ✅ Deploys app and infrastructure
4. ✅ Runs setup job (creates catalog, tables, UC functions, vector index, sample data)
5. ✅ Grants service principal permissions
6. ✅ Deploys app source code
7. ✅ Starts the app automatically
8. ✅ Shows final status and URL

**⏱️ Total time:** ~18-22 minutes

**🛡️ What's Protected:**
- Authentication is validated **before** any deployment starts
- All errors are shown clearly with specific fix instructions
- App automatically starts after deployment
- Final status verification ensures everything is working

---

**Option B: Manual Steps** (if you prefer step-by-step)

```bash
# 1. Generate app config
python generate_app_yaml.py dev

# 2. Deploy infrastructure
databricks bundle deploy --target dev --profile DEFAULT_azure

# 3. Create data and resources
databricks bundle run setup_star_ratings --target dev --profile DEFAULT_azure

# 4. Grant permissions
./grant_permissions.sh dev

# 5. Deploy and start app
./deploy_app_source.sh dev

# 6. Run validation tests (optional)
databricks bundle run validate_star_ratings --target dev --profile DEFAULT_azure
```

**Note:** If any step fails, the error message will show you exactly how to fix it. You can then re-run just that step.

---

**That's it!** ✅

Your app will be available at: `https://your-workspace.azuredatabricks.net/apps/payerstars-dev`

**⏱️ Wait for app to start:** After deployment, the app will automatically start. Wait 30-60 seconds, then:
- Refresh the Apps page in Databricks UI
- Check that status shows **"Active"** (not "Stopped")
- If still "Stopped", click the **"Start"** button

**📖 Note:** Per [Microsoft Databricks documentation](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/apps-tutorial#deploy-the-app-to-the-workspace), deploying a bundle doesn't automatically deploy the app to compute. That's why we run `deploy_app_source.sh` as a separate step to deploy the app source code from the bundle workspace location. The updated script now also ensures the app is started.

**⏱️ Wait for vector index to sync** (~10-15 minutes after deployment)
- Go to: **Databricks UI → Catalog → Vector Search**
- Monitor: `hedis_guidelines_index`
- Wait for status: **ONLINE**

**Total time from zero to fully operational**: ~30-35 minutes

---

## 📋 What Gets Deployed

When you run the commands above, the system automatically:

1. ✅ **Cleanup** - Removes all existing resources (catalog, tables, indexes, functions) for clean run
2. ✅ Creates Unity Catalog `payer_stars_dev`
3. ✅ Creates schema `star_ratings`
4. ✅ Generates synthetic **Medicare-focused** HEDIS measures data (42 measures, removed pediatric)
5. ✅ **CMS 2026 Weights**: Outcomes 3x, Experience/Access 2x, Preventive 1x
6. ✅ Generates synthetic member enrollment data (50,000 Medicare Advantage members, avg age 73)
7. ✅ Creates **4 UC AI functions** (classify, analyze, recommend, explain)
8. ✅ Creates **Medicare-focused** HEDIS guidelines knowledge base (geriatric focus, Part D adherence, readmissions)
9. ✅ Chunks documents for vector search
10. ✅ Creates **vector search index** for semantic guideline search
11. ✅ Creates analysis tables for storing AI results
12. ✅ Batch processes measures through AI functions
13. ✅ Generates star rating predictions with weighted scoring
14. ✅ Creates Genie Space for natural language queries
15. ✅ Deploys Streamlit app with 5 pages (including Star Ratings Calculator)
16. ✅ Grants all necessary permissions

**Total time**: ~18-22 minutes (includes cleanup + setup)

**Note:** The setup job starts with a cleanup task to ensure a completely fresh environment every time!

### **Complete Deployment Flow**

When you run `./deploy_with_config.sh dev`, here's the complete end-to-end flow:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                   COMPLETE DEPLOYMENT FLOW (6 Steps)                            │
│                   Script: ./deploy_with_config.sh dev                           │
└─────────────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════════╗
║  STEP 1: Pre-Flight Checks                                        (~10 sec)   ║
╚═══════════════════════════════════════════════════════════════════════════════╝
                    ┌──────────────────────────┐
                    │ • Check Databricks CLI   │
                    │ • Validate config.yaml   │
                    │ • Update notebook versions│
                    └────────────┬─────────────┘
                                 │
╔═══════════════════════════════════════════════════════════════════════════════╗
║  STEP 2: Generate App Config                                      (~5 sec)    ║
╚═══════════════════════════════════════════════════════════════════════════════╝
                    ┌──────────────────────────┐
                    │ python generate_app_yaml │
                    │ • Reads config.yaml      │
                    │ • Creates app.yaml       │
                    └────────────┬─────────────┘
                                 │
╔═══════════════════════════════════════════════════════════════════════════════╗
║  STEP 3: Deploy Infrastructure                                    (~30 sec)   ║
╚═══════════════════════════════════════════════════════════════════════════════╝
                    ┌──────────────────────────┐
                    │ databricks bundle deploy │
                    │ • Creates app definition │
                    │ • Creates job definitions│
                    │ • Uploads files to WS    │
                    └────────────┬─────────────┘
                                 │
╔═══════════════════════════════════════════════════════════════════════════════╗
║  STEP 4: Run Setup Job (setup_star_ratings)                   (~15-18 min)   ║
╚═══════════════════════════════════════════════════════════════════════════════╝
         ┌────────────────────────┴────────────────────────┐
         │        databricks bundle run setup_star_ratings  │
         └────────────────────────┬────────────────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
    ┌─────────────────┐  ┌──────────────┐  ┌────────────────┐
    │  1. CLEANUP     │  │ 2. CREATE    │  │ 3-4. GENERATE  │
    │  • Drop catalog │→ │    CATALOG   │→ │ • Measures     │
    │  • Drop indexes │  │ • Create     │  │ • Members      │
    │  • Clean state  │  │   schema     │  │ (50K records)  │
    └─────────────────┘  └──────────────┘  └────────┬───────┘
                                                     │
              ┌──────────────────────────────────────┼─────────────┐
              │                                      │             │
              ▼                                      ▼             ▼
    ┌──────────────────┐                 ┌─────────────────────────────┐
    │ 5-7. CREATE UC   │                 │ 8-10. KNOWLEDGE BASE        │
    │     FUNCTIONS    │                 │ • Create docs               │
    │ • classify       │                 │ • Chunk documents           │
    │ • analyze        │                 │ • Vector search index       │
    │ • recommend      │                 │ (~10 min for vector)        │
    │ • explain        │                 └──────────────┬──────────────┘
    └────────┬─────────┘                                │
             │              ┌──────────────────────────┘
             └──────────────┤
                            ▼
                 ┌────────────────────┐
                 │ 11-13. ANALYSIS    │
                 │ • Create tables    │
                 │ • Batch analyze    │
                 │ • Predictions      │
                 └──────────┬─────────┘
                            │
                            ▼
                 ┌────────────────────┐
                 │ 14. CREATE GENIE   │
                 │     SPACE          │
                 │ • Analytics setup  │
                 └──────────┬─────────┘
                            │
                            ▼
                 ┌────────────────────┐
                 │ ✅ SETUP COMPLETE  │
                 └──────────┬─────────┘
                            │
╔═══════════════════════════════════════════════════════════════════════════════╗
║  STEP 5: Grant Permissions (grant_permissions.sh)                (~30 sec)   ║
╚═══════════════════════════════════════════════════════════════════════════════╝
                            │
                 ┌──────────▼─────────────────┐
                 │ Get service principal ID   │
                 │ from deployed app          │
                 └──────────┬─────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
    ┌─────────┐      ┌──────────┐      ┌──────────┐
    │ CATALOG │      │  SCHEMA  │      │ WAREHOUSE│
    │ • USE   │      │ • USE    │      │ • CAN_USE│
    │ CATALOG │      │ • SELECT │      │          │
    └─────────┘      │ • MODIFY │      └──────────┘
                     └──────────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
                 ┌──────────▼─────────────────┐
                 │ Grant function EXECUTE     │
                 │ • All 4 UC functions       │
                 └──────────┬─────────────────┘
                            │
╔═══════════════════════════════════════════════════════════════════════════════╗
║  STEP 6: Deploy App Source (deploy_app_source.sh)                (~30 sec)   ║
╚═══════════════════════════════════════════════════════════════════════════════╝
                            │
                 ┌──────────▼─────────────────┐
                 │ databricks apps deploy     │
                 │ • Copies source code from  │
                 │   bundle workspace location│
                 │ • Starts app compute       │
                 │ • App status: RUNNING      │
                 └──────────┬─────────────────┘
                            │
                            ▼
              ╔═══════════════════════════╗
              ║  🎉 DEPLOYMENT COMPLETE!  ║
              ║                           ║
              ║  App URL:                 ║
              ║  https://your-workspace   ║
              ║    .azuredatabricks.net   ║
              ║    /apps/payerstars-dev   ║
              ╚═══════════════════════════╝
                            │
                            │ (Background process)
                            ▼
              ┌─────────────────────────────┐
              │ Vector Index Sync           │
              │ • Initial sync: 10-15 min   │
              │ • Status: PROVISIONING →    │
              │           ONLINE            │
              └─────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL TIME BREAKDOWN:
  • Pre-flight + Config:         ~15 seconds
  • Infrastructure Deploy:        ~30 seconds
  • Setup Job (15 tasks):         ~15-18 minutes  ⬅ LONGEST STEP
  • Grant Permissions:            ~30 seconds
  • Deploy App Source:            ~30 seconds
  ────────────────────────────────────────────────
  TOTAL TO RUNNING APP:           ~17-20 minutes
  VECTOR INDEX SYNC (background): +10-15 minutes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### **Deployment Task Flow (Step 4 Detail)**

The setup job runs 15 tasks with dependencies. Here's the execution flow:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          DEPLOYMENT TASK FLOW (15 Tasks)                        │
└─────────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────────┐
                              │  START DEPLOY    │
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │  1. CLEANUP      │  (~1 min)
                              │  Delete existing │
                              │  resources       │
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌─────────────────────────┐
                              │  2. CREATE CATALOG      │  (~1 min)
                              │     & SCHEMA            │
                              │  Unity Catalog + schema │
                              └────────┬────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
        ┌───────────▼────────┐    ┌───▼──────────┐  ┌───▼──────────┐
        │ 3. Generate        │    │ 4. Generate  │  │ UC Functions │
        │    Measures        │    │    Members   │  │ (Tasks 5-8)  │
        │ • 45 HEDIS         │    │ • 50K MA     │  │              │
        │   measures         │    │   members    │  │ 5. classify  │
        └───────────┬────────┘    └───┬──────────┘  │ 6. analyze   │
                    │                 │             │ 7. recommend │
                    │                 │             │ 8. explain   │
                    │                 │             └───┬──────────┘
                    │                 │                 │
                    ▼                 ▼                 │
        ┌───────────────────┐    ┌───────────────┐    │
        │ 9. Create KB Docs │    │ 10. Chunk KB  │    │
        │ HEDIS guidelines  │ →  │ Split for     │    │
        └───────────────────┘    │    search     │    │
                                 └───┬───────────┘    │
                                     │                │
                                     ▼                │
                          ┌────────────────┐          │
                          │11. Vector Index│          │
                          │ (~10 min)      │          │
                          └───┬────────────┘          │
                              │                       │
                              ▼                       ▼
                    ┌──────────────────┐  ┌────────────────┐
                    │12. Analysis Table│  │13. Batch       │
                    │                  │→ │   Analyze      │
                    └──────────────────┘  └────────┬───────┘
                                                   │
                                                   ▼
                                          ┌────────────────┐
                                          │14. Predictions │
                                          └────────┬───────┘
                                                   │
                                                   ▼
                                          ┌────────────────┐
                                          │15. Genie Space │
                                          └────────┬───────┘
                                                   │
                                                   ▼
                                          ┌────────────────┐
                                          │ ✅ COMPLETE    │
                                          └────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Key Dependencies:
  • Task 1 (cleanup) runs first
  • Task 2 (create_catalog) depends on cleanup
  • All other tasks depend on create_catalog
  • Vector index (task 11) is the longest single task (~10 min)
  • Tasks run sequentially to avoid conflicts
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🎯 Features

### **Medicare Advantage Star Ratings Focus**
- **CMS 2026 Weighted Methodology**: Outcomes (3x), Experience/Access (2x), Preventive (1x)
- **Star Ratings Calculator**: Interactive what-if scenarios, cut points (≥4.25 = 5 stars)
- **Part D Medication Adherence**: Diabetes, hypertension, cholesterol (3x weight measures)
- **Readmissions & Transitions**: 30-day readmissions, TCM visits, medication reconciliation
- **High-Risk Medications**: Beers Criteria monitoring for elderly (65+)
- **Geriatric Population**: Avg age 73, 80%+ with 2+ chronic conditions
- **Quality Bonus Impact**: Model financial impact of star rating improvements

### **StateGraph Agent Architecture**
- **LangGraph StateGraph Pattern**: Deterministic routing with conditional edges
- **3 Specialized Pipelines**: Measure Analysis, Improvement Planning, Q&A
- **Intent Classification**: Rule-based routing for reliability
- **Explainable Decisions**: Full reasoning trace with HEDIS citations

### **AI Functions** (Unity Catalog)
1. `star_measure_classify` - Performance classification (Critical/High/Moderate/Low)
2. `star_gap_analyze` - Root cause analysis with AI-powered insights
3. `star_improvement_recommend` - Actionable recommendations based on gaps
4. `star_explain` - Human-readable explanations for stakeholders

### **Vector Search**
- **Medicare HEDIS Guidelines Index**: Semantic search of Medicare-focused quality measure guidelines
- **Geriatric Focus**: Part D adherence, readmissions, high-risk meds, chronic disease management
- **Embedding Model**: `databricks-gte-large-en`
- **Use Case**: Retrieve relevant guidelines for measure improvement in elderly populations

### **Genie Space**
- **Natural Language Queries**: Ask questions about star ratings data
- **Auto-Discovery**: Dynamically reads Genie Space ID from database (no manual config)
- **Connected Tables**: measures_data, star_analysis, member_enrollments
- **Sample Questions**: Critical gaps, Medicare measure trends, Part D adherence, improvement priorities

### **Streamlit Dashboard**
- 🏠 **Home** - Medicare Advantage overview, CMS 2026 methodology, Humana context
- 📊 **Measure Analysis** - Interactive agent with StateGraph workflow
- 💡 **Improvement Planner** - Gap analysis and recommendations
- 📈 **Performance Dashboard** - Trends with Genie integration
- 🌟 **Star Ratings Calculator** - Weighted scoring, cut points, what-if scenarios

---

## 🏗️ Architecture & Data Flow

### **StateGraph Agent Workflow**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     STATEGRAPH AGENT WORKFLOW                               │
└─────────────────────────────────────────────────────────────────────────────┘

                         User Query
                              │
                              ▼
                   ┌────────────────────┐
                   │ Intent Classifier  │
                   │ (Rule-Based)       │
                   └──────────┬─────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Measure Analysis │  │ Improvement      │  │ Q&A Pipeline     │
│ Pipeline         │  │ Pipeline         │  │                  │
│                  │  │                  │  │                  │
│ 1. Classify      │  │ 1. Analyze Gaps  │  │ 1. Search Vector │
│ 2. Get Details   │  │ 2. Root Causes   │  │ 2. Find Context  │
│ 3. Show Trends   │  │ 3. Recommend     │  │ 3. Answer Query  │
└────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
         │                     │                      │
         │          UC Functions + Vector Search      │
         │                     │                      │
         └─────────────────────┼──────────────────────┘
                               │
                               ▼
                   ┌────────────────────┐
                   │ Synthesize Response│
                   │ with Citations     │
                   └──────────┬─────────┘
                              │
                              ▼
                        Final Answer
```

### **End-to-End Data Flow**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     CMS STAR RATINGS WORKFLOW                           │
└─────────────────────────────────────────────────────────────────────────┘

Step 1: Data Sources
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   HEDIS Measures                        Member Enrollments
   (Performance Data)                    (Demographics)
         ├─ 45 measures                       ├─ 50,000 members
         ├─ All domains                       ├─ Age, risk scores
         ├─ Performance rates                 └─ Plan types
         └─ Target benchmarks                      │
               │                                   │
               ▼                                   ▼
   ┌────────────────────────┐          ┌────────────────────────┐
   │  measures_data table   │          │  member_enrollments    │
   │  • Performance metrics │          │  • Population data     │
   │  • Gap calculations    │          │  • Risk stratification │
   └────────────────────────┘          └────────────────────────┘
               │                                   │
               └───────────────┬───────────────────┘
                               │
Step 2: AI Analysis           │
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━▼━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    ┌──────────────────────┐
                    │   UC AI Functions    │
                    │   (Claude Sonnet 4.5)│
                    │                      │
                    │ • classify()         │
                    │ • analyze()          │
                    │ • recommend()        │
                    │ • explain()          │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  star_analysis table │
                    │  • Classifications   │
                    │  • Root causes       │
                    │  • Recommendations   │
                    └──────────┬───────────┘
                               │
Step 3: Knowledge Base        │
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━▼━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
              HEDIS Guidelines
              (Best Practices)
         ├─ Screening measures
         ├─ Care quality measures
         ├─ Improvement strategies
         └─ Member outreach tips
                    │
                    ▼
         ┌────────────────────┐
         │ Chunk Documents    │
         │ • Split for search │
         │ • Extract keywords │
         └──────────┬─────────┘
                    │
                    ▼
         ┌────────────────────┐
         │  Vector Search     │
         │  • Semantic search │
         │  • Find relevant   │
         │    guidelines      │
         └──────────┬─────────┘
                    │
Step 4: Predictions & Insights│
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━▼━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    ┌──────────────────────┐
                    │  star_predictions    │
                    │  • Future ratings    │
                    │  • Improvement impact│
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Streamlit Dashboard │
                    │  • Visualizations    │
                    │  • StateGraph agent  │
                    │  • Natural language  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  ACTIONABLE INSIGHTS │
                    │  ✅ Prioritized gaps │
                    │  📋 Action plans     │
                    └──────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Processing Time: Real-time  |  Insight Generation: Seconds
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🔍 Verification

### **Check Deployment Status**

```bash
# Check if app is running
databricks apps get payerstars-dev --profile DEFAULT_azure

# Check if catalog was created
databricks catalogs get payer_stars_dev --profile DEFAULT_azure

# Check if tables exist
databricks tables list \
  --catalog-name payer_stars_dev \
  --schema-name star_ratings \
  --profile DEFAULT_azure
```

### **Expected Output**

You should see:
- **Catalog**: `payer_stars_dev`
- **Schema**: `star_ratings`
- **Tables**: 
  - `measures_data` (45 rows)
  - `member_enrollments` (50,000 rows)
  - `hedis_docs_staging` (5 rows)
  - `hedis_guidelines_kb` (~25 chunks)
  - `star_analysis` (analyzed measures)
  - `star_predictions` (predictions)
  - `config_genie` (configuration)
- **Functions**: 4 AI functions (star_measure_classify, star_gap_analyze, star_improvement_recommend, star_explain)
- **Vector Index**: `hedis_guidelines_index` (ONLINE)
- **App**: `payerstars-dev` (status: RUNNING)

### **Test UC Functions**

```sql
-- Test classification
SELECT payer_stars_dev.star_ratings.star_measure_classify(
  'BCS: Breast Cancer Screening, Performance 62%, Target 75%, Gap 13%'
);

-- Test gap analysis
SELECT payer_stars_dev.star_ratings.star_gap_analyze(
  'CDC: Diabetes Care, Performance 68%, Target 80%, Gap 12%'
);

-- Test recommendations
SELECT payer_stars_dev.star_ratings.star_improvement_recommend(
  'BCS: Performance 62%, Target 75%, Gap 13%',
  '{"root_causes": ["Low outreach", "Access barriers"]}'
);

-- Test explanations
SELECT payer_stars_dev.star_ratings.star_explain(
  'CBP: Blood Pressure Control, Performance 65%, Target 78%',
  'High member impact measure'
);
```

---

## 🆘 Troubleshooting

### **Understanding Error Recovery**

**Automatic Recovery (Built-in):** The deployment scripts (`deploy_with_config.sh` and `deploy_app_source.sh`) have automatic error recovery built directly into them. They handle common issues like "active deployment in progress" without any user action needed.

**Manual Troubleshooting (Rarely Needed):** Only if automatic recovery fails (rare), you'll see suggestions to use the manual troubleshooting tool. This is a safety net, not a normal deployment step.

```
┌──────────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING STRATEGY                       │
└──────────────────────────────────────────────────────────────────┘

MOST CASES (95%):
  Error occurs → Script fixes automatically → Deployment succeeds ✅
  
RARE CASES (5%):
  Error occurs → Auto-fix fails → Script suggests manual tool ℹ️
  → User runs: ./fix_app_deployment.sh dev
  → User chooses recovery option → Fixed ✅
```

---

### **Common Issues and Solutions**

### **Problem: CLI version conflict / cache corruption**

**Symptoms:**
- `Error: cache: load: parse: invalid character '}' after top-level value`
- Authentication keeps failing even after login
- Multiple CLI versions shown when running commands
- Old CLI version (0.18.0) conflicts with new version (0.270.0)

**Cause:** Old Databricks CLI installed in conda environment conflicts with newer homebrew version, causing corrupted cache files.

**Solution:**

```bash
# 1. Check which CLI version you're using
which databricks
databricks --version

# 2. If you see old version (0.18.0) from conda, remove it
rm ~/anaconda3/envs/YOUR_ENV_NAME/bin/databricks
# Replace YOUR_ENV_NAME with your actual conda environment name

# 3. Verify you're now using the correct version
which databricks
# Should show: /opt/homebrew/bin/databricks (or /usr/local/bin/databricks)

databricks --version
# Should show: 0.270.0 or higher

# 4. Clear ALL corrupted cache and config files
rm -rf ~/.cache/databricks
rm -rf ~/.databricks  
rm -rf ~/.databrickscfg

# 5. Authenticate fresh with the profile name
databricks auth login --host https://your-workspace.azuredatabricks.net --profile DEFAULT_azure

# 6. Verify authentication works
databricks current-user me --profile DEFAULT_azure
```

**Key Points:**
- ✅ Use Databricks CLI 0.270.0+ (from homebrew/pip, not old databricks-cli package)
- ✅ Remove old CLI binaries from conda environments
- ✅ Clear cache files before re-authenticating
- ✅ Always specify `--profile DEFAULT_azure` to match your config

---

### **Problem: "Invalid access token" or authentication errors**

**Cause**: Your Databricks CLI authentication token has expired.

**Solution**: Refresh authentication

```bash
databricks auth login --profile DEFAULT_azure
```

Then retry the deployment:
```bash
./deploy_app_source.sh dev
```

**Note**: The script automatically uses the profile from your `config.yaml` (typically `DEFAULT_azure`). If authentication fails, the error message will show you the exact command to run.

---

### **Problem: App shows "Stopped" or "Compute is in stopped state"**

**Cause**: The app source code is deployed but the compute hasn't been started.

**Solution**: Start the app

**Option 1 - Via UI (Easiest):**
1. Go to Databricks → Compute → Apps
2. Find your app (`payerstars-dev`)
3. Click the blue **"Start"** button
4. Wait 30-60 seconds

**Option 2 - Via CLI:**
```bash
databricks apps start payerstars-dev --profile DEFAULT_azure
```

**Note**: The deployment scripts now automatically start the app after deploying source code. If you see this issue, it may be because:
- The auto-start failed (network/permissions issue)
- The app was manually stopped
- You're using an older version of the scripts

---

### **Problem: App shows "No source code" or "Not yet deployed"**

**Cause**: Bundle creates the app infrastructure but doesn't auto-deploy source code to compute ([per Microsoft docs](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/apps-tutorial#deploy-the-app-to-the-workspace))

**Solution**: Run the app deployment script
```bash
./deploy_app_source.sh dev
```

This deploys the source code from the bundle workspace location to the app.

### **Problem: "Cannot deploy app as there is an active deployment in progress"**

**Cause**: The app is currently deploying or stuck in a deployment state.

**✅ Automatic Recovery (No Action Needed)**: 

The deployment scripts detect this error and **automatically**:
1. Stop the app
2. Wait 15 seconds for it to fully stop
3. Retry the deployment

**You don't need to do anything** - just wait for the script to complete. You'll see messages like:

```
⚠️  Active deployment detected, stopping app and retrying...
Stopping app...
Waiting for app to stop...
Retrying deployment...
✅ Success!
```

**🔧 Manual Recovery (Only if Automatic Fails)**:

If you see the error persist after automatic retry, use the interactive troubleshooter:

```bash
./fix_app_deployment.sh dev
```

This tool offers 4 options:
1. **Stop app and redeploy** (fixes most issues) ← Choose this one
2. Restart app
3. Delete and recreate app (nuclear option)
4. Check detailed status

**Example:**
```bash
$ ./fix_app_deployment.sh dev

What would you like to do?
  1) Stop app and redeploy source code (fixes active deployment errors)
  2) Restart app (fixes stuck states)
  3) Delete and recreate app (nuclear option)
  4) Just check status

Enter choice (1-4): 1   ← Just type 1 and press Enter

🛑 Stopping app...
⏳ Waiting 15 seconds for app to stop...
🚀 Redeploying app source code...
✅ Success! App should be running now.
```

**Important:** `fix_app_deployment.sh` is **NOT** a normal deployment step. It's only used when automatic recovery fails, which is rare.

### **Problem: "Permission denied" errors**

**Solution**: Grant service principal permissions
```bash
./grant_permissions.sh dev
```

Or manually:
```bash
# Get service principal ID
SP_ID=$(databricks apps get payerstars-dev --profile DEFAULT_azure --output json | python3 -c "import sys, json; print(json.load(sys.stdin)['service_principal_id'])")

# Grant catalog access
databricks grants update catalog payer_stars_dev \
  --json "{\"changes\": [{\"principal\": \"$SP_ID\", \"add\": [\"USE_CATALOG\"]}]}" \
  --profile DEFAULT_azure

# Grant schema access
databricks grants update schema payer_stars_dev.star_ratings \
  --json "{\"changes\": [{\"principal\": \"$SP_ID\", \"add\": [\"USE_SCHEMA\", \"SELECT\", \"MODIFY\"]}]}" \
  --profile DEFAULT_azure

# Grant warehouse access
databricks permissions update sql/warehouses/YOUR_WAREHOUSE_ID \
  --json "{\"access_control_list\": [{\"service_principal_name\": \"$SP_ID\", \"permission_level\": \"CAN_USE\"}]}" \
  --profile DEFAULT_azure
```

### **Problem: App not found**

Check if deployment succeeded:
```bash
databricks apps list --profile DEFAULT_azure
```

If not listed, redeploy:
```bash
databricks bundle deploy --target dev --profile DEFAULT_azure
```

### **Problem: Setup notebooks failed**

Check job status:
```bash
databricks jobs list --profile DEFAULT_azure
databricks jobs list-runs --job-id <job-id> --limit 1 --profile DEFAULT_azure
```

Rerun failed job:
```bash
databricks bundle run setup_star_ratings --target dev --profile DEFAULT_azure
```

### **Problem: Vector index not syncing**

**Cause**: Vector indexes can take 10-15 minutes to sync initially

**Solution**: Check status in Databricks UI
```
Databricks UI → Catalog → Vector Search → Your Index
```

Wait for status: **ONLINE**

### **Problem: Vector Index or Genie Space already exists**

The setup notebooks check for existing resources. For a completely clean slate:

```bash
# Run cleanup notebook in Databricks workspace
# Navigate to: Workspace > setup > 00_CLEANUP
# Click "Run All"
# Then redeploy
```

---

## 🧹 Cleanup & Testing

### **Complete Cleanup** (Start Fresh)

If you need to start over or clean up all resources:

```bash
# Run cleanup notebook in Databricks
# Navigate to: Workspace > setup > 00_CLEANUP
# Click "Run All"
```

This deletes:
- Vector search index
- Unity Catalog and all contents
- All volumes
- All UC functions
- Setup job (optional)

### **Full End-to-End Test**

Perfect for testing before demos or validating changes:

```bash
# Step 1: Complete cleanup (removes everything)
# Run setup/00_CLEANUP.py in Databricks

# Step 2: Fresh deployment (creates everything from scratch)
./deploy_with_config.sh dev

# Step 3: Wait for vector index to sync (10-15 minutes)

# Step 4: Test the app
# Open: https://your-workspace.azuredatabricks.net/apps/payerstars-dev

# Step 5: Run validation tests (optional)
databricks bundle run validate_star_ratings --target dev --profile DEFAULT_azure
```

### **Expected Timeline**

| Phase | Time | Details |
|-------|------|---------|
| **Cleanup** | ~1-2 minutes | Delete catalog, indexes, functions |
| **Fresh Deployment** | ~15-18 minutes | Setup job completes |
| **Vector Index Sync** | ~10-15 minutes | Background process |
| **Total** | **~17-20 minutes** | For full deployment (+ 10-15 min for vector sync) |

---

## 📁 Project Structure

```
payer_stars/
├── config.yaml                  # ⭐ Configuration (edit this)
├── generate_app_yaml.py         # ⭐ Generator script (run this)
├── databricks.yml               # Databricks Asset Bundle config
├── deploy_with_config.sh        # ⭐ One-command deployment script
├── deploy_app_source.sh         # App deployment script
├── fix_app_deployment.sh        # 🔧 Troubleshooter for app issues
├── grant_permissions.sh         # Permission management script
├── requirements.txt             # Python dependencies
│
├── shared/
│   ├── __init__.py
│   └── config.py                # Config loader for notebooks
│
├── setup/                       # Setup notebooks (run by DAB)
│   ├── 00_CLEANUP.py           # ⭐ Cleanup script (new!)
│   ├── 01_create_catalog_schema.py
│   ├── 02_generate_measures_data.py
│   ├── 03_generate_member_data.py
│   ├── 04_uc_star_classify.py
│   ├── 05_uc_star_analyze.py
│   ├── 06_uc_star_recommend.py
│   ├── 07_uc_star_explain.py
│   ├── 08_create_knowledge_base.py
│   ├── 09_chunk_knowledge_base.py
│   ├── 10_create_vector_index.py
│   ├── 11_create_analysis_table.py
│   ├── 12_batch_analyze_measures.py
│   ├── 13_create_predictions.py
│   ├── 14_create_genie_space.py
│   └── 99_validate_system.py
│
└── app/                         # Streamlit application
    ├── app.yaml                 # Auto-generated (don't edit)
    ├── app.py                   # Main app
    ├── requirements.txt         # Dependencies
    ├── utils/
    │   └── star_agent.py        # StateGraph agent implementation
    └── pages/                   # Streamlit pages
        ├── 1_measure_analysis.py
        ├── 2_improvement_planner.py
        └── 3_analytics_dashboard.py
```

---

## 🔧 Configuration

### **File Structure**

```
config.yaml              # ← Edit this (source of truth)
    ↓
generate_app_yaml.py     # ← Run this (generates app config)
    ↓
app/app.yaml            # ← Auto-generated (don't edit)
    ↓
Deploy!
```

### **Multiple Environments**

The system supports dev, staging, and prod environments:

```yaml
# config.yaml
environments:
  dev:
    catalog: "payer_stars_dev"
  staging:
    catalog: "payer_stars_staging"
  prod:
    catalog: "payer_stars_prod"
```

Deploy to different environments:

```bash
# Dev
./deploy_with_config.sh dev

# Staging
./deploy_with_config.sh staging

# Prod
./deploy_with_config.sh prod
```

---

## 🧪 Validation Testing

The system includes comprehensive validation tests via `99_validate_system.py`.

### **What's Tested**

- ✅ Catalog and schema access
- ✅ All table row counts and data quality
- ✅ All 4 UC functions with real queries
- ✅ Knowledge base documents and chunks
- ✅ Vector search status
- ✅ Analysis pipeline results
- ✅ Performance benchmarks

### **Running Validation Tests**

**Manual (anytime):**
```bash
# Navigate to: Workspace > setup > 99_validate_system
# Attach to any cluster
# Click "Run All"
```

**Via Databricks CLI:**
```bash
databricks workspace export \
  /Workspace/Users/your-email/.bundle/payer_star_ratings/dev/files/setup/99_validate_system.py \
  --profile DEFAULT_azure
```

**Expected Runtime:** ~3-5 minutes

**Expected Output:**
```
🎯 Overall Health Score: 95-100%
✅ Passed: 27/27 tests
⚠️  Warnings: 0
❌ Failed: 0

Status: EXCELLENT - System fully operational
```

---

## 💰 Business Impact

### **For Medicare Advantage Payers (like Humana)**
- **5-Star Rating Achievement**: Enhanced CMS rebate payments (up to 70% vs 50% for <3.5 stars)
- **Quality Bonus Program**: Additional payments for 4+ star plans
- **Member Growth**: Higher ratings improve member retention and acquisition
- **Financial Model**: Calculate ROI of measure improvements with weighted scoring
- **Part D Focus**: Prioritize 3x weighted medication adherence measures
- **Readmissions Reduction**: Target 3x weighted hospital readmissions measure

### **Quality Improvement Benefits**
- **Faster improvement planning**: Days → Minutes for gap analysis
- **AI-powered insights**: Root cause analysis with Claude Sonnet 4.5
- **Weighted prioritization**: Focus on 3x measures (outcomes, Part D) vs 1x (preventive)
- **Medicare-specific guidance**: Geriatric population strategies (seniors 65+)
- **Member impact**: 50K+ Medicare member population analysis
- **What-if scenarios**: Model star rating impact of specific measure improvements

### **CMS Star Ratings Methodology**
- **Weighted Scoring**: 3x for outcomes, 2x for experience/access, 1x for preventive
- **Cut Points**: ≥4.25 = 5 stars | 3.75-4.24 = 4 stars | 3.25-3.74 = 3 stars
- **Financial Impact**: 5-star plans receive enhanced rebates, quality bonuses, member growth
- **Strategic Planning**: Calculator shows exact point improvements needed for next star tier

---

## 🔒 Security & Compliance

- **HIPAA-compliant** via Unity Catalog governance
- **Complete audit trails** for all AI decisions
- **Explainable AI** with HEDIS guideline citations
- **Role-based access** control via Unity Catalog
- **CMS-ready** architecture for star ratings reporting

---

## 📊 Project Status

**✅ Project Complete - January 2026**

This is a production-ready CMS star ratings system demonstrating:
- **Modern AI Architecture**: LangGraph StateGraph + UC Functions + Vector Search
- **Real Healthcare Value**: Automated gap analysis, improvement recommendations, predictive insights
- **Quality Compliance**: HEDIS integration, audit trails, explainable AI
- **Fully Automated**: One-command deployment, complete documentation

**Built with:**
- Databricks Lakehouse Platform
- Unity Catalog & AI Functions
- LangGraph StateGraph
- Vector Search
- Claude Sonnet 4.5
- Streamlit

---

**Built with ❤️ for healthcare quality improvement | January 2026**
