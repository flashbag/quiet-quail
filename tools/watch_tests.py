#!/usr/bin/env python3
"""
Watch script that runs tests automatically when files in scripts/ change.
Similar to nodemon but for Python testing.

Usage:
    python3 tools/watch_tests.py              # Watch all scripts
    python3 tools/watch_tests.py --verbose    # Verbose test output
"""

import sys
import os
import time
import subprocess
from pathlib import Path
from collections import defaultdict

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Error: watchdog module not installed")
    print("Install with: pip install watchdog")
    sys.exit(1)


class ScriptsChangeHandler(FileSystemEventHandler):
    """Handle file changes in scripts directory."""
    
    def __init__(self, test_args=None):
        """Initialize handler."""
        self.test_args = test_args or []
        self.last_run = 0
        self.debounce_seconds = 1.0  # Debounce rapid file changes
        self.test_process = None
    
    def on_modified(self, event):
        """Handle file modification."""
        if event.is_directory:
            return
        
        # Only watch Python files
        if not event.src_path.endswith('.py'):
            return
        
        # Check if it's in scripts/ or tests/
        if 'scripts' not in event.src_path and 'tests' not in event.src_path:
            return
        
        # Debounce: don't run too frequently
        current_time = time.time()
        if current_time - self.last_run < self.debounce_seconds:
            return
        
        self.last_run = current_time
        self.run_tests(event.src_path)
    
    def run_tests(self, changed_file):
        """Run tests when a file changes."""
        # Get relative path
        rel_path = os.path.relpath(changed_file)
        
        # Determine which tests to run
        if 'scripts' in changed_file:
            # Figure out which script changed
            script_name = os.path.basename(changed_file).replace('.py', '')
            test_file = f'tests/test_{script_name}.py'
            
            if os.path.exists(test_file):
                print(f"\n{'='*70}")
                print(f"File changed: {rel_path}")
                print(f"Running: python3 -m pytest {test_file} -v")
                print(f"{'='*70}\n")
                
                self.run_test_command([
                    'python3', '-m', 'pytest', test_file, '-v'
                ] + self.test_args)
            else:
                print(f"\nNo tests found for {script_name}")
        
        elif 'tests' in changed_file:
            # Test file changed, run that test
            print(f"\n{'='*70}")
            print(f"Test file changed: {rel_path}")
            print(f"Running: python3 run_tests.py --verbose")
            print(f"{'='*70}\n")
            
            self.run_test_command(['python3', 'run_tests.py', '--verbose'])
    
    def run_test_command(self, cmd):
        """Run test command and show output."""
        try:
            result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
            
            if result.returncode == 0:
                print("\n✓ Tests passed!")
            else:
                print("\n✗ Tests failed!")
        except Exception as e:
            print(f"Error running tests: {e}")


def main():
    """Main entry point."""
    print("Starting test watcher...")
    print("Watching: scripts/ and tests/ directories")
    print("Press Ctrl+C to stop\n")
    
    # Parse arguments
    test_args = []
    if '--verbose' in sys.argv:
        test_args.append('--verbose')
    
    # Set up file watcher
    event_handler = ScriptsChangeHandler(test_args)
    observer = Observer()
    
    project_root = Path(__file__).parent.parent
    
    # Watch scripts directory
    observer.schedule(event_handler, str(project_root / 'scripts'), recursive=True)
    
    # Watch tests directory
    observer.schedule(event_handler, str(project_root / 'tests'), recursive=True)
    
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping test watcher...")
        observer.stop()
    
    observer.join()


if __name__ == '__main__':
    main()
