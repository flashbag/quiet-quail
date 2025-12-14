# Cron Statistics - Location & Viewing

## 📁 Where Statistics Are Written

**File**: `logs/cron_stats.jsonl`
**Format**: JSONL (one JSON per line)
**Created**: Automatically when `download_job_pages.py` runs

Each line contains:
```json
{
  "timestamp": "2025-12-14T21:35:51.123456",
  "new_jobs_found": 8,
  "jobs_downloaded": 8,
  "download_successful": 8,
  "download_failed": 0,
  "metadata_generated": 10,
  "metadata_skipped": 461,
  "metadata_failed": 0
}
```

## 🔍 View Statistics

### Simple Viewer (Recommended)
```bash
# Latest run
python3 tools/view_cron_stats.py

# Last 5 runs
python3 tools/view_cron_stats.py --last 5

# Last 100 runs
python3 tools/view_cron_stats.py --last 100
```

**Output Example:**
```
======================================================================
⏰ 2025-12-14 21:35:51
======================================================================
Jobs Found:            8
Downloaded:            8 ✓
  Success:             8
  Failed:              0 ✗
Metadata:
  Generated:          10 ✓
  Skipped:           461
  Failed:              0 ✗
```

### Detailed Analysis
```bash
# Last 10 runs with stats table
python3 tools/analyze_cron_stats.py

# All runs
python3 tools/analyze_cron_stats.py --all

# Last 7 days
python3 tools/analyze_cron_stats.py --days=7

# Timeline chart
python3 tools/analyze_cron_stats.py --timeline

# CSV export
python3 tools/analyze_cron_stats.py --csv
```

## 📊 What You Can Track

- **Jobs Found** - New job postings discovered
- **Download Success** - How many jobs were downloaded
- **Download Failures** - Failed downloads (network issues, etc)
- **Metadata Stats** - JSON metadata generation success/failures
- **Trends** - Over time to spot issues

## 🚀 Quick Commands

```bash
# See what happened in last cron run
python3 tools/view_cron_stats.py

# Check last 5 runs
python3 tools/view_cron_stats.py --last 5

# Get stats summary for analysis
python3 tools/analyze_cron_stats.py

# View as raw JSON
python3 tools/view_cron_stats.py --raw

# See timeline of job discoveries
python3 tools/analyze_cron_stats.py --timeline
```

## 📖 Full Documentation

See [CRON_STATS_VIEWER.md](CRON_STATS_VIEWER.md) for detailed guide.
