#!/usr/bin/env python3
"""
Generate a list of available JSON files for the dashboard to load.
Run this after the scraper/parser completes.
"""

import os
import json
from pathlib import Path


def generate_json_file_list(base_dir='data', output_dir='api'):
    """Generate a list of all JSON files in data directory."""
    
    base_path = Path(base_dir).resolve()
    
    if not base_path.exists():
        print(f"Directory {base_dir} does not exist")
        return
    
    # Find all JSON files
    json_files = list(base_path.rglob('*.json'))
    
    # Filter out consolidated_unique.json
    json_files = [f for f in json_files if f.name != 'consolidated_unique.json']
    
    # Convert to relative paths from base_dir (not cwd)
    relative_files = [str(f.relative_to(base_path.parent)) for f in sorted(json_files, reverse=True)]
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Write file list
    file_list = {
        'files': relative_files,
        'count': len(relative_files)
    }
    
    output_file = output_path / 'list-json-files.json'
    with open(output_file, 'w') as f:
        json.dump(file_list, f, indent=2)
    
    print(f"✓ Generated file list with {len(relative_files)} files")
    print(f"✓ Saved to {output_file}")


if __name__ == '__main__':
    generate_json_file_list()
