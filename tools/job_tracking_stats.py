#!/usr/bin/env python3
"""
Track detailed statistics for each unique job posting.
Shows: when appeared, times appeared in different scrapes, when disappeared, status changes.
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def parse_date_from_path(file_path):
    """Extract date from file path like 'saved_json/2025/12/10/output_20251210_202928.json'"""
    parts = file_path.split('/')
    if len(parts) >= 4:
        year, month, day = parts[1], parts[2], parts[3]
        return f"{year}-{month}-{day}"
    return "unknown"


def track_jobs():
    """Track all job postings across time."""
    
    job_timeline = defaultdict(list)  # post_id -> [(date, status, position, unit)]
    
    saved_json_dir = Path('saved_json')
    
    if not saved_json_dir.exists():
        print("No saved_json directory found")
        return
    
    json_files = sorted(saved_json_dir.rglob('*.json'))
    
    # Skip consolidated_unique.json - we need the dated files
    json_files = [f for f in json_files if 'consolidated' not in str(f)]
    
    print(f"Processing {len(json_files)} dated JSON files...\n")
    
    # Load all posts and track timeline
    for json_file in json_files:
        date = parse_date_from_path(str(json_file))
        
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                for post in data.get('posts', []):
                    post_id = post.get('post_id')
                    if post_id:
                        job_timeline[post_id].append({
                            'date': date,
                            'status': post.get('status', 'unknown'),
                            'position': post.get('position', 'N/A'),
                            'unit': post.get('unit_name', 'N/A'),
                            'file': str(json_file)
                        })
        except Exception as e:
            print(f"Error reading {json_file}: {e}")
    
    # Analyze and display statistics
    print("=" * 100)
    print("DETAILED JOB TRACKING STATISTICS")
    print("=" * 100)
    print()
    
    # Get sorted list of unique jobs
    sorted_jobs = sorted(job_timeline.items(), key=lambda x: len(x[1]), reverse=True)
    
    print(f"Total unique jobs tracked: {len(sorted_jobs)}\n")
    
    # Display each job with full timeline
    for idx, (post_id, occurrences) in enumerate(sorted_jobs, 1):
        position = occurrences[0]['position']
        unit = occurrences[0]['unit']
        
        # Extract timeline info
        first_date = occurrences[0]['date']
        last_date = occurrences[-1]['date']
        appearances = len(occurrences)
        
        # Track status changes
        status_timeline = []
        for occ in occurrences:
            status_timeline.append(occ['status'])
        
        unique_statuses = set(status_timeline)
        status_changes = []
        prev_status = None
        for status in status_timeline:
            if status != prev_status:
                status_changes.append(status)
                prev_status = status
        
        # Display
        print(f"\n{idx}. Post ID: {post_id}")
        print(f"   Position: {position}")
        print(f"   Unit: {unit}")
        print(f"   First appeared: {first_date}")
        print(f"   Last seen: {last_date}")
        print(f"   Times appeared in scrapes: {appearances}")
        print(f"   Status: {' → '.join(status_changes) if status_changes else 'unknown'}")
        
        # Show detailed timeline for jobs that changed status or appeared less frequently
        if len(unique_statuses) > 1 or appearances <= 5:
            print(f"   Timeline:")
            for i, occ in enumerate(occurrences, 1):
                print(f"      {i}. {occ['date']}: {occ['status'].upper()}")


def generate_csv_report():
    """Generate a CSV report of job tracking data."""
    
    job_timeline = defaultdict(list)
    
    saved_json_dir = Path('saved_json')
    
    if not saved_json_dir.exists():
        return
    
    json_files = sorted(saved_json_dir.rglob('*.json'))
    json_files = [f for f in json_files if 'consolidated' not in str(f)]
    
    # Load data
    for json_file in json_files:
        date = parse_date_from_path(str(json_file))
        
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                for post in data.get('posts', []):
                    post_id = post.get('post_id')
                    if post_id:
                        job_timeline[post_id].append({
                            'date': date,
                            'status': post.get('status', 'unknown'),
                            'position': post.get('position', 'N/A'),
                            'unit': post.get('unit_name', 'N/A')
                        })
        except Exception as e:
            pass
    
    # Write CSV
    csv_file = Path('job_tracking_report.csv')
    
    with open(csv_file, 'w') as f:
        f.write('Post_ID,Position,Unit,First_Date,Last_Date,Appearances,Status_History\n')
        
        for post_id, occurrences in sorted(job_timeline.items(), key=lambda x: len(x[1]), reverse=True):
            position = occurrences[0]['position'].replace(',', ';')  # Escape commas
            unit = occurrences[0]['unit'].replace(',', ';')
            first_date = occurrences[0]['date']
            last_date = occurrences[-1]['date']
            appearances = len(occurrences)
            
            status_history = ' → '.join([occ['status'] for occ in occurrences])
            
            f.write(f'"{post_id}","{position}","{unit}",{first_date},{last_date},{appearances},"{status_history}"\n')
    
    print(f"\n✓ CSV report saved to: {csv_file}")
    return csv_file


def summary_statistics():
    """Display summary statistics."""
    
    job_timeline = defaultdict(list)
    
    saved_json_dir = Path('saved_json')
    json_files = sorted(saved_json_dir.rglob('*.json'))
    json_files = [f for f in json_files if 'consolidated' not in str(f)]
    
    # Load data
    for json_file in json_files:
        date = parse_date_from_path(str(json_file))
        
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                for post in data.get('posts', []):
                    post_id = post.get('post_id')
                    if post_id:
                        job_timeline[post_id].append({
                            'date': date,
                            'status': post.get('status', 'unknown')
                        })
        except Exception as e:
            pass
    
    # Calculate statistics
    all_appearances = [len(v) for v in job_timeline.values()]
    
    print("\n" + "=" * 100)
    print("SUMMARY STATISTICS")
    print("=" * 100)
    print(f"\nTotal unique jobs: {len(job_timeline)}")
    print(f"Average appearances per job: {sum(all_appearances) / len(all_appearances):.1f}")
    print(f"Jobs appearing in all scrapes: {sum(1 for v in job_timeline.values() if len(v) == len(json_files))}")
    print(f"Jobs appearing once: {sum(1 for v in job_timeline.values() if len(v) == 1)}")
    print(f"Jobs that disappeared (appeared then closed/removed): {sum(1 for v in job_timeline.values() if v[-1]['status'] == 'closed')}")
    
    # Date range
    all_dates = []
    for occurrences in job_timeline.values():
        for occ in occurrences:
            all_dates.append(occ['date'])
    
    if all_dates:
        print(f"Data range: {min(all_dates)} to {max(all_dates)}")
    
    print()


if __name__ == '__main__':
    track_jobs()
    summary_statistics()
    generate_csv_report()
