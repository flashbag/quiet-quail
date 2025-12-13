# Quick Start & Troubleshooting Guide

## 🚀 Running Locally

### Start Dashboard Server
```bash
cd /Users/user/Projects/Quiet-Quail
python3 dashboard_server.py
# Open: http://localhost:8000
```

### Validate Data Structure
```bash
python3 validate_data_structure.py
# Should show: ✅ DATA STRUCTURE IS VALID
# With stats: 22 JSON files, 7968 records, 471 unique jobs
```

### Regenerate Dashboard API
```bash
python3 generate_dashboard_api.py
# Should show: ✓ Generated file list with 22 files
```

## 📊 Data Directory Structure

```
data/
├── 2025/
│   ├── 10/
│   │   ├── 21/
│   │   │   ├── output_20251021_112750.html    # Scraped page
│   │   │   └── output_20251021_112750.json    # Parsed jobs
│   │   ├── 23/
│   │   ├── 26/
│   │   └── 27/
│   ├── 11/
│   │   ├── 09/, 15/, 18/, 19/, 24/, 28/, 29/
│   └── 12/
│       ├── 01/, 02/, 03/, 04/, 05/, 06/, 07/, 09/, 10/
└── consolidated_unique.json                    # All unique jobs (471)
```

## ✅ All Recent Fixes

### 1. **Directory Consolidation** ✓
- Merged `saved_html/`, `saved_json/`, `job_pages/` into `data/`
- Backups: `saved_html_backup/`, `saved_json_backup/`

### 2. **Data Validation** ✓
- Created `validate_data_structure.py`
- Validates: filenames, JSON structure, file pairs
- Reports: statistics, date range, unique jobs

### 3. **Job Page Downloading** ✓
- Created `download_job_pages.py`
- Tracks downloaded URLs to prevent duplicates
- Downloads new job pages only on first appearance
- Saves to: `data/YYYY/MM/DD/job_{post_id}.html`

### 4. **Dashboard Data Loading** ✓
- Fixed: `generate_dashboard_api.py` → now uses `data/`
- Fixed: `dashboard_server.py` → now serves from `/data/`
- Regenerated: `api/list-json-files.json` with 22 files
- API endpoint: `/api/files` → returns all JSON files

### 5. **VPS Deployment** ✓
- Updated: `deploy.sh` → excludes data/ directory
- Improved: `setup_server.sh` → validates venv and dependencies
- Added: Error recovery with better messages
- Documented: `VPS_DEPLOYMENT.md` with step-by-step guide

### 6. **Requirements** ✓
- Added `requests>=2.31.0` for job page downloads
- All dependencies: playwright, beautifulsoup4, requests, webdriver-manager

## 🧪 Testing Checklist

- [x] Local validation passes: `python3 validate_data_structure.py`
- [x] Dashboard server starts: `python3 dashboard_server.py`
- [x] API responds: `curl http://localhost:8000/api/files`
- [x] All 22 JSON files accessible
- [x] 7,968 job records present
- [x] 471 unique post IDs
- [x] Date range correct: 2025-10-21 to 2025-12-10

## 🐛 Troubleshooting

### Dashboard shows "No data files loaded"
```bash
# Solution:
python3 generate_dashboard_api.py
python3 dashboard_server.py
# Reload browser: http://localhost:8000
```

### Server error "Port 8000 already in use"
```bash
# Find and kill process:
lsof -i :8000
kill -9 <PID>
# Or use different port in dashboard_server.py
```

### Data validation fails
```bash
# Check data structure:
ls -la data/
find data -type f -name "*.json" | wc -l
find data -type f -name "*.html" | wc -l

# Run validation:
python3 validate_data_structure.py
```

### Dashboard not loading jobs
```bash
# Check browser console:
# Open: http://localhost:8000
# Press: F12 (Developer Tools)
# Check Console tab for errors

# Also test API directly:
curl -s http://localhost:8000/api/files | python3 -m json.tool
curl -s http://localhost:8000/data/2025/10/21/output_20251021_112750.json | python3 -m json.tool
```

## 📝 Important Files

| File | Purpose | Status |
|------|---------|--------|
| `fetch_lobbyx.py` | Main scraper | ✅ Updated |
| `parse_html_to_json.py` | Parser | ✅ Updated |
| `download_job_pages.py` | Job page downloader | ✅ Created |
| `generate_dashboard_api.py` | API generator | ✅ Fixed |
| `dashboard_server.py` | Web server | ✅ Fixed |
| `dashboard.html` | UI (1644 lines) | ✅ Working |
| `validate_data_structure.py` | Data validator | ✅ Created |
| `migrate_to_data_folder.py` | Migration utility | ✅ Created |
| `requirements.txt` | Dependencies | ✅ Updated |
| `setup_server.sh` | VPS setup | ✅ Updated |
| `deploy.sh` | Deployment script | ✅ Updated |

## 🎯 Next Steps

### For VPS Deployment
1. Wait for server connectivity (currently unreachable at 123.45.67.89)
2. Run: `./deploy.sh root@123.45.67.89 /var/www/quiet-quail`
3. SSH to server and run: `./setup_server.sh`
4. Setup cron: `./setup_cron.sh`

### For Local Development
1. Run: `python3 dashboard_server.py`
2. Open: `http://localhost:8000`
3. Test features: filters, sorting, dark mode, etc.

### For Production
1. Choose deployment method:
   - Option A: Use `dashboard_server.py` (development)
   - Option B: Use Nginx/Apache with static HTML
   - Option C: Use Gunicorn/uWSGI with dashboard_server.py
2. Configure proper logging and monitoring
3. Setup SSL/TLS for HTTPS
4. Configure cron for scheduled scraping

## 📞 Git Commits Summary

```
✅ Consolidate data directories into unified data/ folder
✅ Add data structure validation and fix deployment  
✅ Add comprehensive VPS deployment documentation
✅ Add deployment fixes documentation
✅ Fix dashboard data loading - update to use data/ directory
✅ Add dashboard fix documentation
```

## 💾 Data Statistics

- **Total HTML files:** 24 (raw scrapes)
- **Total JSON files:** 22 (processed jobs)
- **Total records:** 7,968 (with duplicates)
- **Unique jobs:** 471 (after deduplication)
- **Date range:** Oct 21 - Dec 10, 2025
- **Data size:** ~4.5MB JSON data
- **Organization:** YYYY/MM/DD structure

---

**Status:** ✅ Ready for Use
**Last Updated:** 2025-12-13
**All Systems:** Operational
