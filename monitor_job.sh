#!/bin/bash
# Autonomous monitoring script for payer_stars setup job

RUN_ID="$1"
PROFILE="DEFAULT_azure"
MAX_WAIT=1800  # 30 minutes max
CHECK_INTERVAL=30
elapsed=0

echo "🤖 AUTONOMOUS AGENT MONITORING JOB: $RUN_ID"
echo "================================================"

while [ $elapsed -lt $MAX_WAIT ]; do
    # Get job status
    status=$(databricks jobs get-run $RUN_ID --profile $PROFILE --output json 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    state = data.get('state', {}).get('life_cycle_state', 'UNKNOWN')
    result = data.get('state', {}).get('result_state', 'N/A')
    
    # Count completed tasks
    tasks = data.get('tasks', [])
    completed = sum(1 for t in tasks if t.get('state', {}).get('result_state') == 'SUCCESS')
    failed = sum(1 for t in tasks if t.get('state', {}).get('result_state') == 'FAILED')
    total = len(tasks)
    
    print(f'{state}|{result}|{completed}|{failed}|{total}')
except:
    print('ERROR|ERROR|0|0|0')
" 2>/dev/null)
    
    IFS='|' read -r lifecycle result completed failed total <<< "$status"
    
    echo "[$(date +%H:%M:%S)] State: $lifecycle | Result: $result | Progress: $completed/$total tasks | Failed: $failed"
    
    # Check if job is done
    if [ "$lifecycle" = "TERMINATED" ]; then
        if [ "$result" = "SUCCESS" ]; then
            echo ""
            echo "✅ JOB COMPLETED SUCCESSFULLY!"
            echo "   Completed: $completed/$total tasks"
            echo "================================================"
            exit 0
        else
            echo ""
            echo "❌ JOB FAILED"
            echo "   Completed: $completed/$total tasks"
            echo "   Failed: $failed tasks"
            echo "================================================"
            
            # Get failed task details
            databricks jobs get-run $RUN_ID --profile $PROFILE --output json 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tasks = data.get('tasks', [])
    for task in tasks:
        if task.get('state', {}).get('result_state') == 'FAILED':
            print(f\"FAILED: {task.get('task_key')}\")
            print(f\"  Message: {task.get('state', {}).get('state_message', 'No message')}\")
except:
    pass
"
            exit 1
        fi
    fi
    
    sleep $CHECK_INTERVAL
    elapsed=$((elapsed + CHECK_INTERVAL))
done

echo ""
echo "⏰ TIMEOUT after $MAX_WAIT seconds"
echo "   Job still running, check manually"
exit 2
