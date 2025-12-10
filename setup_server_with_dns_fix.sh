#!/bin/bash

# Server setup script with automatic DNS fix
# This script attempts to fix DNS issues before installing packages

set +e  # Don't exit on error, we'll handle them

echo "==================================="
echo "Setting up Quiet-Quail environment"
echo "With automatic DNS troubleshooting"
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
echo ""

# Check DNS before proceeding
echo "Checking DNS configuration..."
if ! nslookup pypi.org > /dev/null 2>&1; then
    echo "⚠ DNS resolution is not working!"
    echo ""
    echo "Attempting to fix DNS configuration..."
    
    # Backup and fix DNS
    if [ -f /etc/resolv.conf ]; then
        cp /etc/resolv.conf /etc/resolv.conf.backup.$(date +%s) 2>/dev/null
    fi
    
    # Try to fix DNS
    cat > /tmp/resolv.conf.new << 'EOF'
nameserver 8.8.8.8
nameserver 8.8.4.4
nameserver 1.1.1.1
EOF
    
    if [ -w /etc/resolv.conf ]; then
        mv /tmp/resolv.conf.new /etc/resolv.conf
        echo "DNS configuration updated."
    else
        echo "Cannot write to /etc/resolv.conf (need root/sudo)"
        echo "Please run: sudo mv /tmp/resolv.conf.new /etc/resolv.conf"
        echo "Or run this script with sudo"
        exit 1
    fi
    
    # Test again
    sleep 2
    if ! nslookup pypi.org > /dev/null 2>&1; then
        echo ""
        echo "✗ DNS still not working after fix attempt."
        echo ""
        echo "Please check:"
        echo "1. Network connectivity: ping 8.8.8.8"
        echo "2. Firewall rules"
        echo "3. Contact your hosting provider"
        echo ""
        echo "For offline installation, use: ./setup_server_offline.sh"
        exit 1
    fi
    echo "✓ DNS is now working!"
else
    echo "✓ DNS is working"
fi

echo ""
echo "==================================="
echo "Proceeding with installation..."
echo "==================================="
echo ""

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
pip install --upgrade pip || {
    echo "Warning: Could not upgrade pip"
}

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "✗ Failed to install Python dependencies"
    echo "Please check the error messages above"
    exit 1
fi

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

if [ $? -ne 0 ]; then
    echo ""
    echo "✗ Failed to install Playwright browsers"
    exit 1
fi

# Install system dependencies for Playwright
echo ""
echo "Installing Playwright system dependencies..."
playwright install-deps chromium || {
    echo ""
    echo "Warning: Could not install system dependencies automatically."
    echo "Trying with sudo..."
    sudo playwright install-deps chromium || {
        echo "You may need to install manually"
    }
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
    echo "✓ Setup completed successfully!"
    echo "==================================="
    echo ""
    echo "Next step: Set up cron job"
    echo "Run: ./setup_cron.sh"
    echo ""
else
    echo ""
    echo "==================================="
    echo "✗ Script test failed!"
    echo "Please check the error messages above."
    echo "==================================="
    exit 1
fi
