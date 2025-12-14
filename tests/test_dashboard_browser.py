#!/usr/bin/env python3
"""
Automated browser tests for Quiet-Quail Dashboard.
Detects JavaScript console errors, API failures, and UI issues.
Starts internal server instance for testing.
Run: python tests/test_dashboard_browser.py
"""

import subprocess
import time
import sys
import os
import signal
from pathlib import Path
import json
import threading

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("ERROR: playwright not installed. Run: pip install playwright")
    sys.exit(1)


class DashboardServer:
    """Internal server instance for testing."""
    def __init__(self, port=8000):
        self.port = port
        self.process = None
        self.base_url = f"http://localhost:{port}"

    def start(self):
        """Start the dashboard server."""
        try:
            # Change to project directory
            project_dir = Path(__file__).parent.parent
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            
            # Start server process
            self.process = subprocess.Popen(
                [sys.executable, 'web/dashboard_server.py'],
                cwd=project_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env
            )
            
            # Wait for server to start with retry
            max_retries = 10
            for attempt in range(max_retries):
                time.sleep(1)
                
                # Verify server is running
                import urllib.request
                try:
                    urllib.request.urlopen(self.base_url, timeout=2)
                    print(f"✓ Internal server started at {self.base_url}")
                    return True
                except Exception:
                    if attempt < max_retries - 1:
                        continue
                    
            print(f"✗ Server failed to start after {max_retries} attempts")
            return False
                
        except Exception as e:
            print(f"✗ Failed to start server: {e}")
            return False

    def stop(self):
        """Stop the dashboard server."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                print("✓ Internal server stopped")
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
                print("✓ Internal server killed")
            except Exception as e:
                print(f"! Error stopping server: {e}")


class DashboardTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.console_errors = []
        self.api_failures = []
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }

    def run_tests(self):
        """Run all browser tests."""
        print("=" * 70)
        print("QUIET-QUAIL DASHBOARD BROWSER TESTS")
        print("=" * 70)
        print()

        with sync_playwright() as p:
            # Launch browser in headless mode
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # Capture console messages
            page.on("console", self._handle_console_message)

            try:
                print(f"[1/5] Loading dashboard at {self.base_url}...")
                self._test_page_load(page)

                print(f"[2/5] Checking for console errors...")
                self._test_console_errors(page)

                print(f"[3/5] Testing API endpoints...")
                self._test_api_endpoints(page)

                print(f"[4/5] Validating DOM elements...")
                self._test_dom_elements(page)

                print(f"[5/5] Testing data loading...")
                self._test_data_loading(page)

            except Exception as e:
                self._fail(f"Test error: {type(e).__name__}: {str(e)}")
            finally:
                context.close()
                browser.close()

        self._print_results()
        return self.test_results["failed"] == 0

    def _handle_console_message(self, msg):
        """Capture console messages."""
        if msg.type in ("error", "warning"):
            self.console_errors.append({
                "type": msg.type,
                "text": msg.text,
                "location": msg.location
            })

    def _test_page_load(self, page):
        """Test that page loads without errors."""
        try:
            response = page.goto(self.base_url, wait_until="networkidle")
            if response.status == 200:
                self._pass("Dashboard page loaded (HTTP 200)")
            else:
                self._fail(f"Dashboard returned HTTP {response.status}")
        except PlaywrightTimeout:
            self._fail("Page load timeout (network not idle after 30s)")
        except Exception as e:
            self._fail(f"Page load failed: {str(e)}")

    def _test_console_errors(self, page):
        """Test that no critical JavaScript errors occurred."""
        if not self.console_errors:
            self._pass("No console errors")
            return

        critical_errors = [e for e in self.console_errors if e["type"] == "error"]
        
        if critical_errors:
            for err in critical_errors:
                self._fail(f"JavaScript ERROR: {err['text']}")
        else:
            warnings = [e for e in self.console_errors if e["type"] == "warning"]
            self._pass(f"No critical errors ({len(warnings)} warnings)")

    def _test_api_endpoints(self, page):
        """Test that API endpoints respond correctly."""
        try:
            # Get files list from API
            files_response = page.evaluate("""
                async () => {
                    const response = await fetch('/api/files');
                    return {
                        status: response.status,
                        data: await response.json()
                    };
                }
            """)

            if files_response["status"] == 200:
                file_count = len(files_response["data"].get("files", []))
                self._pass(f"API /api/files responded with {file_count} files")
            else:
                self._fail(f"API returned HTTP {files_response['status']}")

        except Exception as e:
            self._fail(f"API test failed: {str(e)}")

    def _test_dom_elements(self, page):
        """Test that expected DOM elements exist."""
        tests = [
            ("body", "Page body"),
            ("#totalPosts", "Total posts stat"),
            ("#fileCount", "File count stat"),
            ("#jobsContainer", "Jobs container"),
            ("#unitsContainer", "Units container"),
            ("h1, h2", "Header element"),
        ]

        for selector, description in tests:
            try:
                element = page.query_selector(selector)
                if element:
                    self._pass(f"Found {description} ({selector})")
                else:
                    self._fail(f"Missing {description} ({selector})")
            except Exception as e:
                self._fail(f"DOM test for {selector} failed: {str(e)}")

    def _test_data_loading(self, page):
        """Test that data loads and displays."""
        try:
            # Wait for jobs container to load
            page.wait_for_selector("#jobsContainer", timeout=5000)

            # Check if container has content (not empty or loading)
            job_items = page.query_selector_all("#jobsContainer .job-item, #jobsContainer .card, #jobsContainer li")
            
            if job_items:
                count = len(job_items)
                self._pass(f"Data loaded: {count} job items displayed")
            else:
                # Check if it's just empty (no data) vs error
                container_text = page.query_selector("#jobsContainer").text_content()
                if "error" in container_text.lower() or "failed" in container_text.lower():
                    self._fail(f"Data loading error: {container_text}")
                else:
                    self._pass("Jobs container loaded (no items - expected if no data)")

        except PlaywrightTimeout:
            self._fail("Jobs container did not load within timeout")
        except Exception as e:
            self._fail(f"Data loading test failed: {str(e)}")

    def _pass(self, message):
        """Record passing test."""
        self.test_results["passed"] += 1
        print(f"  ✓ {message}")

    def _fail(self, message):
        """Record failing test."""
        self.test_results["failed"] += 1
        self.test_results["errors"].append(message)
        print(f"  ✗ {message}")

    def _print_results(self):
        """Print test summary."""
        print()
        print("=" * 70)
        print("TEST RESULTS")
        print("=" * 70)
        print(f"Passed: {self.test_results['passed']}")
        print(f"Failed: {self.test_results['failed']}")

        if self.test_results["errors"]:
            print()
            print("FAILURES:")
            for err in self.test_results["errors"]:
                print(f"  • {err}")

        if self.console_errors:
            print()
            print("CONSOLE MESSAGES:")
            for msg in self.console_errors:
                symbol = "⚠" if msg["type"] == "warning" else "✗"
                print(f"  {symbol} [{msg['type'].upper()}] {msg['text']}")

        print()
        if self.test_results["failed"] == 0:
            print("✓ ALL TESTS PASSED")
        else:
            print("✗ SOME TESTS FAILED")
        print("=" * 70)


def check_server_running(base_url="http://localhost:8000"):
    """Check if dashboard server is running."""
    try:
        import urllib.request
        urllib.request.urlopen(base_url, timeout=2)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    # Create and start internal server
    server = DashboardServer()
    
    try:
        print("Starting internal dashboard server for testing...")
        if not server.start():
            print("ERROR: Could not start internal server")
            sys.exit(1)
        
        # Run tests
        tester = DashboardTester(base_url=server.base_url)
        success = tester.run_tests()
        
        sys.exit(0 if success else 1)
        
    finally:
        # Always stop server
        print()
        print("Cleaning up...")
        server.stop()
