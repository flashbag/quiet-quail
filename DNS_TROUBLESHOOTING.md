# DNS Troubleshooting Guide for Server Setup

## Problem
Your server has DNS resolution issues ("Temporary failure in name resolution"), which prevents pip from downloading packages from PyPI.

## Quick Fix Steps

### Option 1: Automatic DNS Fix (Recommended)
```bash
ssh root@144.91.71.38
cd /var/www/quiet-quail
./setup_server_with_dns_fix.sh
```
This script will automatically attempt to fix DNS and proceed with installation.

### Option 2: Manual DNS Fix
```bash
ssh root@144.91.71.38
cd /var/www/quiet-quail

# Check the problem
./check_server_network.sh

# Fix DNS
./fix_dns.sh

# Then run normal setup
./setup_server.sh
```

### Option 3: Manual DNS Configuration
```bash
ssh root@144.91.71.38

# Backup current DNS config
cp /etc/resolv.conf /etc/resolv.conf.backup

# Set Google and Cloudflare DNS
cat > /etc/resolv.conf << EOF
nameserver 8.8.8.8
nameserver 8.8.4.4
nameserver 1.1.1.1
nameserver 1.0.0.1
EOF

# Test DNS
nslookup pypi.org

# If working, proceed with setup
cd /var/www/quiet-quail
./setup_server.sh
```

## What Each Script Does

### `check_server_network.sh`
- Diagnoses DNS and network issues
- Shows current DNS configuration
- Tests connectivity to PyPI

### `fix_dns.sh`
- Automatically fixes DNS configuration
- Sets up Google (8.8.8.8) and Cloudflare (1.1.1.1) DNS
- Tests if the fix worked

### `setup_server_with_dns_fix.sh`
- All-in-one script that fixes DNS automatically
- Then proceeds with full setup
- **Recommended for first-time setup**

### `setup_server.sh`
- Original setup script (use after DNS is fixed)

## Common Issues

### 1. Permission Denied
If you get permission denied when modifying `/etc/resolv.conf`:
```bash
sudo ./fix_dns.sh
# or
sudo ./setup_server_with_dns_fix.sh
```

### 2. DNS Changes Don't Persist
Some servers use `systemd-resolved` which overwrites `/etc/resolv.conf`:
```bash
# Check if systemd-resolved is running
systemctl status systemd-resolved

# If yes, configure it properly
sudo mkdir -p /etc/systemd/resolved.conf.d/
sudo cat > /etc/systemd/resolved.conf.d/dns.conf << EOF
[Resolve]
DNS=8.8.8.8 8.8.4.4 1.1.1.1
EOF

sudo systemctl restart systemd-resolved
```

### 3. Still Can't Resolve
Check if there's a firewall blocking DNS (port 53):
```bash
# Check firewall rules
iptables -L -n | grep 53

# Test direct connection
nc -v -u 8.8.8.8 53
```

Contact your hosting provider if DNS issues persist.

## After DNS is Fixed

Once setup completes successfully:
```bash
cd /var/www/quiet-quail
./setup_cron.sh
```

This will configure the script to run every 6 hours automatically.

## Verification

Check that everything is working:
```bash
# Manual test
cd /var/www/quiet-quail
source venv/bin/activate
python3 fetch_lobbyx.py

# Check cron is set up
crontab -l

# Monitor cron logs
tail -f /var/www/quiet-quail/cron.log
```
