#!/bin/bash

# Script to fix DNS configuration on the server

echo "==================================="
echo "Fixing DNS Configuration"
echo "==================================="
echo ""

# Backup existing resolv.conf
if [ -f /etc/resolv.conf ]; then
    echo "Backing up /etc/resolv.conf..."
    cp /etc/resolv.conf /etc/resolv.conf.backup
    echo "Backup saved to /etc/resolv.conf.backup"
fi

# Add Google and Cloudflare DNS servers
echo "Setting up DNS servers..."
cat > /etc/resolv.conf << EOF
# DNS servers configured by fix_dns.sh
nameserver 8.8.8.8
nameserver 8.8.4.4
nameserver 1.1.1.1
nameserver 1.0.0.1
EOF

echo "New DNS configuration:"
cat /etc/resolv.conf

echo ""
echo "Testing DNS resolution..."
if nslookup pypi.org > /dev/null 2>&1; then
    echo "✓ DNS is working!"
    echo ""
    echo "You can now run: ./setup_server.sh"
else
    echo "✗ DNS still not working"
    echo ""
    echo "Additional troubleshooting:"
    echo "1. Check if systemd-resolved is managing DNS:"
    echo "   systemctl status systemd-resolved"
    echo ""
    echo "2. If using systemd-resolved, try:"
    echo "   rm /etc/resolv.conf"
    echo "   ln -s /run/systemd/resolve/resolv.conf /etc/resolv.conf"
    echo "   systemctl restart systemd-resolved"
    echo ""
    echo "3. Check firewall rules:"
    echo "   iptables -L -n | grep 53"
    echo ""
    echo "4. Contact your hosting provider for network support"
fi

echo ""
echo "==================================="
