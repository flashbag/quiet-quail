#!/usr/bin/env python3
"""
Stage 1: Fetch the main jobs listing page

Downloads the complete jobs listing from lobbyx.army with all content loaded.
Saves as data/YYYY/MM/DD/output_HHMMSS.html
No caching - always fetches fresh data on each run.
"""

import time
import os
import logging
from datetime import datetime
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

def fetch_main_page():
    """Fetch the main jobs listing page using Playwright."""
    
    logging.info("=" * 70)
    logging.info("STAGE 1: Fetching main jobs listing page")
    logging.info("=" * 70)
    
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
