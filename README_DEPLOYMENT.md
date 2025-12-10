# Deployment Guide for Quiet-Quail

This guide explains how to deploy and set up the Quiet-Quail project on a server.

## Prerequisites

- A remote server with SSH access
- Python 3.7+ installed on the server
- Sufficient disk space for saved HTML files

## Deployment Steps

### 1. Deploy to Server

Run the deployment script from your local machine:

```bash
chmod +x deploy.sh
./deploy.sh user@your-server.com /path/on/server
```

Example:
```bash
./deploy.sh admin@example.com /home/admin/quiet-quail
```

The script will:
- Create the remote directory
- Copy project files (excluding saved_html, cache, etc.)
- Set proper permissions

### 2. Setup Environment on Server

SSH to your server:
```bash
ssh user@your-server.com
cd /path/on/server
```

Run the setup script:
```bash
chmod +x setup_server.sh
./setup_server.sh
```

The script will:
- Check Python installation
- Create a virtual environment
- Install Python dependencies
- Install Playwright and Chromium browser
- Install system dependencies
- Create necessary directories
- Run a test to verify everything works

**Note:** You may need sudo privileges for installing Playwright system dependencies.

### 3. Setup Cron Job

After successful setup, configure the cron job to run every 6 hours:

```bash
chmod +x setup_cron.sh
./setup_cron.sh
```

The script will:
- Add a cron job that runs at 00:00, 06:00, 12:00, and 18:00 daily
- Create a log file at `cron.log` for monitoring

#### Manual Cron Setup

If you prefer to set up cron manually:

```bash
crontab -e
```

Add this line:
```
0 */6 * * * cd /path/on/server && /path/on/server/venv/bin/python3 /path/on/server/fetch_lobbyx.py >> /path/on/server/cron.log 2>&1
```

Replace `/path/on/server` with your actual path.

## Monitoring

### View Cron Logs

```bash
tail -f /path/on/server/cron.log
```

### View Application Logs

```bash
tail -f /path/on/server/debug.log
```

### Check Cron Status

```bash
crontab -l
```

### Test Manual Run

```bash
cd /path/on/server
source venv/bin/activate
python3 fetch_lobbyx.py
```

## File Structure on Server

```
/path/on/server/
├── fetch_lobbyx.py       # Main script
├── requirements.txt      # Python dependencies
├── setup_server.sh       # Setup script
├── setup_cron.sh         # Cron setup script
├── venv/                 # Virtual environment
├── saved_html/           # Output directory
│   └── YYYY/MM/DD/       # Date-organized HTML files
├── debug.log             # Application log
└── cron.log              # Cron execution log
```

## Troubleshooting

### Playwright Installation Issues

If Playwright fails to install system dependencies:
```bash
sudo playwright install-deps chromium
```

### Permission Issues

Ensure the user has write permissions:
```bash
chmod -R u+w /path/on/server
```

### Cron Not Running

1. Check cron service status:
   ```bash
   sudo systemctl status cron  # Ubuntu/Debian
   sudo systemctl status crond # CentOS/RHEL
   ```

2. Verify cron job is installed:
   ```bash
   crontab -l
   ```

3. Check cron logs:
   ```bash
   tail -f /path/on/server/cron.log
   ```

### Browser Dependencies Missing

Install system dependencies manually:
```bash
# Ubuntu/Debian
sudo apt-get install -y \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libdbus-1-3 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libasound2

# CentOS/RHEL
sudo yum install -y \
    nss nspr atk at-spi2-atk cups-libs libdrm dbus-libs \
    libXcomposite libXdamage libXfixes libXrandr \
    mesa-libgbm alsa-lib
```

## Updating the Application

To update the application on the server:

1. Make changes locally
2. Run deployment again:
   ```bash
   ./deploy.sh user@your-server.com /path/on/server
   ```

The cron job will automatically use the updated code on the next run.

## Uninstalling

To remove the cron job:
```bash
crontab -e
# Delete the line containing fetch_lobbyx.py
```

To remove the application:
```bash
rm -rf /path/on/server
```
