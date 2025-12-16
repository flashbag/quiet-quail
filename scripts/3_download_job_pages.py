#!/usr/bin/env python3
"""
Stage 3: Download individual job pages

Downloads the HTML for each job posting found in Stage 2 JSON output.
Stores in data/job-pages/{ID:3}/{ID:3}/job_ID.html
Also generates metadata JSON for each job.
"""

import json
import logging
import re
from pathlib import Path
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("download_jobs.log"),
        logging.StreamHandler()
    ]
)

def log_cron_stats(new_jobs_found, downloaded, successful, failed, gen_count, skip_count, fail_count):
    """Log cron run statistics to structured stats file."""
    stats_file = Path("logs/cron_stats.jsonl")
    stats_file.parent.mkdir(parents=True, exist_ok=True)
    
    stats = {
        "timestamp": datetime.now().isoformat(),
        "new_jobs_found": new_jobs_found,
        "jobs_downloaded": downloaded,
        "download_successful": successful,
        "download_failed": failed,
        "metadata_generated": gen_count,
        "metadata_skipped": skip_count,
        "metadata_failed": fail_count
    }
    
    try:
        with open(stats_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(stats, ensure_ascii=False) + "\n")
    except Exception as e:
        logging.error(f"Failed to write stats file: {e}")


def get_job_page_path(post_id):
    """Get canonical path for a job page based on ID."""
    id_str = str(post_id).zfill(6)
    return Path('data') / 'job-pages' / id_str[0:3] / id_str[3:6] / f"job_{post_id}.html"


def is_already_downloaded(post_id):
    """Check if job page already exists using atomic file check."""
    return get_job_page_path(post_id).exists()


def is_job_closed(post_id):
    """
    Check if a job posting is closed.
    A job is considered closed if the HTML contains:
    'На жаль, вакансія вже закрита!'
    """
    path = get_job_page_path(post_id)
    
    if not path.exists():
        return False
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'На жаль, вакансія вже закрита!' in content:
                return True
    except Exception:
        pass
    
    return False


def extract_main_content(html_content):
    """Extract main job posting content from HTML."""
    try:
        # Remove scripts and styles
        content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Try to find main article/content area
        patterns = [
            r'<main[^>]*>(.*?)</main>',
            r'<article[^>]*>(.*?)</article>',
            r'<div[^>]*class="[^"]*(?:content|main|posting|job)[^"]*"[^>]*>(.*?)</div>',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1)[:5000]  # First 5000 chars
        
        # Fallback: use first 5000 chars of body
        body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.IGNORECASE | re.DOTALL)
        if body_match:
            return body_match.group(1)[:5000]
        
        return content[:5000]
    except Exception as e:
        logging.debug(f"Error extracting content: {e}")
        return ""


def get_new_jobs_from_json():
    """Collect all job URLs from consolidated JSON file or all daily JSON files."""
    new_jobs = []
    
    # Try consolidated file first (more efficient, no duplicates)
    consolidated_path = Path('data/consolidated_unique.json')
    if consolidated_path.exists():
        logging.info("Using consolidated_unique.json")
        json_files = [consolidated_path]
    else:
        # Fallback to individual daily files
        base_path = Path('data')
        json_files = list(base_path.rglob('output_*.json'))
    
    if not json_files:
        logging.info("No JSON files found")
        return new_jobs
    
    logging.info(f"Found {len(json_files)} JSON file(s) to check")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                posts = data.get('posts', [])
                
                for post in posts:
                    post_id = post.get('post_id')
                    url = post.get('url', '')
                    
                    # Only add if not already downloaded
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
    
    # Remove duplicates by post_id
    unique_jobs = {}
    for job in new_jobs:
        if job['post_id'] not in unique_jobs:
            unique_jobs[job['post_id']] = job
    
    new_jobs = list(unique_jobs.values())
    logging.info(f"Found {len(new_jobs)} new job URLs to download")
    
    return new_jobs


