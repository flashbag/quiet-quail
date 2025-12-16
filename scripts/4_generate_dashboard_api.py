#!/usr/bin/env python3
"""
Stage 4: Generate dashboard API

Creates the JSON file list for the dashboard to load.
Generates api/list-json-files.json with all available job data.
"""

import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)


def main():
    """Generate JSON file list for dashboard."""
    
    logging.info("=" * 70)
    logging.info("STAGE 4: Generating dashboard API")
    logging.info("=" * 70)
    
    base_path = Path('data').resolve()
    
    if not base_path.exists():
        logging.error(f"Directory data does not exist")
        return
    
    # Find all JSON files
    json_files = list(base_path.rglob('*.json'))
    json_files = [f for f in json_files if f.name != 'consolidated_unique.json']
    
    logging.info(f"Found {len(json_files)} JSON files")
    
    # Convert to relative paths
    file_objects = []
    for json_file in sorted(json_files, reverse=True):
        relative_path = str(json_file.relative_to(base_path.parent))
        file_objects.append({
            'path': relative_path,
            'name': json_file.stem,
            'date': str(json_file.parent)
        })
    
    # Create output directory
    output_path = Path('api')
    output_path.mkdir(exist_ok=True)
    
    # Write file list
    file_list = {
        'files': file_objects,
        'count': len(file_objects)
    }
    
    output_file = output_path / 'list-json-files.json'
    with open(output_file, 'w') as f:
        json.dump(file_list, f, indent=2)
    
    logging.info(f"✓ Generated file list with {len(file_objects)} files")
    logging.info(f"✓ Saved to {output_file}")
    logging.info("STAGE 4 Complete\n")


if __name__ == '__main__':
    main()
