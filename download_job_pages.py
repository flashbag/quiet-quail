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
        logging.info(f"Downloading job {post_id}: {url}")
        
        # Download with timeout and headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        
        # Create directory structure: data/YYYY/MM/DD/
        date_parts = job_data['source_date'].split('/')
        if len(date_parts) >= 3:
            year, month, day = date_parts[0], date_parts[1], date_parts[2]
        else:
            now = datetime.now()
            year, month, day = now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")
        
        output_dir = os.path.join('data', year, month, day)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save with post_id as filename
        filename = f"job_{post_id}.html"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        logging.info(f"  ✓ Saved to {filepath}")
        return True, filepath
        
    except requests.exceptions.Timeout:
        logging.error(f"  ✗ Timeout downloading {url}")
        return False, None
    except requests.exceptions.RequestException as e:
        logging.error(f"  ✗ Error downloading {url}: {e}")
        return False, None
    except Exception as e:
        logging.error(f"  ✗ Unexpected error for {url}: {e}")
        return False, None


def main():
    """Main entry point."""
    print("=" * 60)
    print("Job Page Downloader")
    print("=" * 60)
    
    # Get new jobs
    new_jobs = get_new_jobs_from_json()
    
    if not new_jobs:
        logging.info("No new jobs to download")
        print("No new jobs to download")
        return
    
    # Download pages
    successful = 0
    failed = 0
    
    for idx, job in enumerate(new_jobs, 1):
        print(f"\n[{idx}/{len(new_jobs)}] Downloading: {job['position']} at {job['unit']}")
        success, filepath = download_job_page(job)
        
        if success:
            successful += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Download Summary:")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total: {len(new_jobs)}")
    print("=" * 60)


if __name__ == '__main__':
    main()
