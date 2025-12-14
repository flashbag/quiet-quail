#!/usr/bin/env python3
"""
Migrate saved_html, saved_json, and job_pages to unified data/ directory.
"""

import os
import shutil
from pathlib import Path

def migrate():
    """Migrate all data to unified data/ directory."""
    
    print("=" * 60)
    print("Migrating to unified data/ directory")
    print("=" * 60)
    
    # Ensure data directory exists
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    # Migrate saved_html
    saved_html = Path('saved_html')
    if saved_html.exists():
        print("\nMigrating saved_html/...")
        for item in saved_html.rglob('*'):
            if item.is_file():
                # Calculate relative path
                rel_path = item.relative_to(saved_html)
                dest = data_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)
                print(f"  ✓ {rel_path}")
        print(f"Backed up: saved_html -> saved_html_backup")
        if Path('saved_html_backup').exists():
            shutil.rmtree('saved_html_backup')
        shutil.copytree(saved_html, 'saved_html_backup')
        shutil.rmtree(saved_html)
        print(f"  ✓ Removed original saved_html/")
    
    # Migrate saved_json
    saved_json = Path('saved_json')
    if saved_json.exists():
        print("\nMigrating saved_json/...")
        for item in saved_json.rglob('*'):
            if item.is_file():
                # Calculate relative path
                rel_path = item.relative_to(saved_json)
                dest = data_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)
                print(f"  ✓ {rel_path}")
        print(f"Backed up: saved_json -> saved_json_backup")
        if Path('saved_json_backup').exists():
            shutil.rmtree('saved_json_backup')
        shutil.copytree(saved_json, 'saved_json_backup')
        shutil.rmtree(saved_json)
        print(f"  ✓ Removed original saved_json/")
    
    # Migrate job_pages if it exists
    job_pages = Path('job_pages')
    if job_pages.exists():
        print("\nMigrating job_pages/...")
        for item in job_pages.rglob('*'):
            if item.is_file():
                # Calculate relative path
                rel_path = item.relative_to(job_pages)
                dest = data_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)
                print(f"  ✓ {rel_path}")
        print(f"Backed up: job_pages -> job_pages_backup")
        if Path('job_pages_backup').exists():
            shutil.rmtree('job_pages_backup')
        shutil.copytree(job_pages, 'job_pages_backup')
        shutil.rmtree(job_pages)
        print(f"  ✓ Removed original job_pages/")
    
    print("\n" + "=" * 60)
    print("Migration complete!")
    print(f"All data consolidated in: {data_dir.absolute()}")
    print("\nBackups created:")
    for backup in ['saved_html_backup', 'saved_json_backup', 'job_pages_backup']:
        if Path(backup).exists():
            print(f"  - {backup}")
    print("=" * 60)

if __name__ == '__main__':
    migrate()
