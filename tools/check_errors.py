#!/usr/bin/env python3
"""
Quick guide to check for console errors in the dashboard.
This script demonstrates how to check for errors both statically and at runtime.
"""

import subprocess
import sys


def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def main():
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*20 + "DASHBOARD ERROR DETECTION GUIDE" + " "*17 + "║")
    print("╚" + "="*68 + "╝")
    
    print_header("METHOD 1: Static Analysis (Instant)")
    print("Run the static analysis to check for syntax issues:\n")
    print("  $ python3 test_dashboard_errors.py\n")
    print("This will check for:")
    print("  ✓ JavaScript syntax errors")
    print("  ✓ Mismatched HTML tags")
    print("  ✓ Missing function definitions")
    print("  ✓ JSON file validity")
    print("  ✓ Try/catch error handling coverage")
    
    print_header("METHOD 2: Runtime Console Errors (Browser)")
    print("To see actual runtime errors:\n")
    print("  1. Start the dashboard server:")
    print("     $ python3 dashboard_server.py\n")
    print("  2. Open browser: http://localhost:8000\n")
    print("  3. Press F12 to open Developer Tools\n")
    print("  4. Check these tabs:")
    print("     • Console tab     → JavaScript errors & logs")
    print("     • Network tab     → Failed API requests")
    print("     • Elements tab    → HTML structure issues")
    
    print_header("METHOD 3: Persistent Monitoring (Recommended)")
    print("Use the file watcher to auto-restart on changes:\n")
    print("  $ ./dashboard-watch.sh\n")
    print("Then open browser at http://localhost:8000")
    print("Errors will show in BOTH:")
    print("  • Terminal output (server logs)")
    print("  • Browser console (JavaScript errors)")
    
    print_header("COMMON ERRORS & SOLUTIONS")
    print("Error: 'destroy is not a function'")
    print("  → Solution: Chart object not initialized, check console for canvas errors\n")
    
    print("Error: 'Cannot find element by ID'")
    print("  → Solution: HTML element missing from dashboard.html, check HTML structure\n")
    
    print("Error: 'Fetch failed'")
    print("  → Solution: Check Network tab, verify API endpoints, check CORS headers\n")
    
    print("Error: 'JSON parsing error'")
    print("  → Solution: Invalid JSON file, check saved_json directory for syntax\n")
    
    print_header("WHAT WE CHECK NOW")
    print("✅ Function definitions (loadData, processData, displayJobTracking, etc.)")
    print("✅ Chart initialization (Chart.js library availability)")
    print("✅ Canvas elements (persistenceChart, unitsChartTracking)")
    print("✅ Data processing (JSON validity, deduplication)")
    print("✅ Error handling (try/catch blocks, error logging)")
    print("✅ Job Persistence Distribution (5 dynamic ranges with percentages)")
    print("✅ Detailed breakdown table (color-coded rows with statistics)")
    
    print_header("TEST RESULTS")
    print("Last test run:")
    subprocess.run([sys.executable, 'test_dashboard_errors.py'], 
                   capture_output=False)


if __name__ == '__main__':
    main()
