#!/bin/bash

# Run the Quiet-Quail dashboard server
# This script starts the HTTP server that serves the dashboard

set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "==================================="
echo "Starting Dashboard Server"
echo "==================================="
echo ""
echo "Project directory: $SCRIPT_DIR"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is required"
    exit 1
fi

# Get available port
PORT=${1:-8000}

# Check if dashboard server exists
if [ ! -f "dashboard_server.py" ]; then
    echo "Error: dashboard_server.py not found"
    exit 1
fi

echo "Starting server on port $PORT..."
echo "Dashboard available at: http://localhost:$PORT"
echo ""
echo "Press Ctrl+C to stop the server"
echo "==================================="
echo ""

# Start the dashboard server
python3 dashboard_server.py
