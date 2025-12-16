#!/usr/bin/env python3
"""
Simple viewer for cron statistics with file validation.

Location: logs/cron_stats.jsonl
Format: JSONL (one JSON object per line)

Usage:
    python3 tools/view_cron_stats.py              # View latest run
    python3 tools/view_cron_stats.py --last 5     # Last 5 runs
    python3 tools/view_cron_stats.py --last 100   # Last 100 runs
    python3 tools/view_cron_stats.py --raw        # Raw JSON output
    python3 tools/view_cron_stats.py --validate   # With file validation
"""

import json
import sys
import os
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


def count_json_files():
    """Count total JSON files in data directory."""
    data_path = Path('data')
    if not data_path.exists():
        return 0
    json_files = list(data_path.rglob('output_*.json'))
    return len(json_files)


def count_job_pages():
    """Count downloaded job page HTML files."""
    job_pages_path = Path('data/job-pages')
    if not job_pages_path.exists():
        return 0
    job_files = list(job_pages_path.rglob('job_*.html'))
    return len(job_files)


def get_latest_json_timestamp():
    """Get timestamp of the most recently modified JSON file."""
    data_path = Path('data')
    if not data_path.exists():
        return None
    
    json_files = list(data_path.rglob('output_*.json'))
    if not json_files:
        return None
    
    latest = max(json_files, key=lambda f: f.stat().st_mtime)
    mtime = latest.stat().st_mtime
    return datetime.fromtimestamp(mtime)


def validate_stat(stat):
    """Validate stats against actual file counts. Returns issues list."""
    issues = []
    stat_time = None
    
    try:
        stat_time = datetime.fromisoformat(stat.get('timestamp', ''))
    except:
        return issues
    
    # Validate Stage 2 stats
    if 'parsed_jobs' in stat and 'new_jobs_found' not in stat:
        json_count = count_json_files()
        logged_parsed = stat.get('parsed_jobs', 0)
        
        # Check if there are JSON files but logged count doesn't match
        if json_count > 0 and logged_parsed == 0:
            issues.append(f"⚠️  Stage 2 logged 0 jobs but found {json_count} JSON files")
    
    # Validate Stage 3 stats
    if 'new_jobs_found' in stat:
        actual_job_pages = count_job_pages()
        logged_downloaded = stat.get('jobs_downloaded', 0)
        
        # Check if download count doesn't match actual files
        if logged_downloaded > 0 and logged_downloaded != actual_job_pages:
            issues.append(f"⚠️  Stage 3 logged {logged_downloaded} downloads but {actual_job_pages} job files exist")
        
        # Check if success count doesn't match actual downloads in recent window
        logged_success = stat.get('download_successful', 0)
        if logged_success > 0 and logged_success > actual_job_pages:
            issues.append(f"⚠️  Stage 3 logged {logged_success} successful downloads but only {actual_job_pages} files exist")
    
    return issues


def print_single_stat(stat, validate=False):
    """Pretty print a single stat entry."""
    print(f"\n{'='*70}")
    print(f"⏰ {format_timestamp(stat.get('timestamp', 'unknown'))}")
    
    # Check if this was a skipped run
    if stat.get('note') == 'skipped - recent cache found':
        print(f"{'='*70}")
        print("⏭️  SKIPPED (Recent cache found - no jobs to check)")
        return
    
    # Check if this is Stage 2 format (parsing stats only)
    if 'parsed_jobs' in stat and 'new_jobs_found' not in stat:
        print(f"{'='*70}")
        print(f"Parsed Jobs:       {stat.get('parsed_jobs', 0):>3}")
        if stat.get('note'):
            print(f"Note:              {stat['note']}")
    
    # Stage 3 format (downloading stats)
    elif 'new_jobs_found' in stat:
        print(f"{'='*70}")
        print(f"Jobs Found:        {stat.get('new_jobs_found', 0):>3}")
        print(f"Downloaded:        {stat.get('jobs_downloaded', 0):>3} ✓")
        print(f"  Success:         {stat.get('download_successful', 0):>3}")
        print(f"  Failed:          {stat.get('download_failed', 0):>3} ✗")
        print(f"Metadata:")
        print(f"  Generated:       {stat.get('metadata_generated', 0):>3} ✓")
        print(f"  Skipped:         {stat.get('metadata_skipped', 0):>3}")
        print(f"  Failed:          {stat.get('metadata_failed', 0):>3} ✗")
    
    # Unknown format - just show all fields
    else:
        print(f"{'='*70}")
        for key, value in stat.items():
            if key != 'timestamp':
                print(f"{key:.<30} {value}")
    
    # Show validation issues if requested
    if validate:
        issues = validate_stat(stat)
        if issues:
            print(f"{'─'*70}")
            for issue in issues:
                print(issue)


def main():
    """Main entry point."""
    num_runs = 10  # Show last 10 runs by default (like analyze_cron_stats.py)
    raw_mode = False
    validate_mode = False
    
    # Parse arguments
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--raw":
            raw_mode = True
        elif arg == "--validate":
            validate_mode = True
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
        # Show file counts if validating
        if validate_mode:
            print(f"\n{'='*70}")
            print("📊 Current File Counts")
            print(f"{'='*70}")
            print(f"JSON files:        {count_json_files():>3}")
            print(f"Job pages (HTML):  {count_job_pages():>3}")
            print()
        
        # Pretty print each stat
        for stat in selected_stats:
            print_single_stat(stat, validate=validate_mode)
        
        # Summary for multiple runs
        if len(selected_stats) > 1:
            print(f"\n{'='*70}")
            print("📊 Summary (Last {} Runs)".format(len(selected_stats)))
            print(f"{'='*70}")
            
            # Only include Stage 3 stats in summary
            stage3_stats = [s for s in selected_stats if 'new_jobs_found' in s]
            
            if stage3_stats:
                total_found = sum(s.get('new_jobs_found', 0) for s in stage3_stats)
                total_downloaded = sum(s.get('jobs_downloaded', 0) for s in stage3_stats)
                total_failed = sum(s.get('download_failed', 0) for s in stage3_stats)
                
                print(f"Total Jobs Found:   {total_found}")
                print(f"Total Downloaded:   {total_downloaded} ✓")
                print(f"Total Failed:       {total_failed} ✗")
                
                success_rate = 100*total_downloaded/(total_downloaded+total_failed) if (total_downloaded+total_failed)>0 else 0
                print(f"Success Rate:       {success_rate:.1f}%")
            else:
                print("No Stage 3 (download) statistics in selected range")
        
        print(f"\n{'='*70}\n")


if __name__ == '__main__':
    main()
