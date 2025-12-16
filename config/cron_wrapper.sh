#!/bin/bash

# Cron wrapper script for Quiet-Quail project
# This script is run by cron and handles:
# 1. Activating the virtual environment
# 2. Running the fetch_lobbyx.py script
# 3. Logging output
# 4. Handling errors gracefully

set -e  # Exit on error

# Get the directory where this script is located (config dir)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the project root (parent of config dir)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Set up logging
LOG_FILE="$PROJECT_ROOT/cron.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Log function that writes to both stdout and log file
log_message() {
    local msg="$1"
    echo "[${TIMESTAMP}] ${msg}" | tee -a "$LOG_FILE"
}

log_message "========================================"
log_message "Starting Quiet-Quail cron job"
log_message "========================================"
log_message "Project root: $PROJECT_ROOT"
log_message "Current user: $(whoami)"
log_message "Host: $(hostname)"
log_message ""

# Check if project root exists
if [ ! -d "$PROJECT_ROOT" ]; then
    log_message "ERROR: Project root not found at $PROJECT_ROOT"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    log_message "ERROR: Virtual environment not found at $PROJECT_ROOT/venv"
    log_message "Please run setup_server.sh first"
    exit 1
fi

# Change to project root
cd "$PROJECT_ROOT" || {
    log_message "ERROR: Failed to change to project root: $PROJECT_ROOT"
    exit 1
}
log_message "Changed to: $(pwd)"

# Activate virtual environment
log_message "Activating virtual environment..."
if ! source venv/bin/activate 2>&1; then
    log_message "ERROR: Failed to activate virtual environment"
    exit 1
fi

log_message "Python version: $(python3 --version)"
log_message "Python path: $(which python3)"
log_message ""

# Check if cron pipeline script exists
if [ ! -f "$PROJECT_ROOT/run_cron_pipeline.py" ]; then
    log_message "ERROR: run_cron_pipeline.py not found at $PROJECT_ROOT/run_cron_pipeline.py"
    exit 1
fi

# Run the cron pipeline (stages 1-2 only: fetch + parse)
log_message "Running cron pipeline (fetch + parse only)..."
log_message "Starting at: $(date '+%Y-%m-%d %H:%M:%S')"

# Set a timeout of 30 minutes (1800 seconds) for fetch + parse
set +e
timeout 1800 python3 run_cron_pipeline.py 2>&1 | tee -a "$LOG_FILE"
PIPELINE_RESULT=$?
set -e

log_message "Ended at: $(date '+%Y-%m-%d %H:%M:%S')"

if [ $PIPELINE_RESULT -eq 0 ]; then
    log_message "✓ Cron pipeline completed successfully"
    log_message ""
    log_message "========================================"
    log_message "Cron job completed successfully"
    log_message "========================================"
    log_message ""
    exit 0
elif [ $PIPELINE_RESULT -eq 124 ]; then
    log_message "✗ Cron pipeline timed out (exceeded 30 minutes)"
    log_message ""
    log_message "========================================"
    log_message "Cron job failed: timeout"
    log_message "========================================"
    log_message ""
    exit 1
else
    log_message "✗ Cron pipeline failed with exit code: $PIPELINE_RESULT"
    log_message ""
    log_message "========================================"
    log_message "Cron job failed: exit code $PIPELINE_RESULT"
    log_message "========================================"
    log_message ""
    exit $PIPELINE_RESULT
fi

