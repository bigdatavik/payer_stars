# Quick Reference: Setup Resources Configuration

## 🎯 What Changed?

Hardcoded URLs → Configurable in `config.yaml` ✅

## 📍 Where to Configure

Edit `config.yaml`:
```yaml
environments:
  dev:
    notebooks_folder_url: "https://your-workspace/browse/folders/123?o=123"
    setup_job_url: "https://your-workspace/jobs/456?o=123"
```

## 🔍 How to Find URLs

### Notebooks URL
1. Databricks Workspace → Folders
2. Navigate: `.bundle/payer_star_ratings/dev/files/setup/`
3. Copy URL from browser

### Job URL  
1. Databricks Workflows → Jobs
2. Find: `payer_stars_setup_dev`
3. Copy URL from browser

## 🚀 Deploy After Changes

```bash
# Regenerate app.yaml
python generate_app_yaml.py dev

# Deploy
databricks bundle deploy

# Or use all-in-one script
./deploy_with_config.sh dev
```

## 🆘 If URLs Are Empty?

The app will show a warning message but won't crash. Update `config.yaml` and redeploy.

## 📖 Full Documentation

- User guide: `docs/SETUP_RESOURCES_CONFIG.md`
- Technical details: `docs/CHANGES_SETUP_RESOURCES.md`
- Summary: `docs/SUMMARY_SETUP_RESOURCES.md`

## ✅ Status

- [x] Indentation error fixed
- [x] URLs moved to config.yaml
- [x] Multi-environment support
- [x] Graceful degradation
- [x] Documentation complete
- [x] Production ready

---
*January 29, 2026*
