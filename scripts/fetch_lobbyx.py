import time
import os
import sys
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

# Parse command-line arguments for cache control
force_download = False
skip_recent = True
recent_hours = 1

if len(sys.argv) > 1:
    if sys.argv[1] in ["-h", "--help"]:
        print("Usage: python3 fetch_lobbyx.py [options]")
        print("\nOptions:")
        print("  --force, -f         Force re-download all job pages (ignore cache)")
        print("  --no-cache          Skip all recently-downloaded job pages")
        print("  --cache-hours N     Customize cache window (default: 1 hour)")
        print("  --help, -h          Show this help message")
        print("\nExamples:")
        print("  python3 fetch_lobbyx.py                    # Default: 1-hour cache")
        print("  python3 fetch_lobbyx.py --force            # Force re-download all")
        print("  python3 fetch_lobbyx.py --cache-hours 6    # Use 6-hour cache window")
        sys.exit(0)
    elif sys.argv[1] in ["-f", "--force"]:
        force_download = True
        skip_recent = False
        logging.info("Cache mode: FORCE - Will re-download all job pages")
    elif sys.argv[1] == "--no-cache":
        skip_recent = False
        logging.info("Cache mode: NO-CACHE - Will skip all recently-downloaded files")
    elif sys.argv[1] == "--cache-hours" and len(sys.argv) > 2:
        try:
            recent_hours = int(sys.argv[2])
            logging.info(f"Cache mode: CUSTOM - Using {recent_hours}-hour cache window")
        except ValueError:
            logging.error(f"Invalid cache-hours value: {sys.argv[2]}")
            sys.exit(1)
else:
    logging.info("Cache mode: DEFAULT - Using 1-hour cache window")

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
    # Build command with cache options
    cmd = ["python3", "scripts/download_job_pages.py"]
    if force_download:
        cmd.append("--force")
    elif not skip_recent:
        cmd.append("--no-cache")
    elif recent_hours != 1:
        cmd.extend(["--cache-hours", str(recent_hours)])
    
    result = subprocess.run(
        cmd,
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