#!/bin/bash

# Dashboard development server with auto-reload
# Usage: ./dev.sh [port]

set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# The script is in the project root, not in a subdirectory
PROJECT_ROOT="$SCRIPT_DIR"

# Change to project root
cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✓ Activated virtual environment (.venv)"
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✓ Activated virtual environment (venv)"
else
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if watchdog is installed
if ! python3 -c "import watchdog" 2>/dev/null; then
    echo "⚠️  watchdog not found. Installing..."
    pip install watchdog>=4.0.0
fi

echo "🎯 Starting Quiet-Quail Dashboard in Development Mode"
echo "═══════════════════════════════════════════════════════════"

# Run the dev server
python3 "$PROJECT_ROOT/web/dashboard_dev.py" "$@"
