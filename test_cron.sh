#!/bin/bash
# Test script to verify cron setup is working correctly

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"
VENV_PATH="$PROJECT_DIR/venv"

echo "════════════════════════════════════════════════════════════════"
echo "Testing Cron Setup"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check venv
echo "1. Checking virtual environment..."
if [ -f "$VENV_PATH/bin/python3" ]; then
    echo "   ✅ venv found at $VENV_PATH"
    PYTHON="$VENV_PATH/bin/python3"
    echo "   Python version: $($PYTHON --version)"
else
    echo "   ❌ venv not found at $VENV_PATH"
    exit 1
fi
echo ""

# Check wrapper script
echo "2. Checking cron wrapper script..."
if [ -f "$PROJECT_DIR/cron_wrapper.sh" ]; then
    echo "   ✅ cron_wrapper.sh found"
    if [ -x "$PROJECT_DIR/cron_wrapper.sh" ]; then
        echo "   ✅ cron_wrapper.sh is executable"
    else
        echo "   ⚠️  cron_wrapper.sh is not executable, fixing..."
        chmod +x "$PROJECT_DIR/cron_wrapper.sh"
        echo "   ✅ Made executable"
    fi
else
    echo "   ❌ cron_wrapper.sh not found"
    exit 1
fi
echo ""

# Check fetch_lobbyx.py
echo "3. Checking fetch_lobbyx.py..."
if [ -f "$PROJECT_DIR/fetch_lobbyx.py" ]; then
    echo "   ✅ fetch_lobbyx.py found"
else
    echo "   ❌ fetch_lobbyx.py not found"
    exit 1
fi
echo ""

# Check requirements
echo "4. Checking required dependencies..."
REQUIRED_PACKAGES=("playwright" "beautifulsoup4" "requests")
for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if $PYTHON -c "import ${pkg}" 2>/dev/null; then
        echo "   ✅ $pkg installed"
    else
        echo "   ❌ $pkg not installed"
    fi
done
echo ""

# Test Python import
echo "5. Testing Python environment inside venv..."
if $PYTHON -c "import sys; print('   ✅ Python path:', sys.executable)" 2>/dev/null; then
    :
else
    echo "   ❌ Failed to test Python"
    exit 1
fi
echo ""

# Test wrapper execution (dry run)
echo "6. Testing cron wrapper execution (syntax check)..."
if bash -n "$PROJECT_DIR/cron_wrapper.sh" 2>/dev/null; then
    echo "   ✅ Wrapper script syntax is valid"
else
    echo "   ❌ Wrapper script has syntax errors"
    exit 1
fi
echo ""

# Check crontab
echo "7. Checking crontab..."
if crontab -l 2>/dev/null | grep -q "fetch_lobbyx.py"; then
    echo "   ✅ Cron job is installed"
    echo ""
    echo "   Current cron job:"
    crontab -l | grep "fetch_lobbyx.py" | sed 's/^/   /'
else
    echo "   ⚠️  No cron job found in crontab"
    echo "   Run setup_cron.sh to install it"
fi
echo ""

# Show log files status
echo "8. Checking log files..."
if [ -f "$PROJECT_DIR/cron.log" ]; then
    LINES=$(wc -l < "$PROJECT_DIR/cron.log")
    echo "   ✅ cron.log exists ($LINES lines)"
    echo "   Last 5 entries:"
    tail -5 "$PROJECT_DIR/cron.log" | sed 's/^/      /'
else
    echo "   ℹ️  cron.log doesn't exist yet (will be created on first run)"
fi
echo ""

if [ -f "$PROJECT_DIR/cron_error.log" ]; then
    LINES=$(wc -l < "$PROJECT_DIR/cron_error.log")
    echo "   ✅ cron_error.log exists ($LINES lines)"
    if [ "$LINES" -gt 0 ]; then
        echo "   Last 3 errors:"
        tail -3 "$PROJECT_DIR/cron_error.log" | sed 's/^/      /'
    fi
else
    echo "   ℹ️  cron_error.log doesn't exist yet (no errors)"
fi
echo ""

# Summary
echo "════════════════════════════════════════════════════════════════"
echo "✅ All cron setup checks completed!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "To manually test the cron command, run:"
echo "  $PROJECT_DIR/cron_wrapper.sh"
echo ""
echo "To monitor logs in real-time:"
echo "  tail -f $PROJECT_DIR/cron.log"
echo ""
