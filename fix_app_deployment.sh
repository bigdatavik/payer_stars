#!/bin/bash
# Fix common app deployment issues
#
# Usage:
#   ./fix_app_deployment.sh [environment]
#
# This script handles common app deployment issues:
# - Active deployment in progress
# - App stuck in deploying state
# - App needs restart

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

ENVIRONMENT=${1:-dev}

echo "========================================================================"
echo "🔧 APP DEPLOYMENT TROUBLESHOOTER"
echo "========================================================================"
echo "Environment: ${ENVIRONMENT}"
echo ""

# Check if config.yaml exists
if [ ! -f "config.yaml" ]; then
    echo -e "${RED}❌ ERROR: config.yaml not found!${NC}"
    exit 1
fi

# Load config
echo "📝 Loading configuration..."
eval $(python3 -c "
import yaml
import sys
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    env = config['environments']['$ENVIRONMENT']
    print(f\"PROFILE='{env['profile']}'\")
    print(f\"APP_NAME='{env['app_name']}'\")
except Exception as e:
    print(f'ERROR: Failed to load config - {e}', file=sys.stderr)
    sys.exit(1)
")

if [ -z "$APP_NAME" ]; then
    echo -e "${RED}❌ ERROR: Failed to load configuration${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Configuration loaded${NC}"
echo "   Profile: $PROFILE"
echo "   App Name: $APP_NAME"
echo ""

# Check app status
echo "🔍 Checking app status..."
APP_STATUS=$(databricks apps get "$APP_NAME" --profile "$PROFILE" --output json 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    compute = data.get('compute_status', {})
    print(f\"State: {compute.get('state', 'UNKNOWN')}\")
    print(f\"Message: {compute.get('message', 'N/A')}\")
except:
    print('ERROR: Could not parse app status')
" 2>/dev/null) || {
    echo -e "${RED}❌ App not found or CLI error${NC}"
    echo "The app may need to be deployed first"
    echo ""
    echo "Run: ./deploy_with_config.sh $ENVIRONMENT"
    exit 1
}

echo "$APP_STATUS"
echo ""

# Ask user what they want to do
echo "What would you like to do?"
echo "  1) Stop app and redeploy source code (fixes active deployment errors)"
echo "  2) Restart app (fixes stuck states)"
echo "  3) Delete and recreate app (nuclear option)"
echo "  4) Just check status"
echo ""
read -p "Enter choice (1-4): " CHOICE

case $CHOICE in
    1)
        echo ""
        echo "🛑 Stopping app..."
        databricks apps stop "$APP_NAME" --profile "$PROFILE" || {
            echo -e "${YELLOW}⚠️  Stop command failed (app may already be stopped)${NC}"
        }
        
        echo "⏳ Waiting 15 seconds for app to stop..."
        sleep 15
        
        echo ""
        echo "🚀 Redeploying app source code..."
        ./deploy_app_source.sh "$ENVIRONMENT"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}✅ Success! App deployment complete.${NC}"
            echo ""
            echo "📊 Final app status:"
            databricks apps get "$APP_NAME" --profile "$PROFILE" | grep -E "(state|url)" || true
            echo ""
            echo -e "${BLUE}💡 If app shows STOPPED, it will auto-start. Wait 30-60 seconds.${NC}"
        else
            echo ""
            echo -e "${RED}❌ Deployment still failed.${NC}"
            echo "Try option 2 (Restart) or 3 (Delete and recreate)"
        fi
        ;;
        
    2)
        echo ""
        echo "🔄 Restarting app..."
        databricks apps restart "$APP_NAME" --profile "$PROFILE"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}✅ App restart initiated${NC}"
            echo "Wait 30-60 seconds for app to be available"
        else
            echo -e "${RED}❌ Restart failed${NC}"
        fi
        ;;
        
    3)
        echo ""
        echo -e "${RED}⚠️  WARNING: This will DELETE the app and recreate it${NC}"
        read -p "Are you sure? (yes/no): " CONFIRM
        
        if [ "$CONFIRM" == "yes" ]; then
            echo ""
            echo "🗑️  Deleting app..."
            databricks apps delete "$APP_NAME" --profile "$PROFILE"
            
            echo "⏳ Waiting 10 seconds..."
            sleep 10
            
            echo ""
            echo "🚀 Redeploying everything..."
            ./deploy_with_config.sh "$ENVIRONMENT"
            
            if [ $? -eq 0 ]; then
                echo ""
                echo -e "${GREEN}✅ Complete redeployment successful!${NC}"
            else
                echo ""
                echo -e "${RED}❌ Redeployment failed. Check logs above.${NC}"
            fi
        else
            echo "Cancelled."
        fi
        ;;
        
    4)
        echo ""
        echo "📊 Detailed app status:"
        databricks apps get "$APP_NAME" --profile "$PROFILE"
        ;;
        
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "========================================================================"
