#!/bin/bash
# Quick test runner for dashboard
# Usage: ./test.sh

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$PROJECT_DIR/.venv"

echo "Starting dashboard server..."
$VENV/bin/python web/dashboard_server.py &
SERVER_PID=$!
sleep 2

echo ""
echo "Running browser tests..."
$VENV/bin/python tests/test_dashboard_browser.py
TEST_RESULT=$?

echo ""
echo "Stopping dashboard server..."
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true

exit $TEST_RESULT
