#!/usr/bin/env python3
"""
General Summary - Complete system overview

Shows:
- Latest 10 cron runs (aggregated statistics)
- All counters (JSON files, job pages, metadata files)
- Last updated timestamps for each component
- Details of the newest downloaded job

Usage:
    python3 tools/summary.py              # Display full summary
    python3 tools/summary.py --raw        # Raw JSON output
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def read_stats_file():
    """Read all stats from JSONL file."""
    stats_file = Path("logs/cron_stats.jsonl")
    
    if not stats_file.exists():
        return []
    
    stats = []
    try:
        with open(stats_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        stat = json.loads(line)
                        stats.append(stat)
                    except json.JSONDecodeError:
                        pass
    except Exception:
        pass
    
    return stats


def count_files():
    """Count all files in the system."""
    counts = {
        "json_files": 0,
        "job_pages_html": 0,
        "job_pages_json": 0,
    }
    
    # Count JSON files
    data_path = Path('data')
    if data_path.exists():
        counts['json_files'] = len(list(data_path.rglob('output_*.json')))
    
    # Count job page files
    job_pages_path = Path('data/job-pages')
    if job_pages_path.exists():
        counts['job_pages_html'] = len(list(job_pages_path.rglob('job_*.html')))
        counts['job_pages_json'] = len(list(job_pages_path.rglob('job_*.json')))
    
    return counts


def get_last_timestamps():
    """Get last modified timestamps for key components."""
    timestamps = {
        "last_html_main": None,
        "last_json_parsed": None,
        "last_job_page": None,
    }
    
    # Latest main page HTML
    data_path = Path('data')
    if data_path.exists():
        html_files = list(data_path.rglob('output_*.html'))
        if html_files:
            latest = max(html_files, key=lambda f: f.stat().st_mtime)
            timestamps['last_html_main'] = datetime.fromtimestamp(latest.stat().st_mtime)
        
        # Latest parsed JSON
        json_files = list(data_path.rglob('output_*.json'))
        if json_files:
            latest = max(json_files, key=lambda f: f.stat().st_mtime)
            timestamps['last_json_parsed'] = datetime.fromtimestamp(latest.stat().st_mtime)
    
    # Latest job page
    job_pages_path = Path('data/job-pages')
    if job_pages_path.exists():
        job_files = list(job_pages_path.rglob('job_*.html'))
        if job_files:
            latest = max(job_files, key=lambda f: f.stat().st_mtime)
            timestamps['last_job_page'] = datetime.fromtimestamp(latest.stat().st_mtime)
    
    return timestamps


def get_newest_job():
    """Get the most recently downloaded job with its metadata."""
    job_pages_path = Path('data/job-pages')
    
    if not job_pages_path.exists():
        return None
    
    job_files = list(job_pages_path.rglob('job_*.json'))
    if not job_files:
        return None
    
    # Get the most recently modified job
    newest_job_file = max(job_files, key=lambda f: f.stat().st_mtime)
    
    try:
        with open(newest_job_file, 'r', encoding='utf-8') as f:
            job_data = json.load(f)
            job_data['file_path'] = str(newest_job_file)
            job_data['modified_at'] = datetime.fromtimestamp(newest_job_file.stat().st_mtime)
            return job_data
    except Exception:
        return None


def format_timestamp(dt):
    """Format datetime object."""
    if dt is None:
        return "Never"
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def aggregate_cron_stats(stats, num_runs=10):
    """Aggregate the latest N cron runs."""
    if not stats:
        return None
    
    latest_stats = stats[-num_runs:]
    
    agg = {
        "runs_count": len(latest_stats),
        "total_parsed_jobs": 0,
        "total_new_jobs_found": 0,
        "total_downloaded": 0,
        "total_successful": 0,
        "total_failed": 0,
        "total_metadata_generated": 0,
        "total_metadata_skipped": 0,
        "total_metadata_failed": 0,
        "first_run": None,
        "last_run": None,
    }
    
    stage2_count = 0
    stage3_count = 0
    
    for stat in latest_stats:
        # Track timestamps
        if 'timestamp' in stat:
            ts = datetime.fromisoformat(stat['timestamp'])
            if agg['first_run'] is None:
                agg['first_run'] = ts
            agg['last_run'] = ts
        
        # Stage 2 stats
        if 'parsed_jobs' in stat:
            agg['total_parsed_jobs'] += stat.get('parsed_jobs', 0)
            stage2_count += 1
        
        # Stage 3 stats
        if 'new_jobs_found' in stat:
            agg['total_new_jobs_found'] += stat.get('new_jobs_found', 0)
            agg['total_downloaded'] += stat.get('jobs_downloaded', 0)
            agg['total_successful'] += stat.get('download_successful', 0)
            agg['total_failed'] += stat.get('download_failed', 0)
            agg['total_metadata_generated'] += stat.get('metadata_generated', 0)
            agg['total_metadata_skipped'] += stat.get('metadata_skipped', 0)
            agg['total_metadata_failed'] += stat.get('metadata_failed', 0)
            stage3_count += 1
    
    agg['stage2_runs'] = stage2_count
    agg['stage3_runs'] = stage3_count
    
    return agg


def print_summary(stats, counts, timestamps, newest_job):
    """Print formatted summary."""
    
    print(f"\n{'='*80}")
    print(f"{'QUIET-QUAIL SYSTEM SUMMARY':^80}")
    print(f"{'='*80}\n")
    
    # Cron Stats Summary
    print(f"{'─'*80}")
    print(f"📊 CRON STATISTICS (Last 10 Runs)")
    print(f"{'─'*80}")
    
    agg = aggregate_cron_stats(stats, num_runs=10)
    
    if agg:
        print(f"  Runs Analyzed:         {agg['runs_count']}")
        print(f"  Period:                {format_timestamp(agg['first_run'])} to {format_timestamp(agg['last_run'])}")
        print()
        print(f"  📝 Stage 2 (Parsing):")
        print(f"    - Completed:       {agg['stage2_runs']} runs")
        print(f"    - Total Parsed:    {agg['total_parsed_jobs']} jobs")
        print()
        print(f"  📥 Stage 3 (Downloading):")
        print(f"    - Completed:       {agg['stage3_runs']} runs")
        print(f"    - New Found:       {agg['total_new_jobs_found']} jobs")
        print(f"    - Downloaded:      {agg['total_downloaded']} ✓")
        print(f"      - Successful:    {agg['total_successful']}")
        print(f"      - Failed:        {agg['total_failed']}")
        if agg['total_downloaded'] > 0:
            success_rate = 100 * agg['total_successful'] / agg['total_downloaded']
            print(f"      - Success Rate:  {success_rate:.1f}%")
        print()
        print(f"  📋 Metadata:")
        print(f"    - Generated:       {agg['total_metadata_generated']}")
        print(f"    - Skipped:         {agg['total_metadata_skipped']}")
        print(f"    - Failed:          {agg['total_metadata_failed']}")
    else:
        print("  No cron statistics available")
    
    # File Counts
    print(f"\n{'─'*80}")
    print(f"📁 FILE COUNTERS")
    print(f"{'─'*80}")
    
    print(f"  JSON Files (parsed pages):     {counts['json_files']:>6}")
    print(f"  Job Pages (HTML):              {counts['job_pages_html']:>6}")
    print(f"  Job Metadata (JSON):           {counts['job_pages_json']:>6}")
    print(f"  Total Job Objects:             {counts['job_pages_html']:>6}")
    
    # Last Updated
    print(f"\n{'─'*80}")
    print(f"⏱️  LAST UPDATED")
    print(f"{'─'*80}")
    
    print(f"  Main Page HTML:     {format_timestamp(timestamps['last_html_main'])}")
    print(f"  Parsed JSON:        {format_timestamp(timestamps['last_json_parsed'])}")
    print(f"  Job Page:           {format_timestamp(timestamps['last_job_page'])}")
    
    if agg and agg['last_run']:
        print(f"  Cron Stats:         {format_timestamp(agg['last_run'])}")
    
    # Newest Job
    print(f"\n{'─'*80}")
    print(f"⭐ NEWEST JOB")
    print(f"{'─'*80}")
    
    if newest_job:
        print(f"  ID:                {newest_job.get('post_id', 'N/A')}")
        print(f"  Position:          {newest_job.get('position', 'Unknown')[:60]}")
        print(f"  Unit:              {newest_job.get('unit_name', 'Unknown')[:60]}")
        print(f"  URL:               {newest_job.get('url', 'N/A')[:70]}")
        print(f"  Status:            {newest_job.get('status', 'unknown').upper()}")
        print(f"  Downloaded:        {format_timestamp(newest_job['modified_at'])}")
        print(f"  File Path:         {newest_job['file_path']}")
        
        if newest_job.get('content'):
            content_preview = newest_job['content'][:150].replace('\n', ' ')
            print(f"  Content Preview:   {content_preview}...")
    else:
        print("  No job data available")
    
    print(f"\n{'='*80}\n")


def main():
    """Main entry point."""
    raw_mode = "--raw" in sys.argv
    
    stats = read_stats_file()
    counts = count_files()
    timestamps = get_last_timestamps()
    newest_job = get_newest_job()
    
    if raw_mode:
        output = {
            "cron_stats": stats[-10:] if stats else [],
            "file_counts": counts,
            "last_updated": {
                "last_html_main": format_timestamp(timestamps['last_html_main']),
                "last_json_parsed": format_timestamp(timestamps['last_json_parsed']),
                "last_job_page": format_timestamp(timestamps['last_job_page']),
            },
            "newest_job": newest_job,
            "aggregated_stats": aggregate_cron_stats(stats, 10)
        }
        print(json.dumps(output, ensure_ascii=False, indent=2, default=str))
    else:
        print_summary(stats, counts, timestamps, newest_job)


if __name__ == '__main__':
    main()
