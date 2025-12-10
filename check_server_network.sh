#!/bin/bash

# Network diagnostic script for the server

echo "==================================="
echo "Server Network Diagnostics"
echo "==================================="
echo ""

# Check DNS resolution
echo "1. Checking DNS resolution..."
echo "   Testing pypi.org:"
if nslookup pypi.org > /dev/null 2>&1; then
    echo "   ✓ DNS working with nslookup"
elif host pypi.org > /dev/null 2>&1; then
    echo "   ✓ DNS working with host"
elif dig pypi.org > /dev/null 2>&1; then
    echo "   ✓ DNS working with dig"
else
    echo "   ✗ DNS resolution FAILED"
    echo ""
    echo "   Checking /etc/resolv.conf:"
    if [ -f /etc/resolv.conf ]; then
        cat /etc/resolv.conf
    else
        echo "   /etc/resolv.conf not found"
    fi
fi

echo ""
echo "2. Checking internet connectivity..."
if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
    echo "   ✓ Can reach 8.8.8.8 (Google DNS)"
else
    echo "   ✗ Cannot reach 8.8.8.8"
fi

if ping -c 1 1.1.1.1 > /dev/null 2>&1; then
    echo "   ✓ Can reach 1.1.1.1 (Cloudflare DNS)"
else
    echo "   ✗ Cannot reach 1.1.1.1"
fi

echo ""
echo "3. Checking HTTPS connectivity..."
if curl -Is https://pypi.org > /dev/null 2>&1; then
    echo "   ✓ Can connect to pypi.org via HTTPS"
elif wget --spider https://pypi.org > /dev/null 2>&1; then
    echo "   ✓ Can connect to pypi.org via HTTPS (wget)"
else
    echo "   ✗ Cannot connect to pypi.org"
fi

echo ""
echo "4. Current DNS servers:"
if [ -f /etc/resolv.conf ]; then
    grep nameserver /etc/resolv.conf
fi

echo ""
echo "==================================="
echo "Diagnostic complete"
echo "==================================="
echo ""
echo "If DNS is not working, you can try:"
echo "1. Fix DNS configuration:"
echo "   echo 'nameserver 8.8.8.8' | sudo tee /etc/resolv.conf"
echo "   echo 'nameserver 1.1.1.1' | sudo tee -a /etc/resolv.conf"
echo ""
echo "2. Or use offline installation (see setup_server_offline.sh)"
echo ""
