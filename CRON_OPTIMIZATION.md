# Cron Optimization: Stages 1-2 Only

## Overview

The cron job has been optimized to run **only the first two stages** (fetch and parse):

- **Stage 1:** Fetch main page from lobbyx.army
- **Stage 2:** Parse HTML to JSON

Stages 3 & 4 (downloading individual pages and generating API) are **NOT run by cron**.

## Pipeline Architecture

### Cron Pipeline (Hourly)
```
run_cron_pipeline.py
├── Stage 1: 1_fetch_main_page.py (15-30 min)
│   └── Output: data/YYYY/MM/DD/output_*.html
├── Stage 2: 2_parse_html_to_json.py (5-10 min)
│   ├── Output: data/YYYY/MM/DD/output_*.json
│   └── Logs: parsed_jobs count to cron_stats.jsonl
└── Total Timeout: 30 minutes
```

### Full Pipeline (Manual/Scheduled)
```
run_scraper_pipeline.py
├── Stage 1: Fetch
├── Stage 2: Parse
├── Stage 3: Download job pages (optional)
└── Stage 4: Generate API (optional)
```

## Changes Made

### 1. New Cron Pipeline
**File:** `run_cron_pipeline.py`
- Only runs stages 1-2
- 30-minute timeout (vs 1 hour for full pipeline)
- Faster cron execution

### 2. Stage 2 Enhancements
**File:** `scripts/2_parse_html_to_json.py`

**New function:** `log_cron_stats(parsed_count)`
- Logs parsed job count to `logs/cron_stats.jsonl`
- Called at end of parsing with total posts found

**Statistics logged:**
```json
{
  "timestamp": "2025-12-16T10:00:00.123456",
  "parsed_jobs": 42
}
```

### 3. Stage 1 Improvements
**File:** `scripts/1_fetch_main_page.py`

**Enhancements:**
- Added `max_attempts` limit (100) to prevent infinite loops
- Added attempt counter in debug logs
- Better error handling for load-more clicking

### 4. Cron Wrapper Update
**File:** `config/cron_wrapper.sh`

**Changes:**
- Now calls `python3 run_cron_pipeline.py` (stages 1-2 only)
- Reduced timeout from 1 hour to 30 minutes
- Updated log messages to reflect "cron pipeline"

## Statistics Tracking

### Before
Cron stats only recorded when **downloads happened** (Stage 3):
- Only stats from `3_download_job_pages.py`
- Hours with no new jobs = no stats recorded

### After
Cron stats recorded for **every cron run**:
- Stage 2 logs `parsed_jobs` count
- One line per cron run with timestamp and parsed count
- Example:
  ```
  2025-12-16T10:00:00.123456 - parsed_jobs: 42
  2025-12-16T11:00:00.234567 - parsed_jobs: 35
  2025-12-16T12:00:00.345678 - parsed_jobs: 28
  ```

## Viewing Cron Statistics

### Raw stats file
```bash
cat logs/cron_stats.jsonl | tail -20
```

### View recent stats
```bash
python3 tools/view_cron_stats.py --last 20
```

### Analyze trends
```bash
python3 tools/analyze_cron_stats.py
```

## Workflow

### Hourly Cron (Automatic)
```
Every hour:
  1. Fetch latest jobs listing page
  2. Parse HTML and extract jobs
  3. Log parsed count to stats
  4. Done (no downloads, no API generation)
```

### Manual Full Run (Optional)
```bash
# When you want to download pages and generate API:
python3 run_scraper_pipeline.py
# This runs all 4 stages including download and API generation
```

### Individual Stages (As Needed)
```bash
# Just fetch
python3 scripts/1_fetch_main_page.py

# Just parse
python3 scripts/2_parse_html_to_json.py

# Download pages
python3 scripts/3_download_job_pages.py

# Generate API
python3 scripts/4_generate_dashboard_api.py
```

## Playwright Verification

### Stage 1 Click Logic
✅ **Improved:**
- Max attempts limit prevents infinite loops
- Attempt counter in logs shows click progression
- Clear error messages for failures
- Handles both successful load ("done" class) and early termination

### Example Output
```
2025-12-16 10:00:05 - INFO - Navigating to: https://lobbyx.army/?sphere=it
2025-12-16 10:00:08 - DEBUG - Clicking load-more button (attempt 1)...
2025-12-16 10:00:10 - DEBUG - Clicking load-more button (attempt 2)...
2025-12-16 10:00:12 - DEBUG - Clicking load-more button (attempt 3)...
2025-12-16 10:00:14 - INFO - ✓ All content loaded
2025-12-16 10:00:15 - INFO - ✓ Page saved to data/2025/12/16/output_100015.html
```

## Benefits

✅ **Faster cron execution** - Only 30 min vs 1 hour  
✅ **Better statistics** - Every cron run tracked  
✅ **Cleaner separation** - Cron does fetch+parse, manual does full pipeline  
✅ **Improved robustness** - Playwright click loop has safeguards  
✅ **Flexible workflows** - Can run stages independently as needed  

## Files Changed

**New:**
- `run_cron_pipeline.py` - Cron-specific 2-stage pipeline

**Modified:**
- `scripts/1_fetch_main_page.py` - Improved Playwright clicking
- `scripts/2_parse_html_to_json.py` - Added cron stats logging
- `config/cron_wrapper.sh` - Uses new cron pipeline

**Unchanged:**
- `run_scraper_pipeline.py` - Full 4-stage pipeline (still available)
- All other stage scripts work as before

## Next Steps

1. ✅ Code deployed (git push)
2. ⏳ Wait for next cron run to see stats in `logs/cron_stats.jsonl`
3. ⏳ Monitor stats with `python3 tools/view_cron_stats.py`
4. Optional: Schedule full pipeline runs (stages 3-4) separately

---

**Latest Commit:** e82fdb9 - "Refactor: Split pipelines - cron runs stages 1-2 only"
