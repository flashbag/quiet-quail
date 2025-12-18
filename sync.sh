#!/bin/bash

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$PROJECT_ROOT/venv"
SYNC_SCRIPT="$PROJECT_ROOT/tools/sync_service.py"
CONFIG_FILE="$PROJECT_ROOT/.sync_config.json"
LOG_FILE="${LOG_FILE:-/tmp/quiet-quail-sync.log}"

# Activate venv
if [ -f "$VENV/bin/activate" ]; then
    source "$VENV/bin/activate"
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_message() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}"
}

COMMAND="${1:-help}"

case "$COMMAND" in
    setup)
        log_message "INFO" "Starting sync configuration..."
        python "$SYNC_SCRIPT" --setup
        if [ $? -eq 0 ]; then
            log_message "INFO" "✅ Sync configured successfully"
        fi
        ;;
    
    sync)
        if [ ! -f "$CONFIG_FILE" ]; then
            echo -e "${RED}❌ Not configured${NC}"
            echo "Run: ./sync.sh setup"
            exit 1
        fi
        
        log_message "INFO" "Starting data sync..."
        python "$SYNC_SCRIPT" --sync
        
        if [ $? -eq 0 ]; then
            log_message "SUCCESS" "✅ Data sync completed"
            exit 0
        else
            log_message "ERROR" "❌ Data sync failed"
            exit 1
        fi
        ;;
    
    status)
        if [ ! -f "$CONFIG_FILE" ]; then
            echo "❌ Not configured"
            exit 1
        fi
        
        python "$SYNC_SCRIPT" --status
        ;;
    
    cron)
        # Cron-friendly sync (silent unless error)
        if [ ! -f "$CONFIG_FILE" ]; then
            echo "[ERROR] Sync not configured" >> "$LOG_FILE"
            exit 1
        fi
        
        {
            log_message "INFO" "Cron sync started"
            python "$SYNC_SCRIPT" --sync
            if [ $? -eq 0 ]; then
                log_message "SUCCESS" "Cron sync completed"
            else
                log_message "ERROR" "Cron sync failed"
                exit 1
            fi
        } >> "$LOG_FILE" 2>&1
        ;;
    
    *)
        cat << 'EOF'
Quiet-Quail Data Sync
=====================

Usage: ./sync.sh [command]

Commands:
  setup      Configure remote sync settings
  sync       Manually sync data now (includes consolidation)
  status     Show sync status
  cron       Cron-friendly sync (logs to file)
  help       Show this help

Setup (first time):
  $ ./sync.sh setup
  $ ./sync.sh sync

For cron jobs:
  $ 0 * * * * /path/to/sync.sh cron

Example cron entries:
  # Hourly
  0 * * * * /home/user/Quiet-Quail/sync.sh cron

  # Every 6 hours
  0 */6 * * * /home/user/Quiet-Quail/sync.sh cron

  # Daily at 2 AM
  0 2 * * * /home/user/Quiet-Quail/sync.sh cron

Features:
  - SCP-based secure file transfer with progress display
  - Automatic JSON consolidation after sync
  - Sync history tracking
  - Real-time verbose output

View sync log:
  $ tail -f /tmp/quiet-quail-sync.log

EOF
        ;;
esac
