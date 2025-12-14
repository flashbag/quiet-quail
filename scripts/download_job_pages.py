#!/usr/bin/env python3
"""
Download individual job pages for new job postings.
Uses atomic file-based mechanism: if job_{ID}.html exists, it's already downloaded.
Stores downloaded pages in data/job-pages/{ID:3}/{ID:3}/ directory structure.
No central tracking file needed - file existence = downloaded.
"""

import os
import json
import logging
from pathlib import Path
import requests
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("download_jobs.log"),
        logging.StreamHandler()
    ]
)

def get_job_page_path(post_id):
    """Get canonical path for a job page based on ID."""
    id_str = str(post_id).zfill(6)
    return Path('data') / 'job-pages' / id_str[0:3] / id_str[3:6] / f"job_{post_id}.html"

def is_job_closed(post_id):
    """
    Check if a job posting is closed.
    A job is considered closed if the HTML contains the Ukrainian text:
    'На жаль, вакансія вже закрита!'
    
    Args:
        post_id: Job post ID
    
    Returns:
        True if job is closed, False otherwise
    """
    path = get_job_page_path(post_id)
    
    if not path.exists():
        return False
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Check for the Ukrainian "closed vacancy" message
            if 'На жаль, вакансія вже закрита!' in content:
                return True
    except Exception:
        pass
    
    return False

def is_already_downloaded(post_id):
    """
    Check if job page is already downloaded and valid.
    Verifies: file exists, is not empty, contains meta charset tag, and has valid HTML structure.
    
    Args:
        post_id: Job post ID
    
    Returns:
        True if file exists, not empty, has meta charset tag, and valid HTML structure
        False if file needs to be downloaded
    """
    path = get_job_page_path(post_id)
    
    # Check if file exists
    if not path.exists():
        return False
    
    # Check if file is not empty
    if path.stat().st_size == 0:
        return False
    
    # Check if file contains meta charset tag and valid HTML structure
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read(1000)  # Read first 1KB to check for markers
            # Check for both meta charset and DOCTYPE (indicates valid HTML)
            has_meta_charset = '<meta charset' in content
            has_html_structure = '<!DOCTYPE html>' in content or '<html' in content
            
            if has_meta_charset and has_html_structure:
                return True
    except Exception:
        pass
    
    return False


def get_new_jobs_from_json(json_base_dir='data'):
    """
    Extract all jobs from JSON files and identify new ones.
    Uses atomic file-existence check instead of tracking URLs.
    Returns list of job dicts for jobs that haven't been downloaded yet.
    Does NOT re-download if file exists and is valid.
    
    Args:
        json_base_dir: Base directory for JSON files
    """
    new_jobs = []
    
    json_path = Path(json_base_dir)
    if not json_path.exists():
        logging.warning(f"JSON directory {json_base_dir} does not exist")
        return new_jobs
    
    # Find all JSON files
    json_files = list(json_path.rglob('*.json'))
    logging.info(f"Found {len(json_files)} JSON files to check")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                posts = data.get('posts', [])
                
                for post in posts:
                    post_id = post.get('post_id')
                    url = post.get('url', '')
                    
                    # Only add if not already downloaded (atomic check)
                    if post_id and url and not is_already_downloaded(post_id):
                        new_jobs.append({
                            'post_id': post_id,
                            'url': url,
                            'position': post.get('position', 'Unknown'),
                            'unit': post.get('unit_name', 'Unknown'),
                            'source_date': json_file.parent.name
                        })
        except Exception as e:
            logging.warning(f"Error reading {json_file}: {e}")
    
    # Remove duplicates by post_id (keep first occurrence)
    unique_jobs = {}
    for job in new_jobs:
        if job['post_id'] not in unique_jobs:
            unique_jobs[job['post_id']] = job
    
    new_jobs = list(unique_jobs.values())
    logging.info(f"Found {len(new_jobs)} new job URLs to download")
    
    return new_jobs


def download_job_page(job_data):
    """
    Download individual job page.
    Returns (success: bool, file_path: str or None)
    """
    url = job_data['url']
    post_id = job_data['post_id']
    
    try:
        logging.debug(f"Downloading job {post_id}: {url}")
        
        # Download with shorter timeout and headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=5, headers=headers)
        response.raise_for_status()
        
        # Use the canonical path from get_job_page_path()
        output_path = get_job_page_path(post_id)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Check if job is closed
        if is_job_closed(post_id):
            logging.debug(f"  ✓ Saved job_{post_id} (⚠️ CLOSED)")
        else:
            logging.debug(f"  ✓ Saved job_{post_id}")
        
        return True, str(output_path)
        
    except requests.exceptions.Timeout:
        logging.debug(f"  ✗ Timeout: {post_id}")
        return False, None
    except requests.exceptions.RequestException as e:
        logging.debug(f"  ✗ Error {post_id}: {type(e).__name__}")
        return False, None
    except Exception as e:
        logging.debug(f"  ✗ Unexpected error for {post_id}: {type(e).__name__}")
        return False, None


def main():
    """Main entry point."""
    logging.info("=" * 60)
    logging.info("Job Page Downloader")
    logging.info("=" * 60)
    
    # Get new jobs
    new_jobs = get_new_jobs_from_json()
    
    if not new_jobs:
        logging.info("No new jobs to download")
        return
    
    # Limit to first 100 to avoid excessive downloads
    MAX_DOWNLOADS = 100
    jobs_to_download = new_jobs[:MAX_DOWNLOADS]
    
    if len(new_jobs) > MAX_DOWNLOADS:
        logging.info(f"Limiting downloads to {MAX_DOWNLOADS} jobs (found {len(new_jobs)} new jobs)")
    else:
        logging.info(f"Downloading {len(jobs_to_download)} new job pages")
    
    # Download pages with progress reporting
    successful = 0
    failed = 0
    
    for idx, job in enumerate(jobs_to_download, 1):
        progress_pct = (idx / len(jobs_to_download)) * 100
        logging.info(f"[{idx}/{len(jobs_to_download)} ({progress_pct:.0f}%)] {job['position'][:50]}")
        success, filepath = download_job_page(job)
        
        if success:
            successful += 1
        else:
            failed += 1
    
    logging.info("=" * 60)
    logging.info(f"Download Summary:")
    logging.info(f"  Successful: {successful}/{len(jobs_to_download)}")
    logging.info(f"  Failed: {failed}/{len(jobs_to_download)}")
    if len(new_jobs) > MAX_DOWNLOADS:
        logging.info(f"  Remaining: {len(new_jobs) - MAX_DOWNLOADS} jobs")
    logging.info("=" * 60)


if __name__ == '__main__':
    main()
