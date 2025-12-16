#!/usr/bin/env python3
"""
Stage 2: Parse HTML to JSON

Extracts job postings from the HTML files downloaded in Stage 1.
Maintains same directory structure (YYYY/MM/DD) for output.
Outputs as JSON files with all job data.
"""

import os
import json
import re
import logging
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

def log_cron_stats(parsed_count):
    """Log parsing statistics to cron stats file."""
    stats_file = Path("logs/cron_stats.jsonl")
    stats_file.parent.mkdir(parents=True, exist_ok=True)
    
    stats = {
        "timestamp": datetime.now().isoformat(),
        "parsed_jobs": parsed_count,
    }
    
    try:
        with open(stats_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(stats, ensure_ascii=False) + "\n")
        logging.debug(f"Logged cron stats: {parsed_count} jobs parsed")
    except Exception as e:
        logging.error(f"Failed to write cron stats: {e}")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

def extract_post_id(post_id_str):
    """Extract numeric ID from post-XXXXX format."""
    match = re.search(r'post-(\d+)', post_id_str)
    return match.group(1) if match else None


def parse_post_div(post_div):
    """
    Extract data from a post div element.
    
    Returns dict with:
    - post_id: numeric ID
    - url: link to the job posting
    - unit_name: military unit name
    - position: job title/position
    - image_url: thumbnail image URL
    - categories: list of category classes
    - status: posting status (open/closed)
    """
    post_id = extract_post_id(post_div.get('id', ''))
    
    # Get all classes to extract categories
    classes = post_div.get('class', [])
    categories = [cls for cls in classes if cls.startswith('category-')]
    units = [cls for cls in classes if cls.startswith('units-')]
    status_classes = [cls for cls in classes if 'tors-status-' in cls]
    
    # Extract status
    status = 'unknown'
    for status_class in status_classes:
        if 'is-open' in status_class:
            status = 'open'
        elif 'is-closed' in status_class:
            status = 'closed'
    
    # Find the link
    link = post_div.find('a', class_='job-item')
    url = link.get('href', '') if link else ''
    
    # Find unit name
    unit_name_elem = post_div.find('h4', class_='square-content__title')
    unit_name = unit_name_elem.get_text(strip=True) if unit_name_elem else ''
    
    # Find position/vacancy
    position_elem = post_div.find('h4', class_='vacancy_content')
    position = position_elem.get_text(strip=True) if position_elem else ''
    
    # Find image
    img_elem = post_div.find('img', class_='wp-post-image')
    image_url = img_elem.get('src', '') if img_elem else ''
    
    return {
        'post_id': post_id,
        'url': url,
        'unit_name': unit_name,
        'position': position,
        'image_url': image_url,
        'categories': categories,
        'units': units,
        'status': status
    }


def parse_html_file(html_path):
    """Parse a single HTML file and extract all job postings."""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all divs with id matching "post-XXXXX"
        post_divs = soup.find_all('div', id=re.compile(r'^post-\d+$'))
        
        posts = []
        for post_div in post_divs:
            try:
                post_data = parse_post_div(post_div)
                if post_data['post_id']:  # Only add if we got a valid post ID
                    posts.append(post_data)
            except Exception as e:
                logging.warning(f"Failed to parse post in {html_path}: {e}")
                continue
        
        return posts
    
    except Exception as e:
        logging.error(f"Error parsing {html_path}: {e}")
        return []


def main():
    """Parse all HTML files to JSON."""
    
    logging.info("=" * 70)
    logging.info("STAGE 2: Parsing HTML to JSON")
    logging.info("=" * 70)
    
    base_path = Path('data')
    
    if not base_path.exists():
        logging.error(f"Directory {base_path} does not exist")
        return
    
    # Find all HTML files
    html_files = list(base_path.rglob('*.html'))
    
    if not html_files:
        logging.warning(f"No HTML files found in {base_path}")
        return
    
    logging.info(f"Found {len(html_files)} HTML files to process")
    
    total_posts = 0
    processed_files = 0
    
    for html_file in html_files:
        # Calculate relative path
        relative_path = html_file.relative_to(base_path)
        
        # Create corresponding JSON path
        json_file = base_path / relative_path.with_suffix('.json')
        
        # Create output directory if needed
        json_file.parent.mkdir(parents=True, exist_ok=True)
        
        logging.debug(f"Processing: {relative_path}")
        
        # Parse HTML and extract posts
        posts = parse_html_file(html_file)
        
        if posts:
            # Create output data
            output_data = {
                'source_file': str(relative_path),
                'parsed_at': datetime.now().isoformat(),
                'post_count': len(posts),
                'posts': posts
            }
            
            # Write JSON file
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            logging.debug(f"  ✓ Extracted {len(posts)} posts → {json_file}")
            total_posts += len(posts)
            processed_files += 1
        else:
            logging.debug(f"  No posts found in this file")
    
    logging.info(f"✓ Processed {processed_files}/{len(html_files)} files")
    logging.info(f"✓ Extracted {total_posts} total posts")
    
    # Log statistics for cron tracking
    log_cron_stats(total_posts)
    
    logging.info("STAGE 2 Complete\n")


if __name__ == '__main__':
    main()
