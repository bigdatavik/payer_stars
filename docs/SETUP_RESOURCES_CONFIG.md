# Setup Resources Configuration Guide

## Overview

The **Setup Resources** page (`app/pages/5_setup_resources.py`) provides quick links to view setup notebooks and jobs in your Databricks workspace. These URLs are now configurable per environment in `config.yaml`.

## Configuration Location

All URLs are stored in `config.yaml` under each environment section:

```yaml
environments:
  dev:
    # ... other settings ...
    notebooks_folder_url: "https://your-workspace.net/browse/folders/123456?o=123456"
    setup_job_url: "https://your-workspace.net/jobs/789012?o=123456"
```

## How to Find These URLs

### 1. Notebooks Folder URL

After deploying your bundle, the setup notebooks are located in a workspace folder. To find the URL:

1. Open your Databricks workspace
2. Navigate to **Workspace** → **Folders**
3. Find the bundle folder: `.bundle/payer_star_ratings/dev/files/setup/`
4. Click on the `setup` folder
5. Copy the URL from your browser's address bar
6. Paste it into `config.yaml` under `notebooks_folder_url`

**Example URL format:**
```
https://adb-984752964297111.11.azuredatabricks.net/browse/folders/908565040797499?o=984752964297111
```

### 2. Setup Job URL

After deploying your bundle, a job is created to orchestrate all setup notebooks. To find the URL:

1. Open your Databricks workspace
2. Navigate to **Workflows** → **Jobs**
3. Find the job: `payer_stars_setup_dev` (or `payer_stars_setup_staging`, `payer_stars_setup_prod`)
4. Click on the job
5. Copy the URL from your browser's address bar
6. Paste it into `config.yaml` under `setup_job_url`

**Example URL format:**
```
https://adb-984752964297111.11.azuredatabricks.net/jobs/675854142625590?o=984752964297111
```

## Configuration for All Environments

Update `config.yaml` for each environment you deploy:

```yaml
environments:
  dev:
    # ... other settings ...
    notebooks_folder_url: "YOUR_DEV_NOTEBOOKS_URL"
    setup_job_url: "YOUR_DEV_JOB_URL"

  staging:
    # ... other settings ...
    notebooks_folder_url: "YOUR_STAGING_NOTEBOOKS_URL"
    setup_job_url: "YOUR_STAGING_JOB_URL"

  prod:
    # ... other settings ...
    notebooks_folder_url: "YOUR_PROD_NOTEBOOKS_URL"
    setup_job_url: "YOUR_PROD_JOB_URL"
```

## Regenerate app.yaml

After updating `config.yaml`, regenerate `app/app.yaml`:

```bash
python generate_app_yaml.py dev        # For dev environment
python generate_app_yaml.py staging    # For staging environment
python generate_app_yaml.py prod       # For prod environment
```

Or use the deployment script which does this automatically:

```bash
./deploy_with_config.sh dev
```

## How It Works

1. **config.yaml** → Contains the URLs for each environment
2. **generate_app_yaml.py** → Reads `config.yaml` and generates `app/app.yaml` with environment variables
3. **app/app.yaml** → Defines environment variables that the Streamlit app reads
4. **app/pages/5_setup_resources.py** → Reads environment variables and displays the links

## Graceful Degradation

If URLs are not configured (empty strings), the page will:
- Display a warning message asking users to update `config.yaml`
- Still show the folder path and job name for reference
- Remain functional (no errors)

## Example: Complete dev Configuration

```yaml
dev:
  workspace_host: "https://adb-984752964297111.11.azuredatabricks.net"
  profile: "DEFAULT_azure"
  catalog: "payer_stars_dev"
  schema: "star_ratings"
  warehouse_id: "148ccb90800933a1"
  vector_endpoint: "one-env-shared-endpoint-2"
  llm_endpoint: "databricks-claude-sonnet-4-5"
  app_name: "payerstars-dev"
  genie_space_id: "01jktv1234567890"
  
  # Setup Resources URLs
  notebooks_folder_url: "https://adb-984752964297111.11.azuredatabricks.net/browse/folders/908565040797499?o=984752964297111"
  setup_job_url: "https://adb-984752964297111.11.azuredatabricks.net/jobs/675854142625590?o=984752964297111"
```

## Benefits of This Approach

✅ **Single source of truth**: All configuration in `config.yaml`  
✅ **Environment-specific**: Different URLs for dev/staging/prod  
✅ **Auto-generated**: `app.yaml` is generated from `config.yaml`  
✅ **No hardcoding**: No hardcoded URLs in Python files  
✅ **Graceful degradation**: App works even if URLs aren't configured  
✅ **Easy to update**: Change URLs in one place (`config.yaml`)

## Troubleshooting

### URLs not showing in app?

1. Check that `config.yaml` has the URLs filled in
2. Regenerate `app.yaml`: `python generate_app_yaml.py dev`
3. Verify `app/app.yaml` contains `NOTEBOOKS_FOLDER_URL` and `SETUP_JOB_URL`
4. Redeploy the app: `databricks bundle deploy`

### Getting "URL not configured" warning?

- The URLs in `config.yaml` are empty strings (`""`)
- Follow the steps above to find and add the correct URLs
- Regenerate `app.yaml` and redeploy

## Questions?

See the main README.md or contact the project maintainer.
