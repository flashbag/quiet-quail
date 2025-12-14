#!/bin/bash
# Cron wrapper script that ensures commands run inside venv
# This script is called by cron and handles venv activation and error handling
# Works on both development and VPS environments

# Auto-detect project directory (works on dev and VPS)
if [ -d "/var/www/quiet-quail" ]; then
    PROJECT_DIR="/var/www/quiet-quail"
elif [ -d "$HOME/Projects/Quiet-Quail" ]; then
    PROJECT_DIR="$HOME/Projects/Quiet-Quail"
else
    # Try to find it from script location
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    PROJECT_DIR="$SCRIPT_DIR"
fi

VENV_PATH="$PROJECT_DIR/venv"
LOG_FILE="$PROJECT_DIR/cron.log"
ERROR_LOG="$PROJECT_DIR/cron_error.log"
PID_FILE="$PROJECT_DIR/.cron_running"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$ERROR_LOG"
}

# Prevent concurrent runs
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        log_error "Previous cron job still running (PID: $OLD_PID). Skipping this run."
        exit 1
    fi
fi
echo $$ > "$PID_FILE"
trap "rm -f $PID_FILE" EXIT

# Verify project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    log_error "Project directory not found: $PROJECT_DIR"
    exit 1
fi

# Verify venv exists
if [ ! -f "$VENV_PATH/bin/python3" ]; then
    log_error "Virtual environment not found: $VENV_PATH"
    exit 1
fi

# Change to project directory
cd "$PROJECT_DIR" || {
    log_error "Failed to change to project directory: $PROJECT_DIR"
    exit 1
}

log_message "=== Cron job started ==="
log_message "Python: $VENV_PATH/bin/python3"
log_message "Project: $PROJECT_DIR"

# Run the script with full venv path
if "$VENV_PATH/bin/python3" "$PROJECT_DIR/fetch_lobbyx.py" >> "$LOG_FILE" 2>&1; then
    log_message "✅ Script completed successfully"
    exit 0
else
    EXIT_CODE=$?
    log_error "Script failed with exit code $EXIT_CODE"
    exit $EXIT_CODE
fi
