#!/usr/bin/env python3
"""
Consolidate all parsed jobs into a single deduplicated file.

Reads all output_*.json files and creates a consolidated file with unique jobs only.
Maintains order by first appearance.

Usage:
    python3 tools/consolidate_jobs.py              # Generate consolidated file
    python3 tools/consolidate_jobs.py --force      # Overwrite existing
    python3 tools/consolidate_jobs.py --stats      # Show statistics
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def read_all_parsed_jobs():
    """Read all jobs from output_*.json files."""
    all_jobs = []
    unique_by_id = {}
    source_count = defaultdict(int)
    
    # Find all JSON files
    data_path = Path('data')
    json_files = sorted(data_path.rglob('output_*.json'))
    
    if not json_files:
        print("No JSON files found in data/")
        return [], {}
    
    print(f"📖 Reading {len(json_files)} JSON files...")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                posts = data.get('posts', [])
                
                for post in posts:
                    post_id = post.get('post_id')
                    if post_id and post_id not in unique_by_id:
                        unique_by_id[post_id] = post
                        all_jobs.append(post)
                        source_count[post_id] = 1
                    elif post_id:
                        source_count[post_id] += 1
                        
        except Exception as e:
            print(f"⚠️  Error reading {json_file}: {e}")
    
    return all_jobs, source_count


def generate_consolidated_file(jobs):
    """Generate consolidated JSON file."""
    consolidated = {
        "generated_at": datetime.now().isoformat(),
        "total_unique_jobs": len(jobs),
        "posts": jobs
    }
    
    output_file = Path('data/consolidated_unique.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(consolidated, f, ensure_ascii=False, indent=2)
    
    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"✓ Consolidated file created: {output_file}")
    print(f"  - Size: {file_size_mb:.2f} MB")
    print(f"  - Jobs: {len(jobs):,}")
    
    return output_file


def main():
    """Main entry point."""
    force = "--force" in sys.argv
    show_stats = "--stats" in sys.argv
    
    consolidated_file = Path('data/consolidated_unique.json')
    
    # Check if file exists
    if consolidated_file.exists() and not force:
        print(f"📁 Consolidated file already exists: {consolidated_file}")
        print("Use --force to overwrite")
        
        if show_stats:
            with open(consolidated_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"\nStats:")
                print(f"  Total jobs: {data.get('total_unique_jobs', 0):,}")
                print(f"  Generated: {data.get('generated_at', 'unknown')}")
        
        return
    
    # Read all jobs
    jobs, source_count = read_all_parsed_jobs()
    
    if not jobs:
        print("No jobs found to consolidate")
        return
    
    # Show statistics
    if show_stats:
        total_sources = sum(source_count.values())
        duplicates = total_sources - len(jobs)
        print(f"\nStatistics:")
        print(f"  Total job mentions: {total_sources:,}")
        print(f"  Unique jobs: {len(jobs):,}")
        print(f"  Duplicates removed: {duplicates:,}")
        print(f"  Dedup ratio: {100 * duplicates / total_sources:.1f}%")
    
    # Generate file
    generate_consolidated_file(jobs)
    
    if show_stats:
        # Find most duplicated jobs
        top_dup = sorted([(id, count) for id, count in source_count.items()], 
                        key=lambda x: x[1], reverse=True)[:5]
        
        if top_dup and top_dup[0][1] > 1:
            print(f"\nMost duplicated jobs:")
            for job_id, count in top_dup:
                job = next((j for j in jobs if j.get('post_id') == job_id), {})
                position = job.get('position', 'Unknown')[:50]
                print(f"  - {job_id}: {position} (found {count} times)")


if __name__ == '__main__':
    main()
