#!/usr/bin/env python3
"""
Test runner for Quiet-Quail project.
Runs all tests and generates coverage reports.

Usage:
    python3 run_tests.py              # Run all tests
    python3 run_tests.py --verbose    # Verbose output
    python3 run_tests.py --coverage   # With coverage report
    python3 run_tests.py --html       # Generate HTML coverage report
"""

import sys
import unittest
import os
from pathlib import Path

try:
    import coverage
    HAS_COVERAGE = True
except ImportError:
    HAS_COVERAGE = False

def run_tests(verbosity=1, with_coverage=False, html_report=False):
    """Run all tests with optional coverage."""
    
    cov = None
    if with_coverage and HAS_COVERAGE:
        cov = coverage.Coverage(source=['scripts'])
        cov.start()
    
    # Add project root to path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = str(project_root / 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Stop coverage if running
    coverage_data = None
    if cov:
        cov.stop()
        cov.save()
        coverage_data = cov
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    # Print coverage report
    if coverage_data:
        print("\n" + "=" * 70)
        print("COVERAGE REPORT")
        print("=" * 70)
        coverage_data.report()
        
        # Generate HTML report if requested
        if html_report:
            html_dir = 'htmlcov'
            coverage_data.html_report(directory=html_dir)
            print(f"\nHTML coverage report generated in {html_dir}/")
    
    if result.wasSuccessful():
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


def main():
    """Main entry point."""
    verbosity = 1
    with_coverage = False
    html_report = False
    
    # Parse arguments
    if '--verbose' in sys.argv:
        verbosity = 2
    if '--coverage' in sys.argv:
        with_coverage = True
    if '--html' in sys.argv:
        with_coverage = True
        html_report = True
    
    if not HAS_COVERAGE and with_coverage:
        print("Warning: coverage module not installed.")
        print("Install with: pip install coverage")
        with_coverage = False
    
    exit_code = run_tests(verbosity=verbosity, with_coverage=with_coverage, html_report=html_report)
    
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
