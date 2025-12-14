#!/usr/bin/env python3
"""
Pre-commit hook that runs tests if scripts are modified.
This prevents committing code that breaks tests.

Installation:
    python3 scripts/install_hooks.py
"""

import subprocess
import sys
import os

def run_command(cmd):
    """Run a command and return exit code."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def get_staged_files():
    """Get list of staged files."""
    code, stdout, _ = run_command('git diff --cached --name-only')
    if code != 0:
        return []
    return stdout.strip().split('\n')


def has_script_changes(files):
    """Check if any scripts were modified."""
    for f in files:
        if f.startswith('scripts/') and f.endswith('.py'):
            return True
    return False


def run_tests():
    """Run the test suite."""
    print("\n" + "="*70)
    print("Running tests for modified scripts...")
    print("="*70 + "\n")
    
    code, stdout, stderr = run_command('python3 run_tests.py')
    
    print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)
    
    return code


def main():
    """Main pre-commit hook logic."""
    files = get_staged_files()
    
    if not has_script_changes(files):
        # No script changes, skip tests
        sys.exit(0)
    
    # Run tests
    exit_code = run_tests()
    
    if exit_code != 0:
        print("\n" + "!"*70)
        print("TESTS FAILED - Commit blocked")
        print("Fix the failing tests and try again")
        print("!"*70 + "\n")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
