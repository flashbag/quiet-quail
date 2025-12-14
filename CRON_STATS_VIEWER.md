# Cron Statistics Viewer

## Location

**File**: `logs/cron_stats.jsonl`
**Format**: JSONL (JSON Lines - one JSON object per line)
**Created by**: `scripts/download_job_pages.py` on each run

## Quick View

```bash
# View latest cron run
python3 tools/view_cron_stats.py

# View last 5 runs
python3 tools/view_cron_stats.py --last 5

# View last 100 runs
python3 tools/view_cron_stats.py --last 100

# View as raw JSON
python3 tools/view_cron_stats.py --raw
```

## Detailed Analysis

```bash
# Show last 10 runs with statistics
python3 tools/analyze_cron_stats.py

# Show all runs
python3 tools/analyze_cron_stats.py --all

# Show last 7 days
python3 tools/analyze_cron_stats.py --days=7

# Show timeline chart
python3 tools/analyze_cron_stats.py --timeline

# Export to CSV
python3 tools/analyze_cron_stats.py --csv > stats.csv
```

## What Gets Recorded

Each cron run records:
- **Timestamp** - When the job ran
- **new_jobs_found** - Number of new job postings discovered
- **jobs_downloaded** - Total jobs downloaded
- **download_successful** - Successful downloads
- **download_failed** - Failed downloads
- **metadata_generated** - Metadata JSON files created
- **metadata_skipped** - Existing metadata not re-generated
- **metadata_failed** - Failed metadata generation

## Example Output

### View Single Run
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

### View Summary (Multiple Runs)
```
======================================================================
📊 Summary (Last 5 Runs)
======================================================================
Total Jobs Found:   42
Total Downloaded:   40 ✓
Total Failed:        2 ✗
Success Rate:       95.2%
```

## Using the Data

### Monitor Job Discovery Trends
```bash
python3 tools/analyze_cron_stats.py --timeline
```
Shows graphical timeline of jobs found per run.

### Export for External Analysis
```bash
python3 tools/analyze_cron_stats.py --csv > stats.csv
# Import into Excel, Google Sheets, etc.
```

### Check Recent Activity
```bash
python3 tools/view_cron_stats.py --last 10
```
Quickly see what happened in last 10 cron runs.

### Identify Issues
```bash
python3 tools/analyze_cron_stats.py
```
Look for:
- High failure rates
- Declining job discovery
- Metadata generation problems

## Raw JSON Access

For custom analysis, you can read the raw file:

```bash
# View raw JSONL
cat logs/cron_stats.jsonl

# Last 5 entries
tail -5 logs/cron_stats.jsonl

# Parse with jq (if installed)
cat logs/cron_stats.jsonl | jq '.'
```

## Troubleshooting

### "Stats file not found"
- Cron jobs haven't run yet
- Run `python3 scripts/download_job_pages.py` manually to create stats
- Check that `logs/` directory exists

### Empty or incomplete stats
- Check file permissions: `ls -la logs/cron_stats.jsonl`
- Run download_job_pages.py and check for errors

### Corrupt line in JSONL
- The viewer will skip invalid lines
- Check manually: `python3 tools/view_cron_stats.py --raw`
