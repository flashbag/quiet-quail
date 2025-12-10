#!/bin/bash

# Setup cron job for Quiet-Quail project
# This script configures cron to run fetch_lobbyx.py every 6 hours

set -e  # Exit on error

# Get the absolute path of the project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "==================================="
echo "Setting up cron job"
echo "Project directory: $SCRIPT_DIR"
echo "==================================="

# Define the cron job
CRON_JOB="0 */6 * * * cd $SCRIPT_DIR && $SCRIPT_DIR/venv/bin/python3 $SCRIPT_DIR/fetch_lobbyx.py >> $SCRIPT_DIR/cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -F "fetch_lobbyx.py" > /dev/null; then
    echo ""
    echo "A cron job for fetch_lobbyx.py already exists:"
    echo ""
    crontab -l | grep -F "fetch_lobbyx.py"
    echo ""
    read -p "Do you want to replace it? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted. No changes made."
        exit 0
    fi
    
    # Remove existing cron job
    echo "Removing existing cron job..."
    crontab -l | grep -v -F "fetch_lobbyx.py" | crontab -
fi

# Add new cron job
echo "Adding new cron job..."
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo ""
echo "==================================="
echo "Cron job added successfully!"
echo "==================================="
echo ""
echo "Schedule: Every 6 hours (at 00:00, 06:00, 12:00, 18:00)"
echo "Command: $CRON_JOB"
echo ""
echo "Current crontab:"
crontab -l
echo ""
echo "Log file: $SCRIPT_DIR/cron.log"
echo ""
echo "To view logs: tail -f $SCRIPT_DIR/cron.log"
echo "To edit crontab manually: crontab -e"
echo "To remove cron job: crontab -e (then delete the line)"
echo ""
