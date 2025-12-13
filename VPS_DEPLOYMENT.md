# VPS Deployment Instructions

## Quick Deployment Steps

### 1. Deploy to VPS
```bash
cd /Users/user/Projects/Quiet-Quail
./deploy.sh user@your-vps.com /var/www/quiet-quail
```

Replace `user@your-vps.com` with your actual VPS connection string and `/var/www/quiet-quail` with the desired path.

### 2. Connect to VPS and Complete Setup
```bash
ssh user@your-vps.com
cd /var/www/quiet-quail
chmod +x setup_server.sh setup_cron.sh
./setup_server.sh
```

### 3. Run Migration on Server (if needed)
```bash
cd /var/www/quiet-quail
source venv/bin/activate
python3 migrate_to_data_folder.py
python3 validate_data_structure.py
```

### 4. Setup Cron Job
```bash
cd /var/www/quiet-quail
./setup_cron.sh
```

Or manually:
```bash
crontab -e
# Add this line:
0 */6 * * * cd /var/www/quiet-quail && /var/www/quiet-quail/venv/bin/python3 /var/www/quiet-quail/fetch_lobbyx.py >> /var/www/quiet-quail/cron.log 2>&1
```

## What Changed

### Files Deployed
- `fetch_lobbyx.py` - Main scraper (updated to use data/)
- `parse_html_to_json.py` - Parser (updated to use data/)
- `download_job_pages.py` - Job page downloader (NEW)
- `validate_data_structure.py` - Data validator (NEW)
- `migrate_to_data_folder.py` - Migration utility (NEW)
- `requirements.txt` - Dependencies (includes `requests` for job downloads)
- Setup scripts and configuration files

### Why the VPS Error Occurred
The error `ModuleNotFoundError: No module named 'bs4'` happened because:
1. The venv wasn't properly created/activated
2. Requirements weren't installed in the virtual environment

### How It's Fixed
- Updated `setup_server.sh` to:
  1. Create virtual environment properly
  2. Upgrade pip
  3. Install all requirements (including `beautifulsoup4` and `requests`)
  4. Install Playwright browsers
  5. Create data directory
  6. Run migration script if needed
  7. Validate data structure
  8. Better error messages

### Directory Structure on Server
```
/var/www/quiet-quail/
├── data/                          # Consolidated data directory
│   ├── 2025/
│   │   ├── 10/
│   │   │   └── 21/
│   │   │       ├── output_20251021_112750.html
│   │   │       └── output_20251021_112750.json
│   │   ├── 11/
│   │   └── 12/
│   ├── consolidated_unique.json   # All unique jobs
│   └── .gitkeep
├── fetch_lobbyx.py
├── parse_html_to_json.py
├── download_job_pages.py
├── generate_dashboard_api.py
├── dashboard_server.py
├── dashboard.html
├── requirements.txt
├── validate_data_structure.py
├── migrate_to_data_folder.py
├── setup_server.sh
├── setup_cron.sh
├── venv/                          # Virtual environment
├── cron.log                        # Cron execution log
└── debug.log                       # Application debug log
```

## Verification Commands

### Check data integrity
```bash
source venv/bin/activate
python3 validate_data_structure.py
```

### View cron logs
```bash
tail -f cron.log
tail -f debug.log
```

### Manual test
```bash
source venv/bin/activate
python3 fetch_lobbyx.py
```

## Troubleshooting

### If you get "bs4 not found"
```bash
source venv/bin/activate
pip install beautifulsoup4 requests playwright
```

### If Playwright fails
```bash
source venv/bin/activate
playwright install chromium
playwright install-deps chromium  # May need sudo
```

### Check virtual environment
```bash
source venv/bin/activate
which python3  # Should show path to venv/bin/python3
pip list  # Should show all installed packages
```

### View recent cron errors
```bash
grep -i error cron.log | tail -20
```

## Dashboard Access

After setup, the dashboard will be available through:
- `dashboard_server.py` - Python server (if running on port 5000)
- Static `dashboard.html` - Static HTML file

Check `dashboard_server.py` for the port configuration.
