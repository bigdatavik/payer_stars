#!/bin/bash
# Deploy script for Payer Star Ratings - auto-generates app.yaml

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get environment from argument or default to 'dev'
ENVIRONMENT=${1:-dev}

echo "========================================================================"
echo "🚀 PAYER STAR RATINGS DEPLOYMENT"
echo "========================================================================"
echo "Environment: ${ENVIRONMENT}"
echo ""

# Pre-flight checks
echo "🔍 Pre-flight checks..."
echo ""

# Step 1: Validate config.yaml exists
if [ ! -f "config.yaml" ]; then
    echo -e "${RED}❌ ERROR: config.yaml not found!${NC}"
    echo "Please create config.yaml in project root"
    exit 1
fi

# Step 2: Load profile from config
PROFILE=$(python3 -c "
import yaml
import sys
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    print(config['environments']['${ENVIRONMENT}']['profile'])
except Exception as e:
    print('', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null)

if [ -z "$PROFILE" ]; then
    echo -e "${RED}❌ ERROR: Could not load profile from config.yaml${NC}"
    exit 1
fi

echo "  ✅ Config file found"
echo "  📋 Profile: $PROFILE"

# Step 3: Check Databricks CLI
if ! command -v databricks &> /dev/null; then
    echo -e "${RED}❌ ERROR: Databricks CLI not found${NC}"
    echo "Install it with: pip install databricks-cli"
    exit 1
fi
echo "  ✅ Databricks CLI found"

# Step 4: Check authentication
echo "  🔐 Checking authentication..."
AUTH_CHECK=$(databricks current-user me --profile "$PROFILE" 2>&1)
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERROR: Authentication failed${NC}"
    echo ""
    echo "Error details:"
    echo "$AUTH_CHECK"
    echo ""
    echo -e "${YELLOW}💡 Fix: Authenticate with Databricks${NC}"
    echo "  databricks auth login --profile $PROFILE"
    echo ""
    echo "Then re-run:"
    echo "  ./deploy_with_config.sh ${ENVIRONMENT}"
    exit 1
fi
echo "  ✅ Authentication valid"
echo ""
echo -e "${GREEN}✅ All pre-flight checks passed${NC}"
echo ""

# Store APP_NAME for later use
APP_NAME="payerstars-${ENVIRONMENT}"

# Step 1: Validate config.yaml exists (already done above, remove duplicate)
# Generate app.yaml from config.yaml
echo "📝 Step 1: Generating app/app.yaml from config.yaml..."
python3 generate_app_yaml.py ${ENVIRONMENT}

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERROR: Failed to generate app.yaml${NC}"
    exit 1
fi

echo -e "${GREEN}✅ app.yaml generated successfully${NC}"
echo ""

# Step 3: Validate databricks.yml exists
if [ ! -f "databricks.yml" ]; then
    echo -e "${RED}❌ ERROR: databricks.yml not found!${NC}"
    exit 1
fi

# Step 4: Deploy with Databricks Asset Bundles
echo "📦 Step 2: Deploying with Databricks Asset Bundles..."
databricks bundle deploy --target ${ENVIRONMENT}

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERROR: Deployment failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Deployment successful${NC}"
echo ""

# Step 5: Run setup job to create all resources
echo "⚙️  Step 3: Running setup job (creates catalog, tables, functions, data)..."
echo ""

databricks bundle run setup_star_ratings --target ${ENVIRONMENT}

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERROR: Setup job failed${NC}"
    echo "Check the job logs in Databricks for details"
    exit 1
fi

echo -e "${GREEN}✅ Setup job completed successfully${NC}"
echo ""

# Step 6: Grant permissions to app service principal
echo "🔒 Step 4: Granting service principal permissions..."
echo ""
echo "⏳ Waiting 10 seconds for app to fully initialize..."
sleep 10

./grant_permissions.sh ${ENVIRONMENT}

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  WARNING: Permission grant failed${NC}"
    echo "You can manually grant permissions later by running:"
    echo "  ./grant_permissions.sh ${ENVIRONMENT}"
    echo ""
fi

# Step 7: Deploy app source code
echo "🚀 Step 5: Deploying app source code..."
echo ""
echo "⏳ Waiting for app to be ready for deployment (checking status)..."

# Wait a moment for the app to be fully initialized
sleep 5

# Check if there's an active deployment and wait for it
for i in {1..12}; do
    APP_STATUS=$(databricks apps get "$APP_NAME" --profile "$PROFILE" --output json 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('compute_status', {}).get('state', 'UNKNOWN'))" 2>/dev/null || echo "UNKNOWN")
    
    if [ "$APP_STATUS" != "DEPLOYING" ]; then
        echo "✅ App ready for deployment (status: $APP_STATUS)"
        break
    fi
    
    echo "  App is still deploying, waiting... ($i/12)"
    sleep 10
done

# Deploy app source code (script starts app if stopped and retries on "active deployment in progress")
./deploy_app_source.sh ${ENVIRONMENT}

DEPLOY_EXIT_CODE=$?

if [ $DEPLOY_EXIT_CODE -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}⏳ App deploy failed; waiting 90s then retrying once...${NC}"
    sleep 90
    ./deploy_app_source.sh ${ENVIRONMENT}
    DEPLOY_EXIT_CODE=$?
fi

if [ $DEPLOY_EXIT_CODE -ne 0 ]; then
    echo ""
    echo -e "${RED}❌ ERROR: App deployment failed${NC}"
    echo ""
    echo -e "${YELLOW}💡 Next steps:${NC}"
    echo "  1. Check if authentication is still valid:"
    echo "     databricks auth login --profile $PROFILE"
    echo "  2. Retry app deployment:"
    echo "     ./deploy_app_source.sh ${ENVIRONMENT}"
    echo ""
    echo "Note: Infrastructure and data are already deployed."
    echo "      Only the app needs to be redeployed."
    exit 1
fi

# Verify app is running
echo ""
echo "🔍 Verifying app status..."
APP_STATE=$(databricks apps get "$APP_NAME" --profile "$PROFILE" --output json 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('compute_status', {}).get('state', 'UNKNOWN'))" 2>/dev/null || echo "UNKNOWN")

if [ "$APP_STATE" == "ACTIVE" ] || [ "$APP_STATE" == "RUNNING" ]; then
    echo -e "${GREEN}✅ App is running (status: $APP_STATE)${NC}"
elif [ "$APP_STATE" == "STARTING" ]; then
    echo -e "${YELLOW}⏳ App is starting (status: $APP_STATE)${NC}"
    echo "   Wait 30-60 seconds for it to become active"
else
    echo -e "${YELLOW}⚠️  App status: $APP_STATE${NC}"
    echo "   You may need to start it manually:"
    echo "   databricks apps start $APP_NAME --profile $PROFILE"
fi

echo "========================================================================"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
echo "========================================================================"
echo ""
echo "What was deployed:"
echo "  ✅ Infrastructure (job definitions, app definition)"
echo "  ✅ Setup job executed (catalog, schema, tables, functions, data)"
echo "  ✅ Service principal permissions granted"
echo "  ✅ Streamlit app source code deployed"
echo ""
echo "⚠️  IMPORTANT: Configure Genie Space Instructions"
echo "  1. Go to Databricks: Data Intelligence > Genie > Star Ratings Analytics"
echo "  2. Click Settings (gear icon)"
echo "  3. Copy instructions from setup job output (task: create_genie_space)"
echo "  4. Paste into Instructions field and Save"
echo ""
echo "Next steps:"
echo "  1. Wait 30-60 seconds for app to start"
echo "  2. Access app:"
echo "     https://<workspace>/apps/payerstars-${ENVIRONMENT}"
echo ""
echo "Configuration used:"
echo "  - Environment: ${ENVIRONMENT}"
echo "  - Config file: config.yaml"
echo "  - Generated: app/app.yaml"
echo "========================================================================"
