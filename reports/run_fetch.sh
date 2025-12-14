#!/bin/bash

# Quiet-Quail fetch runner
# This script activates the virtual environment and runs all data collection tasks
# Designed to be called by cron or manually

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

LOG_FILE="$SCRIPT_DIR/cron.log"
START_TIME=$(date '+%Y-%m-%d %H:%M:%S')

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

echo "" >> "$LOG_FILE"
log "=========================================="
log "🚀 Quiet-Quail Data Collection Started"
log "=========================================="

# Check virtual environment
if [ ! -f "$SCRIPT_DIR/venv/bin/python3" ]; then
    log "❌ ERROR: Virtual environment not found"
    exit 1
fi

# Activate virtual environment
log "Activating virtual environment..."
source "$SCRIPT_DIR/venv/bin/activate"
log "✅ Virtual environment activated"

# Verify Python in venv
log "Python: $(python3 --version)"
log "Executable: $(which python3)"

# Run fetch_lobbyx.py
log "---"
log "Step 1: Fetching job listings..."
if python3 "$SCRIPT_DIR/fetch_lobbyx.py" >> "$LOG_FILE" 2>&1; then
    log "✅ Fetch completed"
else
    log "⚠️  Fetch had issues (continuing...)"
fi

# Run parse_html_to_json.py
log "---"
log "Step 2: Parsing HTML to JSON..."
if python3 "$SCRIPT_DIR/parse_html_to_json.py" >> "$LOG_FILE" 2>&1; then
    log "✅ Parsing completed"
else
    log "⚠️  Parsing had issues (continuing...)"
fi

# Run download_job_pages.py
log "---"
log "Step 3: Downloading individual job pages..."
if python3 "$SCRIPT_DIR/download_job_pages.py" >> "$LOG_FILE" 2>&1; then
    log "✅ Job page downloads completed"
else
    log "⚠️  Job page downloads had issues (continuing...)"
fi

# Run generate_dashboard_api.py
log "---"
log "Step 4: Generating dashboard API..."
if python3 "$SCRIPT_DIR/generate_dashboard_api.py" >> "$LOG_FILE" 2>&1; then
    log "✅ Dashboard API generated"
else
    log "⚠️  API generation had issues (continuing...)"
fi

# Validate data structure
log "---"
log "Step 5: Validating data structure..."
if python3 "$SCRIPT_DIR/validate_data_structure.py" >> "$LOG_FILE" 2>&1; then
    log "✅ Data validation passed"
else
    log "⚠️  Data validation had issues"
fi

# Deactivate virtual environment
log "---"
deactivate
log "✅ Virtual environment deactivated"

END_TIME=$(date '+%Y-%m-%d %H:%M:%S')
log "=========================================="
log "🎉 Data Collection Completed"
log "Start: $START_TIME"
log "End:   $END_TIME"
log "=========================================="
