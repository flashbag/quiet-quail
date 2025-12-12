#!/bin/bash

# Setup cron job for Quiet-Quail project
# This script configures cron to run fetch_lobbyx.py every 6 hours

set +e  # Don't exit on error, handle manually

# Get the absolute path of the project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "==================================="
echo "Setting up cron job"
echo "Project directory: $SCRIPT_DIR"
echo "Current user: $(whoami)"
echo "==================================="
echo ""

# Check if venv exists
if [ ! -f "$SCRIPT_DIR/venv/bin/python3" ]; then
    echo "❌ Error: Virtual environment not found at $SCRIPT_DIR/venv"
    echo "Please run setup_server.sh first"
    exit 1
fi

# Define the cron job
CRON_JOB="0 */6 * * * cd $SCRIPT_DIR && $SCRIPT_DIR/venv/bin/python3 $SCRIPT_DIR/fetch_lobbyx.py >> $SCRIPT_DIR/cron.log 2>&1"

# Get current crontab
CURRENT_CRON=$(crontab -l 2>/dev/null)
CRON_RESULT=$?

if [ $CRON_RESULT -eq 0 ]; then
    echo "Current crontab:"
    echo "$CURRENT_CRON"
    echo ""
    
    # Check if cron job already exists
    if echo "$CURRENT_CRON" | grep -F "fetch_lobbyx.py" > /dev/null 2>&1; then
        echo "⚠️  A cron job for fetch_lobbyx.py already exists:"
        echo "$CURRENT_CRON" | grep -F "fetch_lobbyx.py"
        echo ""
        read -p "Do you want to replace it? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Aborted. No changes made."
            exit 0
        fi
        
        # Remove existing cron job
        echo "Removing existing cron job..."
        echo "$CURRENT_CRON" | grep -v -F "fetch_lobbyx.py" | crontab -
        if [ $? -ne 0 ]; then
            echo "❌ Failed to remove old cron job"
            exit 1
        fi
    fi
else
    echo "No existing crontab found (this is normal for first-time setup)"
fi

# Add new cron job
echo ""
echo "Adding new cron job..."
if [ -z "$CURRENT_CRON" ] || [ $CRON_RESULT -ne 0 ]; then
    # No existing crontab, create new one
    echo "$CRON_JOB" | crontab -
else
    # Append to existing crontab
    (echo "$CURRENT_CRON"; echo "$CRON_JOB") | crontab -
fi

if [ $? -eq 0 ]; then
    echo "✅ Cron job added successfully!"
    echo ""
    echo "==================================="
    echo "Cron job details:"
    echo "==================================="
    echo "Schedule: Every 6 hours (at 00:00, 06:00, 12:00, 18:00)"
    echo "Command: $CRON_JOB"
    echo ""
    echo "Verifying installation..."
    sleep 1
    
    VERIFY_CRON=$(crontab -l 2>/dev/null)
    if echo "$VERIFY_CRON" | grep -F "fetch_lobbyx.py" > /dev/null; then
        echo "✅ Verification successful! Cron job is installed."
        echo ""
        echo "Current crontab:"
        crontab -l
        echo ""
        echo "Monitor logs with: tail -f $SCRIPT_DIR/cron.log"
    else
        echo "❌ Verification failed! Cron job not found in crontab"
        exit 1
    fi
else
    echo "❌ Failed to add cron job"
    exit 1
fi
