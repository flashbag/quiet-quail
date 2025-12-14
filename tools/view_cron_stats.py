#!/usr/bin/env python3
"""
Simple viewer for cron statistics.

Location: logs/cron_stats.jsonl
Format: JSONL (one JSON object per line)

Usage:
    python3 tools/view_cron_stats.py              # View latest run
    python3 tools/view_cron_stats.py --last 5     # Last 5 runs
    python3 tools/view_cron_stats.py --last 100   # Last 100 runs
    python3 tools/view_cron_stats.py --raw        # Raw JSON output
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def read_stats_file():
    """Read all stats from JSONL file."""
    stats_file = Path("logs/cron_stats.jsonl")
    
    if not stats_file.exists():
        print(f"📁 Stats file not found: {stats_file}")
        print("\nStats are created when download_job_pages.py runs")
        return []
    
    stats = []
    try:
        with open(stats_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        stat = json.loads(line)
                        stats.append(stat)
                    except json.JSONDecodeError as e:
                        print(f"Warning: Could not parse line {line_num}")
    except Exception as e:
        print(f"Error reading file: {e}")
        return []
    
    return stats


def format_timestamp(ts_str):
    """Format ISO timestamp to readable format."""
    try:
        dt = datetime.fromisoformat(ts_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return ts_str


def print_single_stat(stat):
    """Pretty print a single stat entry."""
    print(f"\n{'='*70}")
    print(f"⏰ {format_timestamp(stat['timestamp'])}")
    
    # Check if this was a skipped run
    if stat.get('note') == 'skipped - recent cache found':
        print(f"{'='*70}")
        print("⏭️  SKIPPED (Recent cache found - no jobs to check)")
        return
    
    print(f"{'='*70}")
    print(f"Jobs Found:        {stat['new_jobs_found']:>3}")
    print(f"Downloaded:        {stat['jobs_downloaded']:>3} ✓")
    print(f"  Success:         {stat['download_successful']:>3}")
    print(f"  Failed:          {stat['download_failed']:>3} ✗")
    print(f"Metadata:")
    print(f"  Generated:       {stat['metadata_generated']:>3} ✓")
    print(f"  Skipped:         {stat['metadata_skipped']:>3}")
    print(f"  Failed:          {stat['metadata_failed']:>3} ✗")


def main():
    """Main entry point."""
    num_runs = 10  # Show last 10 runs by default (like analyze_cron_stats.py)
    raw_mode = False
    
    # Parse arguments
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--raw":
            raw_mode = True
        elif arg == "--last" and i+1 < len(sys.argv)-1:
            try:
                num_runs = int(sys.argv[i+2])
            except ValueError:
                print("Invalid number for --last")
                sys.exit(1)
    
    stats = read_stats_file()
    
    if not stats:
        return
    
    # Get requested runs
    if num_runs > len(stats):
        num_runs = len(stats)
    
    selected_stats = stats[-num_runs:]
    
    if raw_mode:
        # Output raw JSON
        for stat in selected_stats:
            print(json.dumps(stat, ensure_ascii=False, indent=2))
    else:
        # Pretty print each stat
        for stat in selected_stats:
            print_single_stat(stat)
        
        # Summary for multiple runs
        if len(selected_stats) > 1:
            print(f"\n{'='*70}")
            print("📊 Summary (Last {} Runs)".format(len(selected_stats)))
            print(f"{'='*70}")
            
            total_found = sum(s['new_jobs_found'] for s in selected_stats)
            total_downloaded = sum(s['jobs_downloaded'] for s in selected_stats)
            total_failed = sum(s['download_failed'] for s in selected_stats)
            
            print(f"Total Jobs Found:   {total_found}")
            print(f"Total Downloaded:   {total_downloaded} ✓")
            print(f"Total Failed:       {total_failed} ✗")
            print(f"Success Rate:       {100*total_downloaded/(total_downloaded+total_failed) if (total_downloaded+total_failed)>0 else 0:.1f}%")
        
        print(f"\n{'='*70}\n")


if __name__ == '__main__':
    main()
