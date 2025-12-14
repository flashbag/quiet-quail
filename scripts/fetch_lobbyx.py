import time
import os
import logging
import subprocess
from playwright.sync_api import sync_playwright

# Configure logging for maximum debug output
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

logging.debug("Starting script execution.")

# Start Playwright
with sync_playwright() as p:
    logging.debug("Launching browser.")
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Navigate to the target URL
    url = "https://lobbyx.army/?sphere=it"
    logging.debug(f"Navigating to URL: {url}")
    try:
        # Add 30-second timeout to prevent hanging indefinitely
        page.goto(url, timeout=30000, wait_until='domcontentloaded')
        logging.debug(f"Successfully navigated to {url}")
    except Exception as e:
        logging.error(f"Failed to navigate to URL: {e}")
        raise

    # Click the #load-more button until it has the class "done"
    while True:
        try:
            load_more_button = page.locator("#load-more")
            button_class = load_more_button.get_attribute("class")
            logging.debug(f"Button class: {button_class}")
            if "done" in button_class:
                logging.debug("All content loaded.")
                break
            logging.debug("Clicking load-more button.")
            load_more_button.click()
            page.wait_for_timeout(2000)  # Wait for AJAX requests to complete
        except Exception as e:
            logging.error(f"Error or no more load-more button: {e}")
            break

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
    logging.debug(f"Page content saved to {html_file}")

    browser.close()
    logging.debug("Browser closed.")

# Automatically parse the HTML to JSON
logging.debug("Starting HTML to JSON parsing...")
try:
    result = subprocess.run(
        ["python3", "scripts/parse_html_to_json.py"],
        capture_output=True,
        text=True,
        timeout=300
    )
    if result.returncode == 0:
        logging.debug("HTML to JSON parsing completed successfully")
    else:
        logging.warning(f"HTML to JSON parsing had issues: {result.stderr}")
except Exception as e:
    logging.warning(f"Could not run parse_html_to_json.py: {e}")

# Download individual job pages for new jobs
logging.debug("Downloading individual job pages...")
try:
    result = subprocess.run(
        ["python3", "scripts/download_job_pages.py"],
        capture_output=True,
        text=True,
        timeout=600
    )
    if result.returncode == 0:
        logging.debug("Job page downloads completed successfully")
    else:
        logging.warning(f"Job page downloads had issues: {result.stderr}")
except Exception as e:
    logging.warning(f"Could not run download_job_pages.py: {e}")

# Generate dashboard API file
logging.debug("Generating dashboard API file...")
try:
    result = subprocess.run(
        ["python3", "tools/generate_dashboard_api.py"],
        capture_output=True,
        text=True,
        timeout=60
    )
    if result.returncode == 0:
        logging.debug("Dashboard API file generated successfully")
    else:
        logging.warning(f"Dashboard API generation had issues: {result.stderr}")
except Exception as e:
    logging.warning(f"Could not run generate_dashboard_api.py: {e}")

logging.debug("Script execution completed.")