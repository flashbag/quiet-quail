#!/bin/bash

# Summary script - Show project status from root folder

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONSOLIDATED_FILE="$PROJECT_ROOT/data/consolidated_unique.json"
SYNC_LOG="$PROJECT_ROOT/data/.sync_log"
CONFIG_FILE="$PROJECT_ROOT/.sync_config.json"

echo "📊 Quiet-Quail Project Summary"
echo "================================"
echo ""

# Total jobs
if [ -f "$CONSOLIDATED_FILE" ]; then
    total_jobs=$(python -c "import json; data = json.load(open('$CONSOLIDATED_FILE')); print(data.get('total_unique_jobs', 'N/A'))" 2>/dev/null || echo "N/A")
    echo "✓ Total unique jobs: $total_jobs"
else
    echo "✗ Consolidated data not found"
fi

# Last sync time
if [ -f "$SYNC_LOG" ]; then
    last_sync=$(python -c "
import json
try:
    with open('$SYNC_LOG') as f:
        logs = json.load(f)
        if logs:
            last = logs[-1]
            print(f\"{last.get('status', 'N/A')} - {last.get('timestamp', 'N/A')}\")
except:
    print('N/A')
" 2>/dev/null || echo "N/A")
    echo "📅 Last sync: $last_sync"
else
    echo "📅 Last sync: Never"
fi

# Sync configured
if [ -f "$CONFIG_FILE" ]; then
    remote=$(python -c "import json; data = json.load(open('$CONFIG_FILE')); print(f\"{data.get('remote_user', '?')}@{data.get('remote_host', '?')}\")" 2>/dev/null || echo "N/A")
    echo "✓ Sync configured: $remote"
else
    echo "✗ Sync not configured"
fi

# Data files
if [ -d "$PROJECT_ROOT/data/2025" ]; then
    file_count=$(find "$PROJECT_ROOT/data/2025" -name "output_*.json" 2>/dev/null | wc -l | tr -d ' ')
    echo "📁 Parsed data files: $file_count"
fi

# Job pages crawled
if [ -d "$PROJECT_ROOT/data/job-pages" ]; then
    page_count=$(find "$PROJECT_ROOT/data/job-pages" -name "*.html" 2>/dev/null | wc -l | tr -d ' ')
    echo "🔗 Job pages crawled: $page_count"
fi

# Dashboard status
if [ -f "$PROJECT_ROOT/web/dashboard.html" ]; then
    echo "✓ Dashboard: Ready"
fi

echo ""
echo "Commands:"
echo "  ./sync.sh sync          - Sync data from remote VPS"
echo "  python tools/consolidate_jobs.py --stats  - Show consolidation stats"
echo "  python web/dashboard_server.py  - Start dashboard server"
