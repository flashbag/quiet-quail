#!/bin/bash

# Dashboard development server with auto-reload
# Usage: ./dev.sh [port]

set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if watchdog is installed
cd "$PROJECT_ROOT"

if [ ! -d ".venv" ] && [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Check if watchdog is installed
if ! python3 -c "import watchdog" 2>/dev/null; then
    echo "⚠️  watchdog not found. Installing..."
    pip install watchdog>=4.0.0
fi

echo "🎯 Starting Quiet-Quail Dashboard in Development Mode"
echo "═══════════════════════════════════════════════════════════"

# Run the dev server
python3 "$SCRIPT_DIR/dashboard_dev.py" "$@"
