# Changes Summary: Setup Resources URL Configuration

## Date: January 29, 2026

## Problem
The Setup Resources page (`app/pages/5_setup_resources.py`) had hardcoded URLs for the notebooks folder and setup job, making it difficult to:
- Support multiple environments (dev/staging/prod)
- Update URLs when deploying to different workspaces
- Maintain the single source of truth pattern

## Solution
Moved the URLs from hardcoded values to the centralized configuration system.

## Files Modified

### 1. `config.yaml` ✅
**Added new fields** for each environment:
```yaml
environments:
  dev:
    # ... existing fields ...
    notebooks_folder_url: "https://..."
    setup_job_url: "https://..."
```

**Changes:**
- Added `notebooks_folder_url` field to dev/staging/prod environments
- Added `setup_job_url` field to dev/staging/prod environments
- Added helpful comment at the top explaining how to find these URLs
- Dev environment has URLs populated, staging/prod have TODO placeholders

### 2. `generate_app_yaml.py` ✅
**Added environment variables** to the generated `app.yaml`:
```python
# Setup Resources URLs (for Setup Resources page)
- name: 'NOTEBOOKS_FOLDER_URL'
  value: '{env_config.get('notebooks_folder_url', '')}'
- name: 'SETUP_JOB_URL'
  value: '{env_config.get('setup_job_url', '')}'
```

**Changes:**
- Lines 78-83: Added two new environment variables to app.yaml template
- Uses `.get()` with empty string default for graceful degradation

### 3. `app/pages/5_setup_resources.py` ✅
**Replaced hardcoded URLs** with environment variable reads:

**Before:**
```python
# Hardcoded URLs (can be moved to config later)
notebooks_url = "https://adb-984752964297111.11.azuredatabricks.net/browse/folders/908565040797499?o=984752964297111"
job_url = "https://adb-984752964297111.11.azuredatabricks.net/jobs/675854142625590?o=984752964297111"
```

**After:**
```python
# Read URLs from environment variables (set in app.yaml from config.yaml)
notebooks_url = os.getenv('NOTEBOOKS_FOLDER_URL', '')
job_url = os.getenv('SETUP_JOB_URL', '')
environment = os.getenv('ENVIRONMENT', 'dev')
```

**Changes:**
- Removed hardcoded URLs
- Added environment variable reads
- Added graceful degradation with warning messages if URLs not configured
- Removed unused `WorkspaceClient` import
- Fixed indentation errors in the process

### 4. `app/app.yaml` ✅ (auto-generated)
**Added new environment variables:**
```yaml
# Setup Resources URLs (for Setup Resources page)
- name: 'NOTEBOOKS_FOLDER_URL'
  value: 'https://adb-984752964297111.11.azuredatabricks.net/browse/folders/908565040797499?o=984752964297111'
- name: 'SETUP_JOB_URL'
  value: 'https://adb-984752964297111.11.azuredatabricks.net/jobs/675854142625590?o=984752964297111'
```

**Note:** This file is auto-generated from config.yaml, so users should never edit it directly.

### 5. `docs/SETUP_RESOURCES_CONFIG.md` ✅ (new file)
**Created comprehensive documentation** explaining:
- How to find the URLs in Databricks workspace
- How to configure them in config.yaml
- How the configuration flows through the system
- Troubleshooting tips
- Complete examples

## Architecture Flow

```
┌─────────────────┐
│  config.yaml    │  ← User edits URLs here (single source of truth)
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ generate_app_yaml.py    │  ← Reads config.yaml, generates app.yaml
└────────┬────────────────┘
         │
         ▼
┌─────────────────┐
│  app/app.yaml   │  ← Contains environment variables
└────────┬────────┘
         │
         ▼
┌──────────────────────────────┐
│ app/pages/5_setup_resources.py│  ← Reads environment variables
└──────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  User sees URLs │  ← Links displayed in Streamlit UI
└─────────────────┘
```

## Benefits

✅ **Single source of truth**: All configuration in `config.yaml`  
✅ **Environment-specific**: Different URLs for dev/staging/prod  
✅ **No hardcoding**: Follows project's configuration pattern  
✅ **Graceful degradation**: App shows warnings if URLs not configured  
✅ **Easy maintenance**: Change URLs in one place  
✅ **Documentation**: Comprehensive guide for users  
✅ **Consistent pattern**: Matches how Genie Space ID is handled

## Testing

1. ✅ Fixed indentation error in `5_setup_resources.py`
2. ✅ Regenerated `app.yaml` successfully
3. ✅ Verified environment variables appear in `app.yaml`
4. ✅ Code reads from environment variables correctly
5. ✅ Graceful degradation works (empty URLs show warning)

## Next Steps for Users

1. **For dev environment**: URLs are already configured
2. **For staging/prod**: After deployment, update the URLs in `config.yaml`:
   - Find the notebooks folder URL in Databricks workspace
   - Find the setup job URL in Databricks workflows
   - Add them to `config.yaml` under the appropriate environment
   - Run `python generate_app_yaml.py staging` (or prod)
   - Redeploy: `./deploy_with_config.sh staging`

3. **See documentation**: `docs/SETUP_RESOURCES_CONFIG.md`

## Commit Message (Suggested)

```
feat: Move Setup Resources URLs to config.yaml

- Add notebooks_folder_url and setup_job_url to each environment in config.yaml
- Update generate_app_yaml.py to include these URLs as environment variables
- Refactor app/pages/5_setup_resources.py to read from environment variables
- Remove hardcoded URLs from Python code
- Add graceful degradation with warning messages
- Create comprehensive documentation in docs/SETUP_RESOURCES_CONFIG.md
- Fix indentation error in 5_setup_resources.py

Follows existing configuration pattern (single source of truth in config.yaml).
URLs are now environment-specific and easily maintainable.
```

## Files Created

- `docs/SETUP_RESOURCES_CONFIG.md` - Comprehensive user guide
- `docs/CHANGES_SETUP_RESOURCES.md` - This summary document

## Related Issues Fixed

- Indentation error in `app/pages/5_setup_resources.py` (line 29)
- Hardcoded URLs that don't work across environments
- No documentation for how to configure these URLs
