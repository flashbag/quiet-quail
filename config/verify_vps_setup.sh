#!/bin/bash

# Verify VPS setup and paths
# Run this on the VPS to check everything is configured correctly

set -e

echo "=========================================="
echo "VPS Setup Verification"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Must run as root"
    exit 1
fi

# Define paths
VPS_PATH="/var/www/quiet-quail"

echo "🔍 Checking paths..."
echo "Expected path: $VPS_PATH"
echo ""

# Check if project directory exists
if [ -d "$VPS_PATH" ]; then
    echo "✅ Project directory exists"
else
    echo "❌ Project directory NOT found at $VPS_PATH"
    echo "Please run: ./deploy.sh root@<vps-ip> $VPS_PATH"
    exit 1
fi

# Check venv
echo ""
echo "🔍 Checking virtual environment..."
if [ -f "$VPS_PATH/venv/bin/python3" ]; then
    PYTHON_VERSION=$("$VPS_PATH/venv/bin/python3" --version)
    echo "✅ Virtual environment found: $PYTHON_VERSION"
else
    echo "❌ Virtual environment NOT found"
    echo "Please run: ssh root@<vps-ip> 'cd $VPS_PATH && ./setup_server.sh'"
    exit 1
fi

# Check dependencies
echo ""
echo "🔍 Checking Python dependencies..."
DEPS=("playwright" "beautifulsoup4" "requests")
for dep in "${DEPS[@]}"; do
    if "$VPS_PATH/venv/bin/python3" -c "import $dep" 2>/dev/null; then
        echo "✅ $dep installed"
    else
        echo "❌ $dep NOT installed"
    fi
done

# Check main scripts
echo ""
echo "🔍 Checking scripts..."
SCRIPTS=("fetch_lobbyx.py" "parse_html_to_json.py" "download_job_pages.py" "generate_dashboard_api.py")
for script in "${SCRIPTS[@]}"; do
    if [ -f "$VPS_PATH/$script" ]; then
        echo "✅ $script found"
    else
        echo "❌ $script NOT found"
    fi
done

# Test Python syntax on main script
echo ""
echo "🔍 Testing Python syntax..."
if "$VPS_PATH/venv/bin/python3" -m py_compile "$VPS_PATH/fetch_lobbyx.py" 2>/dev/null; then
    echo "✅ fetch_lobbyx.py syntax OK"
else
    echo "❌ fetch_lobbyx.py has syntax errors"
fi

# Check data directory
echo ""
echo "🔍 Checking data directory..."
if [ -d "$VPS_PATH/data" ]; then
    FILE_COUNT=$(find "$VPS_PATH/data" -type f | wc -l)
    echo "✅ Data directory exists with $FILE_COUNT files"
else
    echo "⚠️  Data directory does not exist (will be created on first run)"
fi

# Test cron command manually
echo ""
echo "🔍 Testing manual cron command..."
TEST_CMD="cd $VPS_PATH && $VPS_PATH/venv/bin/python3 $VPS_PATH/fetch_lobbyx.py"
if eval "$TEST_CMD" 2>&1 | tail -5; then
    echo "✅ Manual test completed"
else
    echo "❌ Manual test failed"
fi

# Check current crontab
echo ""
echo "🔍 Checking crontab..."
if crontab -l 2>/dev/null | grep -F "fetch_lobbyx.py" > /dev/null; then
    echo "✅ Cron job found:"
    crontab -l | grep -F "fetch_lobbyx.py"
else
    echo "⚠️  Cron job NOT configured"
    echo "Run: $VPS_PATH/setup_cron.sh"
fi

# Check logs
echo ""
echo "🔍 Checking logs..."
if [ -f "$VPS_PATH/cron.log" ]; then
    LINES=$(wc -l < "$VPS_PATH/cron.log")
    echo "✅ Cron log exists ($LINES lines)"
    echo "Last 5 lines:"
    tail -5 "$VPS_PATH/cron.log"
else
    echo "ℹ️  Cron log not yet created"
fi

echo ""
echo "=========================================="
echo "✅ Verification complete"
echo "=========================================="
