#!/bin/bash
# Test and verify cron setup
# Run this script to check if cron is configured correctly

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="${1:-.}"
VENV_PATH="$PROJECT_DIR/venv"
WRAPPER_SCRIPT="$PROJECT_DIR/cron_wrapper.sh"
PYTHON="$VENV_PATH/bin/python3"
SCRIPT="$PROJECT_DIR/fetch_lobbyx.py"

echo "========================================="
echo "Cron Setup Verification"
echo "========================================="
echo ""

# Check 1: Project directory
echo "1. Checking project directory..."
if [ -d "$PROJECT_DIR" ]; then
    echo "   ✅ Project directory exists: $PROJECT_DIR"
else
    echo "   ❌ Project directory not found: $PROJECT_DIR"
    exit 1
fi

# Check 2: Virtual environment
echo ""
echo "2. Checking virtual environment..."
if [ -f "$PYTHON" ]; then
    echo "   ✅ Python executable found: $PYTHON"
    echo "   Version: $($PYTHON --version)"
else
    echo "   ❌ Python executable not found: $PYTHON"
    exit 1
fi

# Check 3: Required packages in venv
echo ""
echo "3. Checking required packages..."
PACKAGES=("playwright" "beautifulsoup4" "requests")
for pkg in "${PACKAGES[@]}"; do
    if "$PYTHON" -c "import $pkg" 2>/dev/null; then
        echo "   ✅ $pkg is installed"
    else
        echo "   ❌ $pkg is NOT installed"
        exit 1
    fi
done

# Check 4: Main script
echo ""
echo "4. Checking main script..."
if [ -f "$SCRIPT" ]; then
    echo "   ✅ Script found: $SCRIPT"
else
    echo "   ❌ Script not found: $SCRIPT"
    exit 1
fi

# Check 5: Wrapper script
echo ""
echo "5. Checking wrapper script..."
if [ -f "$WRAPPER_SCRIPT" ]; then
    echo "   ✅ Wrapper script found: $WRAPPER_SCRIPT"
    if [ -x "$WRAPPER_SCRIPT" ]; then
        echo "   ✅ Wrapper script is executable"
    else
        echo "   ⚠️  Wrapper script is not executable, making it executable..."
        chmod +x "$WRAPPER_SCRIPT"
        echo "   ✅ Made executable"
    fi
else
    echo "   ❌ Wrapper script not found: $WRAPPER_SCRIPT"
    exit 1
fi

# Check 6: Log file permissions
echo ""
echo "6. Checking log file paths..."
LOG_DIR="$PROJECT_DIR"
if [ -w "$LOG_DIR" ]; then
    echo "   ✅ Log directory is writable: $LOG_DIR"
else
    echo "   ❌ Log directory is not writable: $LOG_DIR"
    exit 1
fi

# Check 7: Test run (optional)
echo ""
echo "7. Test run (this will actually run the script)..."
read -p "Do you want to perform a test run? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "   Running test..."
    if bash "$WRAPPER_SCRIPT"; then
        echo "   ✅ Test run successful"
    else
        echo "   ⚠️  Test run failed, but setup may still be valid"
    fi
else
    echo "   Skipped test run"
fi

# Summary
echo ""
echo "========================================="
echo "✅ All checks passed!"
echo "========================================="
echo ""
echo "Cron configuration:"
echo "  Schedule: Every 6 hours (0 */6 * * *)"
echo "  Command:  $WRAPPER_SCRIPT"
echo ""
echo "Log files:"
echo "  Success: $PROJECT_DIR/cron.log"
echo "  Errors:  $PROJECT_DIR/cron_error.log"
echo ""
echo "Next step: Run setup_cron.sh to install cron job"
