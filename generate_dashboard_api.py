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
    
    # Convert to relative paths and create objects with path property
    file_objects = []
    for json_file in sorted(json_files, reverse=True):
        relative_path = str(json_file.relative_to(base_path.parent))
        file_objects.append({
            'path': relative_path,
            'name': json_file.stem,
            'date': str(json_file.parent)
        })
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Write file list
    file_list = {
        'files': file_objects,
        'count': len(file_objects)
    }
    
    output_file = output_path / 'list-json-files.json'
    with open(output_file, 'w') as f:
        json.dump(file_list, f, indent=2)
    
    print(f"✓ Generated file list with {len(file_objects)} files")
    print(f"✓ Saved to {output_file}")


if __name__ == '__main__':
    generate_json_file_list()
