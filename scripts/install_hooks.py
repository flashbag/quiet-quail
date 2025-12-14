#!/usr/bin/env python3
"""
Install git hooks for automatic testing.

Usage:
    python3 scripts/install_hooks.py
"""

import os
import sys
from pathlib import Path
import stat


def install_pre_commit_hook():
    """Install pre-commit hook."""
    git_hooks_dir = Path('.git/hooks')
    
    if not git_hooks_dir.exists():
        print("Error: .git/hooks directory not found. Are you in a git repository?")
        return False
    
    hook_file = git_hooks_dir / 'pre-commit'
    
    # Create the hook script
    hook_content = '''#!/bin/bash
# Pre-commit hook - runs tests before commit
python3 scripts/pre_commit_hook.py
exit_code=$?

if [ $exit_code -ne 0 ]; then
    exit 1
fi

exit 0
'''
    
    try:
        with open(hook_file, 'w') as f:
            f.write(hook_content)
        
        # Make executable
        st = os.stat(hook_file)
        os.chmod(hook_file, st.st_mode | stat.S_IEXEC | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        print(f"✓ Pre-commit hook installed: {hook_file}")
        return True
    except Exception as e:
        print(f"Error installing pre-commit hook: {e}")
        return False


def main():
    """Main entry point."""
    print("Installing git hooks...\n")
    
    success = install_pre_commit_hook()
    
    if success:
        print("\n✓ All hooks installed successfully!")
        print("\nHooks will run automatically on git commit")
        print("To bypass hooks (not recommended): git commit --no-verify")
    else:
        print("\n✗ Failed to install hooks")
        sys.exit(1)


if __name__ == '__main__':
    main()
