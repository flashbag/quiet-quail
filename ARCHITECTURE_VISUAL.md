# Pipeline Architecture - Visual Guide

## Before vs After

### BEFORE (Single Pipeline)
```
Cron (Hourly)
    ↓
run_scraper_pipeline.py
    ├─ Stage 1: Fetch (15-30 min)
    ├─ Stage 2: Parse (5-10 min)
    ├─ Stage 3: Download Pages (30-60 min) ← Heavy operation
    └─ Stage 4: Generate API (1-5 min)
    
Total: 60-120 minutes (often timeout!)
Problem: Heavy download stage slowing down cron
```

### AFTER (Split Pipelines)
```
Cron (Hourly)
    ↓
run_cron_pipeline.py
    ├─ Stage 1: Fetch (15-30 min)
    ├─ Stage 2: Parse (5-10 min) ← Logs parsed_jobs count
    └─ Done!
    
Total: 20-40 minutes ✅

Manual (When needed)
    ↓
run_scraper_pipeline.py
    ├─ Stage 1: Fetch
    ├─ Stage 2: Parse
    ├─ Stage 3: Download Pages (heavy)
    └─ Stage 4: Generate API
```

## Data Flow

```
CRON EXECUTION (Every Hour)
════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────┐
│ 1️⃣  FETCH MAIN PAGE (Stage 1)                                  │
│────────────────────────────────────────────────────────────────│
│ • Use Playwright to browse lobbyx.army                          │
│ • Click "Load More" button (with safeguards)                   │
│ • Save complete HTML with all jobs loaded                      │
│ • Output: data/YYYY/MM/DD/output_HHMMSS.html                  │
│ • Time: 15-30 minutes                                           │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2️⃣  PARSE HTML TO JSON (Stage 2)                              │
│────────────────────────────────────────────────────────────────│
│ • Extract job listings from HTML                               │
│ • Parse job data (ID, position, unit, category, status)      │
│ • Save structured JSON data                                    │
│ • Output: data/YYYY/MM/DD/output_HHMMSS.json                 │
│ • Time: 5-10 minutes                                            │
│                                                                 │
│ 📊 LOG STATISTICS:                                             │
│    ├─ parsed_jobs count                                        │
│    ├─ timestamp                                                │
│    └─ Save to: logs/cron_stats.jsonl                           │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
                    ✅ DONE
             Total Time: 20-40 minutes
```

## Statistics File Format

```json
// logs/cron_stats.jsonl (one entry per line)

{"timestamp": "2025-12-16T10:00:00.123456", "parsed_jobs": 42}
{"timestamp": "2025-12-16T11:00:00.234567", "parsed_jobs": 38}
{"timestamp": "2025-12-16T12:00:00.345678", "parsed_jobs": 35}
{"timestamp": "2025-12-16T13:00:00.345789", "parsed_jobs": 40}
```

## Playwright Click Loop (Stage 1)

```
┌──────────────────────────────────────────┐
│ Navigate to lobbyx.army                  │
└──────────────────┬───────────────────────┘
                   ↓
            ┌──────────────┐
            │ Attempt = 0  │
            └──────┬───────┘
                   ↓
    ┌──────────────────────────────┐
    │ Attempt += 1                 │
    └──────────────┬───────────────┘
                   ↓
    ┌──────────────────────────────────┐
    │ Button has class="done"?         │
    └──┬───────────────────────────────┘
       │
  Yes  │  No
       │  ├─→ Click button
       │  ├─→ Wait 2 seconds (AJAX)
       │  ├─→ Increment attempt
       │  └─→ Check loop condition
       │
  ┌────┴──────────────────────────┐
  │ Attempt >= max_attempts (100)? │
  └──┬────────────────────────────┘
     │
 No  │  Yes
     │  ├─→ Stop (safeguard)
     │  └─→ Log warning
     │
     └─→ ✅ Page fully loaded
```

## File Organization

```
Repository/
├── run_cron_pipeline.py          ← New: Cron pipeline (2 stages)
├── run_scraper_pipeline.py       ← Full pipeline (4 stages)
│
├── scripts/
│   ├── 1_fetch_main_page.py          (improved Playwright)
│   ├── 2_parse_html_to_json.py       (logs stats)
│   ├── 3_download_job_pages.py       (not in cron)
│   └── 4_generate_dashboard_api.py   (not in cron)
│
├── config/
│   └── cron_wrapper.sh           (updated for cron pipeline)
│
├── logs/
│   ├── cron_stats.jsonl          ← Statistics from cron
│   └── debug.log
│
├── data/
│   ├── YYYY/MM/DD/
│   │   ├── output_*.html         (Stage 1)
│   │   └── output_*.json         (Stage 2)
│   │
│   └── job-pages/                (Stage 3 - not in cron)
│       └── {ID:3}/{ID:3}/
│           ├── job_*.html
│           └── job_*.json
│
└── api/                          (Stage 4 - not in cron)
    └── list-json-files.json
```

## Execution Timeline

```
HOURLY CRON EXECUTION (Typical Flow)

10:00:00 - Cron triggered
10:00:01 - run_cron_pipeline.py starts
10:00:02 - Stage 1: Fetch begins
          └─ Launch browser
          └─ Navigate to lobbyx.army
          └─ Click "Load More" 10-20 times
          └─ Save HTML to data/2025/12/16/output_100020.html
10:15:00 - Stage 1: Complete (15 min)
10:15:01 - Stage 2: Parse begins
          └─ Read HTML files
          └─ Extract 42 jobs
          └─ Save JSON to data/2025/12/16/output_100020.json
          └─ Call log_cron_stats(42)
          └─ Append to logs/cron_stats.jsonl
10:20:00 - Stage 2: Complete (5 min)
10:20:01 - Pipeline ends
          └─ Total time: 20 minutes ✅
          └─ Cron moves to next tasks
```

## Statistics Viewing

```bash
# View cron stats (default: last 10 runs)
$ python3 tools/view_cron_stats.py
Shows timestamps and parsed_jobs counts

# View specific number of runs
$ python3 tools/view_cron_stats.py --last 20
Shows last 20 runs

# Analyze trends
$ python3 tools/analyze_cron_stats.py
Shows statistics, timeline, charts
```

## Key Improvements

```
┌─────────────────────────────────────────────────────────┐
│ CRON PERFORMANCE                                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ❌ Before:  60-120 minutes                             │
│    └─ Stage 3 (download) blocked cron                  │
│    └─ Often timed out                                  │
│    └─ Stats only logged on success                     │
│                                                         │
│ ✅ After:   20-40 minutes                              │
│    └─ Light stages only (fetch + parse)               │
│    └─ Never times out                                  │
│    └─ Stats logged every run                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

**Architecture:** Modular pipeline with split cron/manual execution  
**Performance:** 50% faster cron execution  
**Reliability:** Safeguards for Playwright clicking  
**Visibility:** Every cron run tracked in statistics  

---

*Visual Guide - Reference Material*  
*Last Updated: 2025-12-16*
