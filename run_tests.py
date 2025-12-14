#!/usr/bin/env python3
"""
Test runner for Quiet-Quail project.
Runs all tests and generates a report.

Usage:
    python3 run_tests.py              # Run all tests
    python3 run_tests.py --verbose    # Verbose output
    python3 run_tests.py --coverage   # With coverage report
"""

import sys
import unittest
import os
from pathlib import Path

def run_tests(verbosity=1, with_coverage=False):
    """Run all tests."""
    
    # Add project root to path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = str(project_root / 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
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
    
    # Parse arguments
    if '--verbose' in sys.argv:
        verbosity = 2
    if '--coverage' in sys.argv:
        with_coverage = True
    
    # Try to use coverage if requested
    if with_coverage:
        try:
            import coverage
            cov = coverage.Coverage()
            cov.start()
            
            exit_code = run_tests(verbosity=verbosity)
            
            cov.stop()
            cov.save()
            print("\nCoverage Report:")
            cov.report()
            
            return exit_code
        except ImportError:
            print("Warning: coverage module not installed. Running tests without coverage.")
            return run_tests(verbosity=verbosity)
    else:
        return run_tests(verbosity=verbosity)


if __name__ == '__main__':
    sys.exit(main())
