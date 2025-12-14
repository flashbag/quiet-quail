#!/usr/bin/env python3
"""
Download individual job pages for new job postings.
Only downloads if the URL hasn't been downloaded before.
Stores downloaded pages in job_pages/ directory structure.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
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

# File to track downloaded URLs
DOWNLOADED_URLS_FILE = "downloaded_urls.json"

def load_downloaded_urls():
    """Load set of already downloaded URLs from file."""
    if os.path.exists(DOWNLOADED_URLS_FILE):
        try:
            with open(DOWNLOADED_URLS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('urls', []))
        except Exception as e:
            logging.warning(f"Could not load downloaded URLs file: {e}")
            return set()
    return set()


def save_downloaded_urls(urls):
    """Save set of downloaded URLs to file."""
    try:
        with open(DOWNLOADED_URLS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'urls': list(urls), 'last_updated': datetime.now().isoformat()}, f)
    except Exception as e:
        logging.error(f"Could not save downloaded URLs file: {e}")


def get_new_jobs_from_json(json_base_dir='data'):
    """
    Extract all jobs from JSON files and identify new ones.
    Returns list of (post_id, url, job_data) tuples for new jobs.
    """
    downloaded_urls = load_downloaded_urls()
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
                    url = post.get('url', '')
                    if url and url not in downloaded_urls:
                        new_jobs.append({
                            'post_id': post.get('post_id'),
                            'url': url,
                            'position': post.get('position', 'Unknown'),
                            'unit': post.get('unit_name', 'Unknown'),
                            'source_date': json_file.parent.name
                        })
                        downloaded_urls.add(url)
        except Exception as e:
            logging.warning(f"Error reading {json_file}: {e}")
    
    # Remove duplicates (keep first occurrence)
    unique_jobs = {}
    for job in new_jobs:
        if job['url'] not in unique_jobs:
            unique_jobs[job['url']] = job
    
    new_jobs = list(unique_jobs.values())
    logging.info(f"Found {len(new_jobs)} new job URLs to download")
    
    # Save updated downloaded URLs
    save_downloaded_urls(downloaded_urls)
    
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
        
        # Create ID-based directory structure: data/job-pages/{ID:3}/{ID:3}/
        id_str = str(post_id).zfill(6)
        output_dir = os.path.join('data', 'job-pages', id_str[0:3], id_str[3:6])
        os.makedirs(output_dir, exist_ok=True)
        
        # Save with post_id as filename
        filename = f"job_{post_id}.html"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        logging.debug(f"  ✓ Saved job_{post_id}")
        return True, filepath
        
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
