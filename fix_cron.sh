#!/bin/bash

# Fix cron job issues on VPS
# This script properly sets up and tests the cron job

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cron Job Setup and Fix${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Must run as root${NC}"
    exit 1
fi

# Get the absolute path of the project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Determine if running locally or on VPS
if [ "$SCRIPT_DIR" = "/var/www/quiet-quail" ]; then
    PROJECT_DIR="/var/www/quiet-quail"
    echo "Running on VPS"
else
    PROJECT_DIR="$SCRIPT_DIR"
    echo "Running locally at: $PROJECT_DIR"
fi

echo "Project directory: $PROJECT_DIR"
echo ""

# Verify Python and venv
if [ ! -f "$PROJECT_DIR/venv/bin/python3" ]; then
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo "Please run: ./setup_server.sh"
    exit 1
fi

PYTHON="$PROJECT_DIR/venv/bin/python3"
PYTHON_VERSION=$($PYTHON --version)
echo -e "${GREEN}✅ Python found: $PYTHON_VERSION${NC}"
echo ""

# Verify fetch_lobbyx.py exists and has correct syntax
if [ ! -f "$PROJECT_DIR/fetch_lobbyx.py" ]; then
    echo -e "${RED}❌ fetch_lobbyx.py not found${NC}"
    exit 1
fi

echo "Testing Python syntax..."
if $PYTHON -m py_compile "$PROJECT_DIR/fetch_lobbyx.py"; then
    echo -e "${GREEN}✅ Syntax check passed${NC}"
else
    echo -e "${RED}❌ Syntax error in fetch_lobbyx.py${NC}"
    exit 1
fi
echo ""

# Define the correct cron job
CRON_SCHEDULE="0 */6 * * *"
CRON_COMMAND="cd $PROJECT_DIR && $PYTHON $PROJECT_DIR/fetch_lobbyx.py >> $PROJECT_DIR/cron.log 2>&1"
CRON_JOB="$CRON_SCHEDULE $CRON_COMMAND"

echo "Cron job details:"
echo "Schedule: $CRON_SCHEDULE (every 6 hours)"
echo "Command: $CRON_COMMAND"
echo ""

# Get current crontab
CURRENT_CRON=$(crontab -l 2>/dev/null || echo "")

# Check if cron job already exists
if echo "$CURRENT_CRON" | grep -F "fetch_lobbyx.py" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Existing cron job found:${NC}"
    echo "$CURRENT_CRON" | grep -F "fetch_lobbyx.py"
    echo ""
    
    # Remove the old cron job
    echo "Removing old cron job..."
    NEW_CRON=$(echo "$CURRENT_CRON" | grep -v "fetch_lobbyx.py" || echo "")
    
    if [ -z "$NEW_CRON" ]; then
        # No other cron jobs, remove all
        crontab -r 2>/dev/null || true
    else
        # Keep other cron jobs
        echo "$NEW_CRON" | crontab -
    fi
    
    echo -e "${GREEN}✅ Old cron job removed${NC}"
fi

echo ""
echo "Installing new cron job..."

# Add new cron job
if [ -z "$CURRENT_CRON" ] || [ $(echo "$CURRENT_CRON" | wc -l) -eq 0 ]; then
    # Create new crontab
    echo "$CRON_JOB" | crontab -
else
    # Append to existing crontab
    if ! echo "$CURRENT_CRON" | grep -F "fetch_lobbyx.py" > /dev/null 2>&1; then
        # Remove old jobs if they exist, then add new
        NEW_CRON=$(echo "$CURRENT_CRON" | grep -v "fetch_lobbyx.py" || echo "")
        if [ -z "$NEW_CRON" ]; then
            echo "$CRON_JOB" | crontab -
        else
            (echo "$NEW_CRON"; echo "$CRON_JOB") | crontab -
        fi
    fi
fi

echo -e "${GREEN}✅ Cron job installed${NC}"
echo ""

# Verify installation
echo "Verifying cron job installation..."
if crontab -l 2>/dev/null | grep -F "fetch_lobbyx.py" > /dev/null; then
    echo -e "${GREEN}✅ Cron job verified:${NC}"
    crontab -l | grep -F "fetch_lobbyx.py"
else
    echo -e "${RED}❌ Failed to install cron job${NC}"
    exit 1
fi

echo ""
echo "Testing manual execution..."
echo "Command: $PYTHON $PROJECT_DIR/fetch_lobbyx.py"
echo ""

if cd "$PROJECT_DIR" && timeout 60 $PYTHON "$PROJECT_DIR/fetch_lobbyx.py"; then
    echo ""
    echo -e "${GREEN}✅ Script executed successfully${NC}"
else
    RESULT=$?
    if [ $RESULT -eq 124 ]; then
        echo -e "${YELLOW}⚠️  Script timed out (timeout after 60 seconds)${NC}"
    else
        echo -e "${RED}❌ Script failed with exit code $RESULT${NC}"
    fi
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Cron job setup complete${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Monitor log file: tail -f $PROJECT_DIR/cron.log"
echo "2. Verify cron is running: crontab -l"
echo "3. Check system cron logs: grep CRON /var/log/syslog"
