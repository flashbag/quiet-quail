#!/usr/bin/env python3
"""
Generate metadata JSON files for all downloaded job pages.
This creates job_*.json files alongside job_*.html files.

Useful for:
- Backfilling metadata for jobs downloaded before the metadata feature
- Re-generating metadata if something goes wrong
- One-time initialization for better performance

Usage:
    python3 scripts/generate_job_metadata.py              # Generate for all jobs
    python3 scripts/generate_job_metadata.py --force      # Overwrite existing metadata
    python3 scripts/generate_job_metadata.py --help       # Show help
"""

import os
import json
import logging
import sys
import re
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("generate_metadata.log"),
        logging.StreamHandler()
    ]
)


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
            r'<section[^>]*>(.*?)</section>',
        ]
        
        main_content = None
        for pattern in patterns:
            match = re.search(pattern, content, flags=re.DOTALL | re.IGNORECASE)
            if match:
                main_content = match.group(1)
                break
        
        # Fallback: find the largest div
        if not main_content:
            divs = re.findall(r'<div[^>]*>(.*?)</div>', content, flags=re.DOTALL | re.IGNORECASE)
            if divs:
                main_content = max(divs, key=len)
        
        # Last resort: use body content
        if not main_content:
            body_match = re.search(r'<body[^>]*>(.*?)</body>', content, flags=re.DOTALL | re.IGNORECASE)
            if body_match:
                main_content = body_match.group(1)
            else:
                main_content = html_content
        
        # Clean up: remove navigation, footer, headers, sidebars
        main_content = re.sub(r'<nav[^>]*>.*?</nav>', '', main_content, flags=re.DOTALL | re.IGNORECASE)
        main_content = re.sub(r'<footer[^>]*>.*?</footer>', '', main_content, flags=re.DOTALL | re.IGNORECASE)
        main_content = re.sub(r'<header[^>]*>.*?</header>', '', main_content, flags=re.DOTALL | re.IGNORECASE)
        main_content = re.sub(r'<aside[^>]*>.*?</aside>', '', main_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove common non-content elements
        main_content = re.sub(r'<div[^>]*class="[^"]*(?:sidebar|nav|menu|ad)[^"]*"[^>]*>.*?</div>', '', main_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Clean up excessive whitespace
        main_content = re.sub(r'\s+', ' ', main_content)
        main_content = main_content.strip()
        
        return main_content[:50000] if main_content else ""
    except Exception as e:
        logging.debug(f"Error extracting content: {e}")
        return ""


def is_job_closed(html_content):
    """Check if job is closed based on HTML content."""
    return 'На жаль, вакансія вже закрита!' in html_content


def generate_metadata(post_id, html_file):
    """Generate metadata for a job HTML file."""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        is_closed = is_job_closed(html_content)
        main_content = extract_main_content(html_content)
        
        metadata = {
            'post_id': int(post_id),
            'url': '',
            'position': 'Unknown',
            'unit_name': 'Unknown',
            'status': 'closed' if is_closed else 'open',
            'is_closed': is_closed,
            'content': main_content,
            'downloaded_at': str(int(html_file.stat().st_mtime))
        }
        
        return metadata
    except Exception as e:
        logging.error(f"Error generating metadata for job {post_id}: {e}")
        return None


def main():
    """Generate metadata for all downloaded jobs."""
    force_overwrite = '--force' in sys.argv
    
    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        sys.exit(0)
    
    # Find all job HTML files
    job_pages_dir = Path('data') / 'job-pages'
    if not job_pages_dir.exists():
        logging.error(f"Job pages directory not found: {job_pages_dir}")
        sys.exit(1)
    
    html_files = sorted(job_pages_dir.rglob('job_*.html'))
    logging.info(f"Found {len(html_files)} job HTML files")
    
    if not html_files:
        logging.warning("No job HTML files found")
        sys.exit(0)
    
    generated = 0
    skipped = 0
    failed = 0
    
    for idx, html_file in enumerate(html_files, 1):
        # Extract post_id from filename
        try:
            post_id = int(html_file.stem.split('_')[1])
        except (ValueError, IndexError):
            logging.warning(f"Could not extract post_id from {html_file.name}")
            failed += 1
            continue
        
        # Check if metadata JSON already exists
        json_file = html_file.with_name(f"job_{post_id}.json")
        if json_file.exists() and not force_overwrite:
            skipped += 1
            continue
        
        # Generate metadata
        metadata = generate_metadata(post_id, html_file)
        if not metadata:
            failed += 1
            continue
        
        # Write metadata JSON
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            generated += 1
            
            # Log progress
            progress_pct = (idx / len(html_files)) * 100
            status = "CLOSED" if metadata['is_closed'] else "open"
            logging.debug(f"[{idx}/{len(html_files)} ({progress_pct:.0f}%)] Generated metadata for job_{post_id} ({status})")
        except Exception as e:
            logging.error(f"Failed to write metadata for job {post_id}: {e}")
            failed += 1
    
    # Summary
    logging.info("=" * 60)
    logging.info("Metadata Generation Summary:")
    logging.info(f"  Generated: {generated}")
    logging.info(f"  Skipped: {skipped}")
    logging.info(f"  Failed: {failed}")
    logging.info(f"  Total: {len(html_files)}")
    logging.info("=" * 60)


if __name__ == '__main__':
    main()
