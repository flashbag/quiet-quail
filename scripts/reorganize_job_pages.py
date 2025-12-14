#!/usr/bin/env python3
"""
Reorganize job pages from date-based to ID-based structure.
Move from: data/YYYY/MM/DD/job_{ID}.html
To: data/job-pages/{ID:3}/{ID:3}/{ID:3}/{ID}.html (three-level ID-based)
"""

import os
import shutil
from pathlib import Path
import json

DATA_DIR = Path(__file__).parent.parent / 'data'
JOB_PAGES_DIR = DATA_DIR / 'job-pages'

def get_id_path(job_id):
    """Create three-level directory path from ID."""
    id_str = str(job_id).zfill(6)  # Pad to 6 digits
    return JOB_PAGES_DIR / id_str[0:3] / id_str[3:6] / f"job_{job_id}.html"

def reorganize():
    """Move all job_*.html files to ID-based structure."""
    job_files = list(DATA_DIR.glob('*/*/*/job_*.html'))
    
    if not job_files:
        print("No job pages found")
        return
    
    print(f"Found {len(job_files)} job pages to reorganize")
    
    moved = 0
    errors = []
    
    for old_path in sorted(job_files):
        try:
            # Extract job ID from filename
            job_id = old_path.stem.replace('job_', '')
            
            # Get new path
            new_path = get_id_path(job_id)
            
            # Create directories
            new_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file
            if new_path.exists():
                print(f"  ⚠️  Already exists: {new_path.relative_to(DATA_DIR)}")
            else:
                shutil.move(str(old_path), str(new_path))
                moved += 1
                if moved % 50 == 0:
                    print(f"  [{moved}/{len(job_files)}] Moved...")
        
        except Exception as e:
            errors.append({'file': old_path, 'error': str(e)})
            print(f"  ❌ Error: {old_path}: {e}")
    
    print(f"\n✅ Reorganization complete:")
    print(f"   Moved: {moved}")
    print(f"   Errors: {len(errors)}")
    
    # Verify
    verify_count = len(list(JOB_PAGES_DIR.glob('*/*/*/job_*.html')))
    print(f"   Job pages in new location: {verify_count}")

if __name__ == '__main__':
    print("🔄 Reorganizing job pages from date-based to ID-based structure...\n")
    reorganize()
    print("\n✅ Done!")
