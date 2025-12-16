# Quiet-Quail Job Scraper Pipeline

## Overview

The job scraping process is now organized as a **clear 4-stage pipeline**. Each stage handles a specific task and runs independently. This design makes debugging easier and provides clear visibility into the process.

## Pipeline Stages

### Stage 1: Fetch Main Page
**Script:** `scripts/1_fetch_main_page.py`

Fetches the complete jobs listing from lobbyx.army with all content loaded.

- **Input:** None (always fetches fresh)
- **Output:** `data/YYYY/MM/DD/output_HHMMSS.html`
- **Process:**
  - Launches browser using Playwright
  - Navigates to `https://lobbyx.army/?sphere=it`
  - Clicks "Load More" button until all content is loaded
  - Saves complete HTML with all jobs loaded

### Stage 2: Parse HTML to JSON
**Script:** `scripts/2_parse_html_to_json.py`

Parses the HTML files from Stage 1 and extracts structured job data.

- **Input:** `data/YYYY/MM/DD/output_*.html`
- **Output:** `data/YYYY/MM/DD/output_*.json`
- **Process:**
  - Finds all HTML files in data directory
  - Extracts job postings from HTML
  - Creates JSON with job details (ID, URL, position, unit, categories, status)
  - Maintains same directory structure as input

### Stage 3: Download Job Pages
**Script:** `scripts/3_download_job_pages.py`

Downloads individual job posting pages and creates metadata.

- **Input:** `data/YYYY/MM/DD/output_*.json` (list of jobs)
- **Output:**
  - `data/job-pages/{ID:3}/{ID:3}/job_ID.html` (individual job HTML)
  - `data/job-pages/{ID:3}/{ID:3}/job_ID.json` (job metadata)
- **Process:**
  - Reads JSON files from Stage 2
  - Downloads each job page using requests
  - Generates metadata JSON for each job (status, position, unit, content)
  - Limits to 100 downloads per run to avoid overloading
  - Logs cron statistics for monitoring

### Stage 4: Generate Dashboard API
**Script:** `scripts/4_generate_dashboard_api.py`

Creates the JSON file list for the dashboard.

- **Input:** All JSON files in `data/` directory
- **Output:** `api/list-json-files.json`
- **Process:**
  - Scans entire data directory for JSON files
  - Creates list with file paths and metadata
  - Dashboard uses this file to load job data

## Running the Pipeline

### Complete Pipeline (All Stages)
```bash
python3 run_scraper_pipeline.py
```

This runs all 4 stages in order. If a stage fails, it logs the error and continues to the next stage.

### Individual Stages
```bash
# Stage 1: Fetch
python3 scripts/1_fetch_main_page.py

# Stage 2: Parse
python3 scripts/2_parse_html_to_json.py

# Stage 3: Download
python3 scripts/3_download_job_pages.py

# Stage 4: API
python3 scripts/4_generate_dashboard_api.py
```

## Key Differences from Previous Version

### Removed
- **Cache checking** - Scripts no longer check if files are recent
- **Force options** - No `--force`, `--no-cache`, or `--cache-hours` flags
- **Conditional execution** - All stages always run (or can run independently)
- **Orchestration complexity** - Single `fetch_lobbyx.py` replaced with clear pipeline

### Added
- **Numbered scripts** - Clear ordering: 1_, 2_, 3_, 4_
- **Stage logging** - Each stage prints its stage number and completion
- **Pipeline orchestrator** - `run_scraper_pipeline.py` manages all stages
- **Clear separation** - Each script focuses on one job
- **Progress indicators** - Download progress (X/Y files), checkmarks for success

## Cron Integration

The cron wrapper (`config/cron_wrapper.sh`) now calls the pipeline:

```bash
# Old (removed)
python3 scripts/fetch_lobbyx.py

# New
python3 run_scraper_pipeline.py
```

Cron runs every hour automatically. The pipeline:
1. Always fetches fresh data (no cache skipping)
2. Processes all stages in order
3. Logs all output to `cron.log`
4. Records statistics to `logs/cron_stats.jsonl`

## Logging & Monitoring

### Debug Log
```bash
tail -f debug.log  # All stages log here
```

### Cron Log
```bash
tail -f cron.log  # Cron execution
```

### Statistics
```bash
# View last 10 cron runs
python3 tools/view_cron_stats.py

# Analyze all statistics
python3 tools/analyze_cron_stats.py
```

## Directory Structure

```
data/
  YYYY/MM/DD/
    output_HHMMSS.html   (Stage 1 - HTML listing)
    output_HHMMSS.json   (Stage 2 - Parsed jobs)
  job-pages/
    {ID:3}/{ID:3}/
      job_ID.html        (Stage 3 - Individual job HTML)
      job_ID.json        (Stage 3 - Job metadata)

api/
  list-json-files.json   (Stage 4 - Dashboard file list)

logs/
  cron_stats.jsonl       (Statistics from each cron run)
```

## Troubleshooting

### Stage 1 fails (fetch)
- Check network connectivity
- Verify `https://lobbyx.army/?sphere=it` is accessible
- Check browser timeout (30 seconds) - may need increase for slow connections

### Stage 2 fails (parse)
- Verify HTML files exist from Stage 1
- Check for HTML format changes on website
- May need to update CSS selectors if website structure changed

### Stage 3 fails (download)
- Verify JSON files exist from Stage 2
- Check network connectivity for downloading job pages
- Individual failures don't block the pipeline

### Stage 4 fails (API)
- Verify JSON files exist in data directory
- Check write permissions for `api/` directory

## Future Improvements

- Add rate limiting to prevent overloading lobbyx.army
- Add retry logic with exponential backoff
- Add caching back with user control (optional)
- Add webhook notifications on failures
- Add data validation between stages
