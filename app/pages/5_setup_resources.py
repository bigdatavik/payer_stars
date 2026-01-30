"""
Setup Resources - Quick Links to Notebooks and Jobs
"""

import streamlit as st
import os

st.set_page_config(layout="wide", page_title="Setup Resources", page_icon="🔧")

st.title("🔧 Setup Resources")
st.markdown("Quick links to view setup notebooks and jobs in your Databricks workspace.")

st.markdown("---")

# Notebooks Section
st.header("📓 Setup Notebooks")
st.markdown("""
The setup notebooks create all the data, Unity Catalog functions, vector indexes, and Genie space.
View the notebooks to understand how the system is configured.
""")

# Read URLs from environment variables (set in app.yaml from config.yaml)
notebooks_url = os.getenv('NOTEBOOKS_FOLDER_URL', '')
job_url = os.getenv('SETUP_JOB_URL', '')
environment = os.getenv('ENVIRONMENT', 'dev')

# Display notebooks link if URL is configured
if notebooks_url:
    st.markdown(f"### [🔗 Open Setup Notebooks Folder]({notebooks_url})")
    st.caption(f"Path: `.bundle/payer_star_ratings/{environment}/files/setup/`")
else:
    st.warning("⚠️ Notebooks folder URL not configured. Please update `notebooks_folder_url` in `config.yaml` for the `{environment}` environment.")
    st.caption(f"Path: `.bundle/payer_star_ratings/{environment}/files/setup/`")
with st.expander("📋 15 Setup Notebooks"):
    st.markdown("""
    1. `00_CLEANUP.py` - Drop existing catalog and indexes
    2. `01_create_catalog_schema.py` - Create Unity Catalog structure
    3. `02_generate_measures_data.py` - Generate 42 HEDIS measures
    4. `03_generate_member_data.py` - Generate 50K member records
    5. `04_uc_star_classify.py` - Create classify UC function
    6. `05_uc_star_analyze.py` - Create gap analysis UC function
    7. `06_uc_star_recommend.py` - Create recommendation UC function
    8. `07_uc_star_explain.py` - Create explanation UC function
    9. `08_create_knowledge_base.py` - Generate HEDIS guidelines
    10. `09_chunk_knowledge_base.py` - Chunk guidelines for embeddings
    11. `10_create_vector_index.py` - Create vector search index
    12. `11_create_analysis_table.py` - Create analysis results table
    13. `12_batch_analyze_measures.py` - Pre-compute measure analysis
    14. `13_create_predictions.py` - Generate star rating predictions
    15. `14_create_genie_space.py` - Setup Genie for NL queries
    """)

st.markdown("---")

# Job Section
st.header("⚙️ Setup Job")
st.markdown("""
The setup job orchestrates all 15 notebooks in sequence with proper dependencies.
View the job to see execution history and timing.
""")

# Display job link if URL is configured
if job_url:
    st.markdown(f"### [🔗 Open Setup Job]({job_url})")
    st.caption(f"Job name: `payer_stars_setup_{environment}`")
else:
    st.warning(f"⚠️ Setup job URL not configured. Please update `setup_job_url` in `config.yaml` for the `{environment}` environment.")
    st.caption(f"Job name: `payer_stars_setup_{environment}`")

st.info("""
**From the job page you can:**
- View run history and execution times
- See task dependencies and timeline
- Monitor active runs
- Re-run the entire setup
""")

st.markdown("---")

# Additional Info
st.markdown("### 💡 About These Resources")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Notebooks**
    - Source of truth for setup logic
    - Can be edited and re-run individually
    - Located in DAB bundle workspace folder
    - Environment-specific (dev/prod)
    """)

with col2:
    st.markdown("""
    **Job**
    - Automated orchestration of all notebooks
    - Handles dependencies between tasks
    - Deployed via Databricks Asset Bundles
    - Tracks execution history
    """)

st.markdown("---")
st.caption("🔧 Setup Resources | Dynamically generated links for your workspace")
