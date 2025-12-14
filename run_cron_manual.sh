#!/bin/bash
# Manual test script - runs the cron job manually for testing

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"

echo "Running cron job manually (simulating cron execution)..."
echo ""

bash "$PROJECT_DIR/cron_wrapper.sh"

EXIT_CODE=$?

echo ""
echo "Exit code: $EXIT_CODE"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Cron job executed successfully!"
else
    echo "❌ Cron job failed with exit code $EXIT_CODE"
    echo ""
    echo "Check logs for details:"
    echo "  tail -20 $PROJECT_DIR/cron.log"
    echo "  tail -20 $PROJECT_DIR/cron_error.log"
fi

exit $EXIT_CODE
