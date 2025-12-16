#!/usr/bin/env python3
"""
Stage 1: Fetch the main jobs listing page

Downloads the complete jobs listing from lobbyx.army with all content loaded.
Saves as data/YYYY/MM/DD/output_HHMMSS.html

Caching: If a file was downloaded within 1 hour, uses cache instead of re-downloading.
"""

import time
import os
import logging
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

def check_cache(cache_hours=1):
    """
    Check if a recent HTML file exists within cache window.
    
    Args:
        cache_hours: Hours threshold for cache validity (default: 1)
    
    Returns:
        Path to cached file if valid, None otherwise
    """
    base_path = Path('data')
    
    if not base_path.exists():
        return None
    
    # Find all output_*.html files
    html_files = list(base_path.rglob('output_*.html'))
    
    if not html_files:
        return None
    
    # Sort by modification time and check the latest
    html_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    latest_file = html_files[0]
    
    # Check if file is within cache window
    current_time = time.time()
    file_mtime = latest_file.stat().st_mtime
    age_hours = (current_time - file_mtime) / 3600
    
    if age_hours < cache_hours:
        return latest_file
    
    return None

def fetch_main_page():
    """Fetch the main jobs listing page using Playwright, with 1-hour cache."""
    
    logging.info("=" * 70)
    logging.info("STAGE 1: Fetching main jobs listing page")
    logging.info("=" * 70)
    
    # Check cache first
    cached_file = check_cache(cache_hours=1)
    if cached_file:
        age_minutes = ((time.time() - cached_file.stat().st_mtime) / 60)
        logging.info(f"✓ Using cached file from {age_minutes:.0f} minutes ago")
        logging.info(f"✓ File: {cached_file.relative_to(Path('data'))}")
        logging.info("STAGE 1 Complete (cached)\n")
        return
    
    logging.info("No recent cache found, fetching fresh data...")
    
    # Start Playwright
    with sync_playwright() as p:
        logging.debug("Launching browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Navigate to the target URL
        url = "https://lobbyx.army/?sphere=it"
        logging.info(f"Navigating to: {url}")
        try:
            page.goto(url, timeout=30000, wait_until='domcontentloaded')
            logging.debug("Successfully navigated")
        except Exception as e:
            logging.error(f"Failed to navigate to URL: {e}")
            raise

        # Click the #load-more button until it has the class "done"
        logging.debug("Loading all content...")
        max_attempts = 100  # Prevent infinite loops
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            try:
                load_more_button = page.locator("#load-more")
                button_class = load_more_button.get_attribute("class")
                
                if "done" in button_class:
                    logging.info("✓ All content loaded")
                    break
                
                logging.debug(f"Clicking load-more button (attempt {attempt})...")
                load_more_button.click()
                page.wait_for_timeout(2000)  # Wait for AJAX requests to complete
                
            except Exception as e:
                logging.debug(f"No more load-more button or error: {e}")
                break
        
        if attempt >= max_attempts:
            logging.warning(f"Reached maximum attempts ({max_attempts}), stopping load-more clicks")

        # Create a three-level directory structure for data files
        subfolder1 = time.strftime("%Y")
        subfolder2 = time.strftime("%m")
        subfolder3 = time.strftime("%d")
        output_dir = os.path.join("data", subfolder1, subfolder2, subfolder3)
        os.makedirs(output_dir, exist_ok=True)

        # Save the page content to an HTML file with a timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        html_file = os.path.join(output_dir, f"output_{timestamp}.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(page.content())
        
        logging.info(f"✓ Page saved to {html_file}")
        browser.close()
        logging.debug("Browser closed")

if __name__ == "__main__":
    fetch_main_page()
    logging.info("STAGE 1 Complete\n")
