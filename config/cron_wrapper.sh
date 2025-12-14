#!/bin/bash

# Cron wrapper script for Quiet-Quail project
# This script is run by cron and handles:
# 1. Activating the virtual environment
# 2. Running the fetch_lobbyx.py script
# 3. Logging output
# 4. Handling errors gracefully

# Get the directory where this script is located (config dir)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the project root (parent of config dir)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Set up logging
LOG_FILE="$PROJECT_ROOT/cron.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Append to log file
exec >> "$LOG_FILE" 2>&1

echo "========================================"
echo "[$TIMESTAMP] Running Quiet-Quail cron job"
echo "========================================"
echo "Project root: $PROJECT_ROOT"
echo "Current directory: $(pwd)"
echo "Current user: $(whoami)"
echo ""

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "ERROR: Virtual environment not found at $PROJECT_ROOT/venv"
    echo "Please run setup_server.sh first"
    exit 1
fi

# Change to project root
cd "$PROJECT_ROOT"

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

echo "Python version: $(python3 --version)"
echo ""

# Run the fetch_lobbyx.py script
echo "Running fetch_lobbyx.py..."
python3 scripts/fetch_lobbyx.py
FETCH_RESULT=$?

if [ $FETCH_RESULT -eq 0 ]; then
    echo "✓ fetch_lobbyx.py completed successfully"
else
    echo "✗ fetch_lobbyx.py failed with exit code: $FETCH_RESULT"
    exit $FETCH_RESULT
fi

echo ""
echo "[$TIMESTAMP] Cron job completed"
echo "========================================"
echo ""

exit 0
