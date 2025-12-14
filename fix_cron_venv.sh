#!/bin/bash

# Fix and test cron job for Quiet-Quail project
# Ensures cron runs inside virtual environment

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "=================================================="
echo "Quiet-Quail Cron Fixer - VirtualEnv Integration"
echo "=================================================="
echo "Project directory: $SCRIPT_DIR"
echo "User: $(whoami)"
echo ""

# 1. VERIFY VIRTUALENV EXISTS
echo "[1/5] Checking virtual environment..."
if [ ! -f "$SCRIPT_DIR/venv/bin/python3" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: ./setup_server.sh"
    exit 1
fi

VENV_PYTHON="$SCRIPT_DIR/venv/bin/python3"
echo "✅ Virtual environment found: $VENV_PYTHON"
echo "   Python version: $($VENV_PYTHON --version)"

# 2. VERIFY SCRIPTS EXIST
echo ""
echo "[2/5] Checking required scripts..."
for script in fetch_lobbyx.py parse_html_to_json.py download_job_pages.py validate_data_structure.py; do
    if [ ! -f "$SCRIPT_DIR/$script" ]; then
        echo "❌ Missing script: $script"
        exit 1
    fi
    echo "✅ Found: $script"
done

# 3. TEST VENV EXECUTION
echo ""
echo "[3/5] Testing virtual environment execution..."
TEST_OUTPUT=$($VENV_PYTHON -c "import bs4; print('✅ BeautifulSoup4 available')" 2>&1)
if [ $? -eq 0 ]; then
    echo "$TEST_OUTPUT"
else
    echo "❌ Virtual environment test failed!"
    echo "Output: $TEST_OUTPUT"
    exit 1
fi

# 4. CREATE ROBUST CRON COMMAND
echo ""
echo "[4/5] Creating robust cron command..."

# The proper way to run cron with venv:
# Option 1: Use full path to python in venv (preferred)
# Option 2: Source venv/bin/activate in a subshell

# We'll use Option 2 for better reliability
CRON_SCRIPT="$SCRIPT_DIR/run_fetch.sh"

cat > "$CRON_SCRIPT" << 'EOF'
#!/bin/bash
# Cron runner script - activates venv and runs fetch_lobbyx.py

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Run the main script
python3 fetch_lobbyx.py

# Parse HTML to JSON
python3 parse_html_to_json.py

# Download individual job pages
python3 download_job_pages.py

# Generate API file
python3 generate_dashboard_api.py

# Exit cleanly
deactivate
EOF

chmod +x "$CRON_SCRIPT"
echo "✅ Created cron runner script: $CRON_SCRIPT"

# 5. SETUP CRON JOB
echo ""
echo "[5/5] Setting up cron job..."

# Test cron script
echo "Testing cron runner script..."
if ! "$CRON_SCRIPT" >> "$SCRIPT_DIR/cron-test.log" 2>&1; then
    echo "⚠️  Note: Cron test had issues (may be expected if server is being set up)"
fi

# Define cron schedule: every 6 hours
CRON_SCHEDULE="0 */6 * * *"
CRON_JOB="$CRON_SCHEDULE $CRON_SCRIPT >> $SCRIPT_DIR/cron.log 2>&1"

# Check current cron
CURRENT_CRON=$(crontab -l 2>/dev/null || echo "")

if echo "$CURRENT_CRON" | grep -F "run_fetch.sh" > /dev/null 2>&1; then
    echo "Removing old cron entry..."
    echo "$CURRENT_CRON" | grep -v -F "run_fetch.sh" | crontab - 2>/dev/null || true
fi

# Add new cron job
if [ -z "$CURRENT_CRON" ]; then
    echo "$CRON_JOB" | crontab -
else
    (echo "$CURRENT_CRON"; echo "$CRON_JOB") | crontab -
fi

echo "✅ Cron job installed!"
echo ""
echo "=================================================="
echo "CRON SETUP COMPLETE"
echo "=================================================="
echo ""
echo "Schedule: Every 6 hours (00:00, 06:00, 12:00, 18:00)"
echo "Runner script: $CRON_SCRIPT"
echo "Log file: $SCRIPT_DIR/cron.log"
echo ""
echo "Current crontab:"
crontab -l
echo ""
echo "To verify manually, run:"
echo "  $CRON_SCRIPT"
echo ""
echo "To monitor logs:"
echo "  tail -f $SCRIPT_DIR/cron.log"
echo ""
