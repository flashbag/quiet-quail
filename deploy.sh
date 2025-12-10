#!/bin/bash

# Deploy script for Quiet-Quail project
# Usage: ./deploy.sh user@hostname /path/on/server

set -e  # Exit on error

# Check arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 user@hostname /path/on/server"
    echo "Example: $0 user@example.com /home/user/quiet-quail"
    exit 1
fi

SERVER="$1"
REMOTE_PATH="$2"

echo "==================================="
echo "Deploying Quiet-Quail to server"
echo "Server: $SERVER"
echo "Path: $REMOTE_PATH"
echo "==================================="

# Create remote directory if it doesn't exist
echo "Creating remote directory..."
ssh "$SERVER" "mkdir -p $REMOTE_PATH"

# Copy project files to server
echo "Copying files to server..."

# Check if rsync is available on remote server
if ssh "$SERVER" "command -v rsync" &> /dev/null; then
    echo "Using rsync for file transfer..."
    rsync -avz --progress \
        --exclude 'saved_html/' \
        --exclude '__pycache__/' \
        --exclude '*.pyc' \
        --exclude '.git/' \
        --exclude 'debug.log' \
        --exclude '.venv/' \
        --exclude 'venv/' \
        fetch_lobbyx.py \
        parse_html_to_json.py \
        requirements.txt \
        setup_server.sh \
        setup_server_with_dns_fix.sh \
        setup_cron.sh \
        check_server_network.sh \
        fix_dns.sh \
        fix_dns_comprehensive.sh \
        "$SERVER:$REMOTE_PATH/"
else
    echo "rsync not found on server, using scp instead..."
    scp fetch_lobbyx.py \
        parse_html_to_json.py \
        requirements.txt \
        setup_server.sh \
        setup_server_with_dns_fix.sh \
        setup_cron.sh \
        check_server_network.sh \
        fix_dns.sh \
        fix_dns_comprehensive.sh \
        "$SERVER:$REMOTE_PATH/"
fi

# Make setup scripts executable on server
echo "Making setup scripts executable..."
ssh "$SERVER" "chmod +x $REMOTE_PATH/setup_server.sh $REMOTE_PATH/setup_server_with_dns_fix.sh $REMOTE_PATH/setup_cron.sh $REMOTE_PATH/check_server_network.sh $REMOTE_PATH/fix_dns.sh $REMOTE_PATH/fix_dns_comprehensive.sh"

echo ""
echo "==================================="
echo "Deployment completed successfully!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. SSH to your server: ssh $SERVER"
echo "2. Navigate to: cd $REMOTE_PATH"
echo "3. Run setup: ./setup_server.sh"
echo ""
