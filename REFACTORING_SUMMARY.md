# Pipeline Refactoring Summary

## ✅ What Changed

### Scripts Reorganized (4 Clear Stages)

| Stage | Old Name | New Name | Purpose |
|-------|----------|----------|---------|
| 1 | fetch_lobbyx.py (partial) | **1_fetch_main_page.py** | Fetch jobs listing from lobbyx.army |
| 2 | parse_html_to_json.py | **2_parse_html_to_json.py** | Parse HTML → JSON with job data |
| 3 | download_job_pages.py | **3_download_job_pages.py** | Download individual job pages |
| 4 | generate_dashboard_api.py | **4_generate_dashboard_api.py** | Generate dashboard file list |

### Orchestration
- **Old:** `scripts/fetch_lobbyx.py` (orchestrator with caching)
- **New:** `run_scraper_pipeline.py` (simple stage runner) + numbered scripts

### Cache Removal
All caching and force options **completely removed**:

**Removed:**
- `should_fetch_main_page()` function
- `should_download_job_pages()` function  
- `--force`, `-f` flags
- `--no-cache` flag
- `--cache-hours N` flag
- `skip_recent` parameter
- `recent_hours` parameter
- All cache validation logic

**Result:** Scripts always run completely fresh on every execution

## 📊 Pipeline Flow

```
┌─────────────────────────────────────────┐
│  1. Fetch Main Page                     │
│  → data/YYYY/MM/DD/output_*.html        │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  2. Parse HTML to JSON                  │
│  → data/YYYY/MM/DD/output_*.json        │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  3. Download Job Pages                  │
│  → data/job-pages/{ID:3}/{ID:3}/        │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  4. Generate Dashboard API              │
│  → api/list-json-files.json             │
└─────────────────────────────────────────┘
```

## 🎯 Benefits

1. **Clear Ordering:** Numbered scripts show execution order immediately
2. **No Caching Confusion:** Always fresh fetch, no skipped runs
3. **Easier Debugging:** Each stage logs separately, clear stage identification
4. **Simpler Cron:** Cron wrapper just calls one pipeline script
5. **Modular:** Each stage can run independently
6. **Progress Tracking:** Stage numbers in logs, checkmarks for completion

## 🚀 How to Run

### Complete Pipeline
```bash
python3 run_scraper_pipeline.py
```

### Individual Stages
```bash
python3 scripts/1_fetch_main_page.py
python3 scripts/2_parse_html_to_json.py
python3 scripts/3_download_job_pages.py
python3 scripts/4_generate_dashboard_api.py
```

### Cron (Automatic)
Cron now calls: `python3 run_scraper_pipeline.py` (via config/cron_wrapper.sh)

## 📝 Logging

All stages log to:
- `debug.log` - Detailed execution logs
- `cron.log` - Cron job execution (when run via cron)

Example output:
```
======================================================================
STAGE 1: Fetching main jobs listing page
======================================================================
2025-12-16 10:00:00 - INFO - Navigating to: https://lobbyx.army/?sphere=it
2025-12-16 10:00:05 - INFO - ✓ All content loaded
2025-12-16 10:00:06 - INFO - ✓ Page saved to data/2025/12/16/output_100006.html
2025-12-16 10:00:06 - INFO - STAGE 1 Complete

======================================================================
STAGE 2: Parsing HTML to JSON
======================================================================
2025-12-16 10:00:06 - INFO - Found 1 HTML files to process
2025-12-16 10:00:07 - INFO - ✓ Processed 1/1 files
2025-12-16 10:00:07 - INFO - ✓ Extracted 42 total posts
2025-12-16 10:00:07 - INFO - STAGE 2 Complete
...
```

## 🔧 Files Changed

**New Files:**
- `scripts/1_fetch_main_page.py`
- `scripts/2_parse_html_to_json.py`
- `scripts/3_download_job_pages.py`
- `scripts/4_generate_dashboard_api.py`
- `run_scraper_pipeline.py` (orchestrator)
- `PIPELINE.md` (documentation)

**Modified Files:**
- `config/cron_wrapper.sh` - Updated to use pipeline
- `scripts/fetch_lobbyx.py` - (kept for reference, no longer used)

**Removed (Functionality):**
- All caching logic
- All CLI options for cache control

## ✅ Verification

All 4 scripts exist and follow numbering:
```
✓ scripts/1_fetch_main_page.py
✓ scripts/2_parse_html_to_json.py  
✓ scripts/3_download_job_pages.py
✓ scripts/4_generate_dashboard_api.py
✓ run_scraper_pipeline.py (orchestrator)
```

## 🚨 Next Steps on VPS

1. Pull the latest changes:
   ```bash
   cd /var/www/quiet-quail
   git pull origin main
   ```

2. Test the new pipeline:
   ```bash
   python3 run_scraper_pipeline.py
   ```

3. The cron job will automatically use the new pipeline on next execution

## 📚 Documentation

See [PIPELINE.md](PIPELINE.md) for detailed documentation of each stage.
