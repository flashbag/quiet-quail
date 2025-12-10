#!/bin/bash

# Server setup script for Quiet-Quail project
# This script sets up the environment on the server

set -e  # Exit on error

echo "==================================="
echo "Setting up Quiet-Quail environment"
echo "==================================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed."
    echo "Please install Python3 first:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi

echo "Python3 found: $(python3 --version)"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Install system dependencies for Playwright (may require sudo)
echo ""
echo "==================================="
echo "Installing Playwright system dependencies..."
echo "This may require sudo password:"
echo "==================================="
playwright install-deps chromium || {
    echo ""
    echo "Warning: Could not install system dependencies automatically."
    echo "You may need to run this manually with sudo:"
    echo "  sudo playwright install-deps chromium"
    echo ""
}

# Create saved_html directory
echo "Creating saved_html directory..."
mkdir -p saved_html

# Test the script
echo ""
echo "==================================="
echo "Testing the script..."
echo "==================================="
python3 fetch_lobbyx.py

if [ $? -eq 0 ]; then
    echo ""
    echo "==================================="
    echo "Setup completed successfully!"
    echo "==================================="
    echo ""
    echo "To set up cron job (run every 6 hours):"
    echo "1. Edit crontab: crontab -e"
    echo "2. Add this line:"
    echo "   0 */6 * * * cd $SCRIPT_DIR && $SCRIPT_DIR/venv/bin/python3 $SCRIPT_DIR/fetch_lobbyx.py >> $SCRIPT_DIR/cron.log 2>&1"
    echo ""
    echo "Or run the setup_cron.sh script:"
    echo "  ./setup_cron.sh"
    echo ""
else
    echo ""
    echo "==================================="
    echo "Error: Script test failed!"
    echo "Please check the error messages above."
    echo "==================================="
    exit 1
fi
