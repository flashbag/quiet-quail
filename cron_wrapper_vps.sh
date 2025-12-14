#!/bin/bash
# VPS deployment version of cron wrapper
# Deploy this to /var/www/quiet-quail/cron_wrapper.sh on the VPS

PROJECT_DIR="/var/www/quiet-quail"
VENV_PATH="$PROJECT_DIR/venv"
PYTHON="$VENV_PATH/bin/python3"
SCRIPT="$PROJECT_DIR/fetch_lobbyx.py"
LOG_FILE="$PROJECT_DIR/cron.log"
ERROR_LOG="$PROJECT_DIR/cron_error.log"

# Ensure directories exist
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$(dirname "$ERROR_LOG")"

# Function to append timestamped log
log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log_err() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$ERROR_LOG"
}

# Verify critical paths
if [ ! -d "$PROJECT_DIR" ]; then
    echo "ERROR: Project directory not found: $PROJECT_DIR" >> "$ERROR_LOG"
    exit 1
fi

if [ ! -f "$PYTHON" ]; then
    log_err "Python executable not found: $PYTHON"
    exit 1
fi

if [ ! -f "$SCRIPT" ]; then
    log_err "Script not found: $SCRIPT"
    exit 1
fi

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Execute script with full paths
log_msg "START: fetch_lobbyx.py"
"$PYTHON" "$SCRIPT" 2>&1 | tee -a "$LOG_FILE"
EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -eq 0 ]; then
    log_msg "SUCCESS: Script completed"
else
    log_err "FAILED: Exit code $EXIT_CODE"
fi

exit $EXIT_CODE
