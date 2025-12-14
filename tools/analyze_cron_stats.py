#!/usr/bin/env python3
"""
Analyze cron run statistics from the JSONL stats file.
Provides summary statistics and trends over time.

Usage:
    python3 tools/analyze_cron_stats.py              # Show last 10 runs
    python3 tools/analyze_cron_stats.py --all        # Show all runs
    python3 tools/analyze_cron_stats.py --days 7     # Show last 7 days
    python3 tools/analyze_cron_stats.py --csv        # Export to CSV
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from statistics import mean, median


def read_stats(limit=None, days=None):
    """Read stats from JSONL file with optional filtering."""
    stats_file = Path("logs/cron_stats.jsonl")
    
    if not stats_file.exists():
        print(f"Stats file not found: {stats_file}")
        return []
    
    stats = []
    cutoff_date = None
    
    if days:
        cutoff_date = datetime.now() - timedelta(days=days)
    
    with open(stats_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                stat = json.loads(line)
                stat_dt = datetime.fromisoformat(stat["timestamp"])
                
                if cutoff_date and stat_dt < cutoff_date:
                    continue
                
                stats.append(stat)
    
    if limit:
        stats = stats[-limit:]
    
    return stats


def print_table(stats):
    """Print stats as a formatted table."""
    if not stats:
        print("No stats available")
        return
    
    print("\nCron Run Statistics:")
    print("-" * 120)
    print(f"{'Timestamp':<20} {'Found':<8} {'Downloaded':<12} {'Success':<10} {'Failed':<8} {'Meta Gen':<10} {'Meta Skip':<10}")
    print("-" * 120)
    
    for s in stats:
        ts = s["timestamp"].split("T")[0] + " " + s["timestamp"].split("T")[1][:8]
        print(f"{ts:<20} {s['new_jobs_found']:<8} {s['jobs_downloaded']:<12} {s['download_successful']:<10} {s['download_failed']:<8} {s['metadata_generated']:<10} {s['metadata_skipped']:<10}")
    
    print("-" * 120)


def print_summary(stats):
    """Print summary statistics."""
    if not stats:
        print("No stats available")
        return
    
    found_all = [s["new_jobs_found"] for s in stats]
    downloaded_all = [s["jobs_downloaded"] for s in stats]
    
    print("\nSummary Statistics:")
    print(f"  Total runs: {len(stats)}")
    print(f"  Total jobs found: {sum(found_all)}")
    print(f"  Total jobs downloaded: {sum(downloaded_all)}")
    print(f"  Average jobs per run: {mean(found_all):.1f}")
    print(f"  Median jobs per run: {median(found_all):.1f}")
    print(f"  Max jobs in single run: {max(found_all)}")
    print(f"  Min jobs in single run: {min(found_all)}")
    
    failed_runs = [s for s in stats if s["download_failed"] > 0]
    if failed_runs:
        print(f"  Runs with failures: {len(failed_runs)}")


def export_csv(stats):
    """Export stats as CSV to stdout."""
    if not stats:
        print("No stats available")
        return
    
    print("timestamp,new_jobs_found,jobs_downloaded,download_successful,download_failed,metadata_generated,metadata_skipped,metadata_failed")
    for s in stats:
        print(f"{s['timestamp']},{s['new_jobs_found']},{s['jobs_downloaded']},{s['download_successful']},{s['download_failed']},{s['metadata_generated']},{s['metadata_skipped']},{s['metadata_failed']}")


def main():
    """Main entry point."""
    limit = 10
    days = None
    csv_mode = False
    
    # Parse arguments
    for arg in sys.argv[1:]:
        if arg == "--all":
            limit = None
        elif arg == "--csv":
            csv_mode = True
        elif arg.startswith("--days"):
            days = int(arg.split("=")[1])
    
    stats = read_stats(limit=limit, days=days)
    
    if csv_mode:
        export_csv(stats)
    else:
        print_table(stats)
        print_summary(stats)


if __name__ == "__main__":
    main()
