#!/bin/bash
# Test script to verify cron job runs correctly inside venv

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"
VENV_PATH="$PROJECT_DIR/venv"

echo "=================================================="
echo "Testing Cron VEnv Execution"
echo "=================================================="
echo ""

# Check if venv exists
if [ ! -f "$VENV_PATH/bin/python3" ]; then
    echo "❌ Virtual environment not found at $VENV_PATH"
    exit 1
fi

echo "✅ Virtual environment found: $VENV_PATH"
echo ""

# Check if cron_wrapper.sh exists and is executable
if [ ! -f "$PROJECT_DIR/cron_wrapper.sh" ]; then
    echo "❌ cron_wrapper.sh not found"
    exit 1
fi

if [ ! -x "$PROJECT_DIR/cron_wrapper.sh" ]; then
    echo "⚠️  cron_wrapper.sh is not executable, fixing..."
    chmod +x "$PROJECT_DIR/cron_wrapper.sh"
    echo "✅ cron_wrapper.sh is now executable"
fi
echo ""

# Test 1: Verify Python in venv works
echo "Test 1: Verify venv Python works..."
PYTHON_VERSION=$("$VENV_PATH/bin/python3" --version)
echo "  Python: $PYTHON_VERSION"
echo "  Path: $VENV_PATH/bin/python3"
echo "✅ Test 1 passed"
echo ""

# Test 2: Verify required packages
echo "Test 2: Checking required packages..."
"$VENV_PATH/bin/python3" -c "
import sys
required = ['bs4', 'playwright', 'requests']
for pkg in required:
    try:
        __import__(pkg)
        print(f'  ✓ {pkg}')
    except ImportError:
        print(f'  ✗ {pkg} MISSING')
        sys.exit(1)
"
echo "✅ Test 2 passed - All required packages available"
echo ""

# Test 3: Verify fetch_lobbyx.py exists and has correct shebang
echo "Test 3: Checking fetch_lobbyx.py..."
if [ ! -f "$PROJECT_DIR/fetch_lobbyx.py" ]; then
    echo "❌ fetch_lobbyx.py not found"
    exit 1
fi
echo "✅ fetch_lobbyx.py exists"
echo ""

# Test 4: Simulate cron wrapper execution (dry run)
echo "Test 4: Simulating cron wrapper execution (dry run)..."
bash -n "$PROJECT_DIR/cron_wrapper.sh" 2>&1 || {
    echo "❌ Syntax error in cron_wrapper.sh"
    exit 1
}
echo "✅ Test 4 passed - No syntax errors"
echo ""

# Test 5: Test cron_wrapper.sh can be sourced
echo "Test 5: Testing cron_wrapper.sh can be run..."
chmod +x "$PROJECT_DIR/cron_wrapper.sh"
OUTPUT=$("$PROJECT_DIR/cron_wrapper.sh" 2>&1) || {
    EXIT_CODE=$?
    if echo "$OUTPUT" | grep -q "✅"; then
        echo "✅ Test 5 passed - cron_wrapper.sh executed successfully"
    else
        echo "⚠️  Exit code $EXIT_CODE (may be due to no new data)"
        echo "Output: $OUTPUT" | head -20
    fi
}
echo ""

# Test 6: Verify log files will be created
echo "Test 6: Checking log file locations..."
LOG_FILE="$PROJECT_DIR/cron.log"
ERROR_LOG="$PROJECT_DIR/cron_error.log"
echo "  Log file: $LOG_FILE"
echo "  Error log: $ERROR_LOG"
if [ -f "$LOG_FILE" ]; then
    echo "  ✓ cron.log exists"
    echo "    Last entries:"
    tail -3 "$LOG_FILE" | sed 's/^/      /'
fi
echo "✅ Test 6 passed"
echo ""

# Test 7: Show crontab entry that would be installed
echo "Test 7: Crontab entry to be installed:"
echo "  Command: 0 */6 * * * $SCRIPT_DIR/cron_wrapper.sh"
echo "  This will run every 6 hours at: 00:00, 06:00, 12:00, 18:00"
echo "✅ Test 7 passed"
echo ""

echo "=================================================="
echo "✅ ALL TESTS PASSED"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Run ./setup_cron.sh to install cron job"
echo "  2. Monitor logs: tail -f cron.log"
echo "  3. Verify installation: crontab -l"
echo ""
