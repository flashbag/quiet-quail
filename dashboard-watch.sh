#!/bin/bash
# Convenience script to run dashboard with auto-reload on file changes
# Usage: ./dashboard-watch.sh or bash dashboard-watch.sh

set -e

echo "=========================================="
echo "Dashboard Server with Auto-Reload"
echo "=========================================="
echo ""
echo "This script will:"
echo "  1. Start the dashboard server"
echo "  2. Watch for file changes"
echo "  3. Auto-restart on any changes"
echo ""
echo "Supported files: .html, .py, .css, .js, .json"
echo "Press Ctrl+C to stop"
echo ""

# Check if we're in the right directory
if [ ! -f "dashboard_server.py" ]; then
    echo "Error: dashboard_server.py not found"
    echo "Make sure you're in the Quiet-Quail project directory"
    exit 1
fi

# Check if watchdog is installed
python3 -c "import watchdog" 2>/dev/null || {
    echo "Installing watchdog..."
    pip install watchdog -q
}

# Run the watcher
python3 run_dashboard_watch.py
