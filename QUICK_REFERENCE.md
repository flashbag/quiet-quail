# Quick Reference: New Pipeline Structure

## 📋 Four-Stage Pipeline

```
Stage 1: Fetch Main Page
  └─ Script: scripts/1_fetch_main_page.py
  └─ Output: data/YYYY/MM/DD/output_HHMMSS.html
  └─ Task: Download full jobs listing from lobbyx.army

Stage 2: Parse HTML → JSON
  └─ Script: scripts/2_parse_html_to_json.py
  └─ Output: data/YYYY/MM/DD/output_HHMMSS.json
  └─ Task: Extract job data from HTML

Stage 3: Download Job Pages
  └─ Script: scripts/3_download_job_pages.py
  └─ Output: data/job-pages/{ID:3}/{ID:3}/job_*.{html,json}
  └─ Task: Download individual job pages & metadata

Stage 4: Generate Dashboard API
  └─ Script: scripts/4_generate_dashboard_api.py
  └─ Output: api/list-json-files.json
  └─ Task: Create file list for dashboard
```

## ⚡ How to Run

### All Stages (Recommended)
```bash
python3 run_scraper_pipeline.py
```

### Individual Stage
```bash
python3 scripts/1_fetch_main_page.py    # Stage 1
python3 scripts/2_parse_html_to_json.py  # Stage 2
python3 scripts/3_download_job_pages.py  # Stage 3
python3 scripts/4_generate_dashboard_api.py  # Stage 4
```

## 🔍 Monitoring

### Real-time Debug Log
```bash
tail -f debug.log
```

### Cron Execution
```bash
tail -f cron.log
```

### View Last 10 Cron Runs
```bash
python3 tools/view_cron_stats.py
```

### Analyze All Statistics
```bash
python3 tools/analyze_cron_stats.py --timeline
```

## 📊 Key Facts

| Aspect | Details |
|--------|---------|
| **Caching** | ❌ Removed - Always fetch fresh |
| **CLI Options** | ❌ Removed - No --force, --no-cache, etc |
| **Cron Frequency** | Every hour (automatic) |
| **Max Downloads** | 100 jobs per run |
| **Timeout** | 1 hour per full pipeline |
| **Statistics** | Logged to `logs/cron_stats.jsonl` |

## 🚀 Deployment

On VPS, pull and test:
```bash
cd /var/www/quiet-quail
git pull origin main
python3 run_scraper_pipeline.py
```

Cron automatically uses new pipeline via `config/cron_wrapper.sh`

## 📂 File Structure After Running

```
data/
├── 2025/12/16/
│   ├── output_100006.html      ← Stage 1 (HTML)
│   ├── output_100006.json      ← Stage 2 (parsed jobs)
│   └── ...
└── job-pages/
    ├── 001/
    │   ├── 001/
    │   │   ├── job_1001.html   ← Stage 3 (job HTML)
    │   │   └── job_1001.json   ← Stage 3 (metadata)

api/
└── list-json-files.json        ← Stage 4 (dashboard list)

logs/
└── cron_stats.jsonl            ← Statistics tracking
```

## ✅ What's New

✅ Clear stage numbering (1_, 2_, 3_, 4_)  
✅ No cache confusion  
✅ Always fresh data  
✅ Simpler orchestration  
✅ Better visibility  
✅ Easier debugging  

---

**Last Updated:** 2025-12-16  
**Commits:** 5c237b0 + c78ff0b + eb1c94d
