#!/bin/bash
# Deploy App Source Code
# This script deploys the Streamlit app source code to Databricks Apps

set -e

# ============================================================================
# Auto-detect Databricks CLI (v0.200+ required for bundle support)
# ============================================================================
DATABRICKS_CLI=""

# Check common installation locations in order of preference
for cli_path in /opt/homebrew/bin/databricks /usr/local/bin/databricks $(which databricks 2>/dev/null); do
    # Skip if path is empty or not executable
    if [ -z "$cli_path" ] || [ ! -x "$cli_path" ]; then
        continue
    fi
    
    # Get version and check if it's >= 0.200.0
    VERSION=$("$cli_path" --version 2>&1 | grep -oE 'v?[0-9]+\.[0-9]+\.[0-9]+' | head -1 | sed 's/v//')
    
    if [ -n "$VERSION" ]; then
        # Extract minor version (e.g., "270" from "0.270.0")
        MINOR=$(echo "$VERSION" | cut -d. -f2)
        
        # Check if minor version >= 200 (new CLI with bundle support)
        if [ "$MINOR" -ge 200 ] 2>/dev/null; then
            DATABRICKS_CLI="$cli_path"
            break
        fi
    fi
done

# Exit if no suitable CLI found
if [ -z "$DATABRICKS_CLI" ]; then
    echo "❌ Error: Databricks CLI v0.200+ not found"
    echo ""
    echo "Installation instructions:"
    echo "  macOS:   brew install databricks/tap/databricks"
    echo "  Linux:   curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh"
    echo ""
    exit 1
fi

# ============================================================================

ENVIRONMENT=${1:-dev}

echo "🚀 Deploying Streamlit App"
echo "Environment: $ENVIRONMENT"
echo ""

# Load config
APP_NAME=$(python3 -c "import yaml; cfg=yaml.safe_load(open('config.yaml')); print(cfg['environments']['$ENVIRONMENT']['app_name'])")
PROFILE=$(python3 -c "import yaml; cfg=yaml.safe_load(open('config.yaml')); print(cfg['environments']['$ENVIRONMENT']['profile'])")

echo "App Name: $APP_NAME"
echo "Profile: $PROFILE"
echo ""

# If app compute is STOPPED, start it and wait for ACTIVE so deploy can succeed
COMPUTE_STATE=$("$DATABRICKS_CLI" apps get "$APP_NAME" --profile "$PROFILE" --output json 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('compute_status', {}).get('state', 'UNKNOWN'))" 2>/dev/null || echo "UNKNOWN")
if [ "$COMPUTE_STATE" = "STOPPED" ]; then
    echo "⏳ App compute is stopped; starting app..."
    "$DATABRICKS_CLI" apps start "$APP_NAME" --profile "$PROFILE" 2>/dev/null || true
    echo "   Waiting for compute to become ACTIVE (up to 2 min)..."
    for _ in 1 2 3 4 5 6 7 8; do
        sleep 15
        COMPUTE_STATE=$("$DATABRICKS_CLI" apps get "$APP_NAME" --profile "$PROFILE" --output json 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('compute_status', {}).get('state', 'UNKNOWN'))" 2>/dev/null || echo "UNKNOWN")
        if [ "$COMPUTE_STATE" = "ACTIVE" ]; then
            echo "   ✅ Compute is ACTIVE"
            break
        fi
    done
    echo ""
fi

# Generate app.yaml from config for this environment, then upload to workspace via bundle
echo "📝 Generating app/app.yaml and uploading to workspace..."
python3 generate_app_yaml.py "$ENVIRONMENT"
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to generate app.yaml"
    exit 1
fi
"$DATABRICKS_CLI" bundle deploy --target "$ENVIRONMENT" --profile "$PROFILE"
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Bundle deploy failed"
    exit 1
fi
echo ""

# Get current Databricks username
CURRENT_USER=$("$DATABRICKS_CLI" current-user me --profile "$PROFILE" --output json 2>/dev/null | python3 -c "import sys, json; print(json.load(sys.stdin)['userName'])" 2>&1)

if [ $? -ne 0 ] || [ -z "$CURRENT_USER" ]; then
    echo "❌ ERROR: Could not determine current Databricks user"
    echo "Please ensure Databricks CLI is configured properly"
    exit 1
fi

# Construct the bundle workspace path where source code is deployed
# Pattern: /Workspace/Users/<username>/.bundle/<bundle-name>/<environment>/files/app
BUNDLE_NAME="payer_star_ratings"
BUNDLE_SOURCE_PATH="/Workspace/Users/${CURRENT_USER}/.bundle/${BUNDLE_NAME}/${ENVIRONMENT}/files/app"

echo "Current user: $CURRENT_USER"
echo "Bundle source path: $BUNDLE_SOURCE_PATH"
echo ""

# Deploy app from the bundle workspace path
echo "📤 Deploying app from bundle workspace location..."
DEPLOY_OUTPUT=$("$DATABRICKS_CLI" apps deploy "$APP_NAME" --source-code-path "$BUNDLE_SOURCE_PATH" --profile "$PROFILE" 2>&1)
DEPLOY_EXIT=$?
if [ $DEPLOY_EXIT -eq 0 ]; then
    echo "$DEPLOY_OUTPUT"
elif echo "$DEPLOY_OUTPUT" | grep -q "active deployment in progress\|Cannot deploy app"; then
    echo "   ⏳ Active deployment in progress; waiting 90s then retrying once..."
    sleep 90
    "$DATABRICKS_CLI" apps deploy "$APP_NAME" --source-code-path "$BUNDLE_SOURCE_PATH" --profile "$PROFILE"
    if [ $? -ne 0 ]; then
        echo "❌ ERROR: App deployment failed after retry"
        exit 1
    fi
else
    echo "$DEPLOY_OUTPUT"
    echo "❌ ERROR: App deployment failed"
    exit 1
fi

echo ""
echo "✅ App deployed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Start app: databricks apps start $APP_NAME --profile $PROFILE"
echo "   2. Get app URL: databricks apps get $APP_NAME --profile $PROFILE"
echo "   3. Open app in browser"
echo ""
