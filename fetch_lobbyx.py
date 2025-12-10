import time
import os
import logging
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
    page.goto(url)

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

    # Create a three-level directory structure for saved HTML files
    subfolder1 = time.strftime("%Y")
    subfolder2 = time.strftime("%m")
    subfolder3 = time.strftime("%d")
    output_dir = os.path.join("saved_html", subfolder1, subfolder2, subfolder3)
    os.makedirs(output_dir, exist_ok=True)

    # Save the page content to an HTML file with a timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    html_file = os.path.join(output_dir, f"output_{timestamp}.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(page.content())
    logging.debug(f"Page content saved to {html_file}")

    browser.close()
    logging.debug("Browser closed.")