def generate_all_job_metadata(skip_existing=True):
    """Generate metadata JSON files for all downloaded jobs."""
    job_pages_dir = Path('data') / 'job-pages'
    if not job_pages_dir.exists():
        return 0, 0, 0
    
    html_files = list(job_pages_dir.rglob('job_*.html'))
    if not html_files:
        return 0, 0, 0
    
    generated = 0
    skipped = 0
    failed = 0
    
    logging.debug(f"Generating metadata for {len(html_files)} jobs...")
    
    for html_file in html_files:
        try:
            post_id = int(html_file.stem.split('_')[1])
        except (ValueError, IndexError):
            failed += 1
            continue
        
        json_file = html_file.with_name(f"job_{post_id}.json")
        if json_file.exists() and skip_existing:
            skipped += 1
            continue
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            is_closed = is_job_closed(post_id)
            main_content = extract_main_content(html_content)
            
            metadata = {
                'post_id': post_id,
                'url': '',
                'position': 'Unknown',
                'unit_name': 'Unknown',
                'status': 'closed' if is_closed else 'open',
                'is_closed': is_closed,
                'content': main_content,
                'downloaded_at': str(int(html_file.stat().st_mtime))
            }
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            generated += 1
        except Exception as e:
            logging.debug(f"Failed to generate metadata for job {post_id}: {e}")
            failed += 1
    
    return generated, skipped, failed


def download_job_page(job_data):
    """Download individual job page and create metadata JSON."""
    url = job_data['url']
    post_id = job_data['post_id']
    
    try:
        logging.debug(f"Downloading job {post_id}: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=5, headers=headers)
        response.raise_for_status()
        
        # Get canonical path
        output_path = get_job_page_path(post_id)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Check if job is closed
        is_closed = is_job_closed(post_id)
        main_content = extract_main_content(response.text)
        
        # Create metadata JSON file
        metadata = {
            'post_id': post_id,
            'url': url,
            'position': job_data.get('position', 'Unknown'),
            'unit_name': job_data.get('unit', 'Unknown'),
            'status': 'closed' if is_closed else 'open',
            'is_closed': is_closed,
            'content': main_content,
            'downloaded_at': str(Path(output_path).stat().st_mtime)
        }
        
        json_path = output_path.with_name(f"job_{post_id}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        if is_closed:
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
    
    logging.info("=" * 70)
    logging.info("STAGE 3: Downloading individual job pages")
    logging.info("=" * 70)
    
    # Get new jobs
    new_jobs = get_new_jobs_from_json()
    new_jobs_found = len(new_jobs)
    
    if not new_jobs:
        logging.info("✓ No new jobs to download")
        log_cron_stats(0, 0, 0, 0, 0, 0, 0)
        logging.info("STAGE 3 Complete\n")
        return
    
    # Limit to 100 downloads per run
    MAX_DOWNLOADS = 100
    jobs_to_download = new_jobs[:MAX_DOWNLOADS]
    
    if len(new_jobs) > MAX_DOWNLOADS:
        logging.info(f"Limiting to {MAX_DOWNLOADS} jobs (found {len(new_jobs)} new jobs)")
    else:
        logging.info(f"Downloading {len(jobs_to_download)} new job pages")
    
    # Download pages with progress
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
    
    logging.info("=" * 70)
    logging.info(f"Download Summary:")
    logging.info(f"  Found: {new_jobs_found}")
    logging.info(f"  Downloaded: {successful}/{len(jobs_to_download)} ✓")
    logging.info(f"  Failed: {failed}/{len(jobs_to_download)} ✗")
    if len(new_jobs) > MAX_DOWNLOADS:
        logging.info(f"  Remaining: {len(new_jobs) - MAX_DOWNLOADS}")
    
    # Generate metadata for all jobs
    logging.info("Generating/updating metadata files...")
    gen_count, skip_count, fail_count = generate_all_job_metadata(skip_existing=True)
    logging.info(f"Metadata Summary:")
    logging.info(f"  Generated: {gen_count} ✓")
    logging.info(f"  Skipped: {skip_count}")
    logging.info(f"  Failed: {fail_count} ✗")
    logging.info("=" * 70)
    
    # Log statistics
    log_cron_stats(new_jobs_found, successful, successful, failed, gen_count, skip_count, fail_count)
    logging.info("STAGE 3 Complete\n")


if __name__ == '__main__':
    main()
