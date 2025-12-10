#!/bin/bash

# Comprehensive DNS fix for VPN-enabled servers
# Handles NordVPN and other VPN DNS issues

echo "==================================="
echo "Comprehensive DNS Fix"
echo "==================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root or with sudo"
    exit 1
fi

# Detect VPN
VPN_DETECTED=""
if command -v nordvpn &> /dev/null; then
    VPN_DETECTED="nordvpn"
    echo "✓ NordVPN detected"
fi

# Check current DNS
echo ""
echo "Current DNS configuration:"
if [ -f /etc/resolv.conf ]; then
    cat /etc/resolv.conf
else
    echo "/etc/resolv.conf not found!"
fi

echo ""
echo "==================================="
echo "Applying DNS fixes..."
echo "==================================="

# Backup current configuration
BACKUP_FILE="/etc/resolv.conf.backup.$(date +%s)"
if [ -f /etc/resolv.conf ]; then
    cp /etc/resolv.conf "$BACKUP_FILE"
    echo "✓ Backed up to $BACKUP_FILE"
fi

# Method 1: Direct resolv.conf (works for most cases)
echo ""
echo "Method 1: Setting DNS in /etc/resolv.conf..."

# Remove immutable flag if set
chattr -i /etc/resolv.conf 2>/dev/null

cat > /etc/resolv.conf << 'EOF'
# DNS configuration for Quiet-Quail
nameserver 8.8.8.8
nameserver 8.8.4.4
nameserver 1.1.1.1
nameserver 1.0.0.1
options timeout:2 attempts:3
EOF

echo "✓ DNS servers set to:"
cat /etc/resolv.conf

# Method 2: Handle systemd-resolved
echo ""
echo "Method 2: Checking systemd-resolved..."
if systemctl is-active --quiet systemd-resolved 2>/dev/null; then
    echo "✓ systemd-resolved is active, configuring..."
    
    mkdir -p /etc/systemd/resolved.conf.d/
    cat > /etc/systemd/resolved.conf.d/dns_servers.conf << 'EOF'
[Resolve]
DNS=8.8.8.8 8.8.4.4 1.1.1.1 1.0.0.1
FallbackDNS=208.67.222.222 208.67.220.220
Domains=~.
DNSSEC=no
DNSOverTLS=no
EOF
    
    systemctl restart systemd-resolved
    echo "✓ systemd-resolved restarted"
    
    # Update symlink if needed
    if [ -L /etc/resolv.conf ]; then
        rm /etc/resolv.conf
        ln -sf /run/systemd/resolve/resolv.conf /etc/resolv.conf
        echo "✓ Updated resolv.conf symlink"
    fi
else
    echo "✓ systemd-resolved not running"
fi

# Method 3: NordVPN specific fix
if [ "$VPN_DETECTED" = "nordvpn" ]; then
    echo ""
    echo "Method 3: Configuring NordVPN DNS..."
    
    # Set NordVPN to use custom DNS
    nordvpn set dns 8.8.8.8 8.8.4.4 2>/dev/null || true
    
    # Disable VPN DNS if connected
    NORDVPN_STATUS=$(nordvpn status | grep "Status:" | awk '{print $2}')
    if [ "$NORDVPN_STATUS" = "Connected" ]; then
        echo "⚠ NordVPN is connected. DNS may be overridden by VPN."
        echo "  Disconnecting VPN temporarily..."
        nordvpn disconnect
        sleep 2
    fi
    
    echo "✓ NordVPN DNS configured"
    echo ""
    echo "Note: If you reconnect to NordVPN, run:"
    echo "  nordvpn set dns 8.8.8.8 8.8.4.4"
fi

# Method 4: NetworkManager (if present)
echo ""
echo "Method 4: Checking NetworkManager..."
if systemctl is-active --quiet NetworkManager 2>/dev/null; then
    echo "✓ NetworkManager detected, configuring..."
    
    # Create NetworkManager DNS configuration
    mkdir -p /etc/NetworkManager/conf.d/
    cat > /etc/NetworkManager/conf.d/dns.conf << 'EOF'
[main]
dns=default
rc-manager=unmanaged
EOF
    
    systemctl restart NetworkManager
    echo "✓ NetworkManager restarted"
else
    echo "✓ NetworkManager not running"
fi

# Prevent resolv.conf from being overwritten
echo ""
echo "Method 5: Protecting resolv.conf..."
chattr +i /etc/resolv.conf 2>/dev/null && echo "✓ Made resolv.conf immutable" || echo "⚠ Could not set immutable flag"

# Test DNS resolution
echo ""
echo "==================================="
echo "Testing DNS resolution..."
echo "==================================="

TESTS=("google.com" "pypi.org" "github.com")
SUCCESS=0

for domain in "${TESTS[@]}"; do
    echo -n "Testing $domain... "
    if nslookup "$domain" > /dev/null 2>&1; then
        echo "✓ OK"
        ((SUCCESS++))
    elif host "$domain" > /dev/null 2>&1; then
        echo "✓ OK (with host)"
        ((SUCCESS++))
    elif ping -c 1 "$domain" > /dev/null 2>&1; then
        echo "✓ OK (with ping)"
        ((SUCCESS++))
    else
        echo "✗ FAILED"
    fi
done

echo ""
if [ $SUCCESS -gt 0 ]; then
    echo "==================================="
    echo "✓ DNS is working! ($SUCCESS/$((${#TESTS[@]})) tests passed)"
    echo "==================================="
    echo ""
    echo "You can now run the setup:"
    echo "  cd /var/www/quiet-quail"
    echo "  ./setup_server.sh"
    echo ""
    if [ "$VPN_DETECTED" = "nordvpn" ]; then
        echo "VPN Note:"
        echo "  To keep DNS working with NordVPN:"
        echo "  nordvpn set dns 8.8.8.8 8.8.4.4"
        echo ""
    fi
else
    echo "==================================="
    echo "✗ DNS still not working"
    echo "==================================="
    echo ""
    echo "Additional steps to try:"
    echo ""
    echo "1. Check network connectivity:"
    echo "   ping 8.8.8.8"
    echo ""
    echo "2. Check if DNS port is blocked:"
    echo "   nc -v -u 8.8.8.8 53"
    echo ""
    echo "3. Try alternative DNS providers:"
    echo "   echo 'nameserver 208.67.222.222' > /etc/resolv.conf"
    echo ""
    echo "4. Restart networking:"
    echo "   systemctl restart networking"
    echo ""
    echo "5. Contact your hosting provider"
    echo ""
fi

# Show final configuration
echo "Final /etc/resolv.conf:"
cat /etc/resolv.conf
echo ""
