#!/usr/bin/env python3
"""
Deduplicate job posts across all JSON files.
Creates a single deduplicated JSON file instead of having duplicates across multiple files.
"""

import json
from pathlib import Path
from collections import defaultdict

def deduplicate_posts():
    """Remove duplicate posts and consolidate into a single file."""
    
    all_posts = {}
    post_order = []  # Keep track of first appearance
    
    saved_json_dir = Path('saved_json')
    
    if not saved_json_dir.exists():
        print("No saved_json directory found")
        return
    
    json_files = sorted(saved_json_dir.rglob('*.json'))
    print(f"Processing {len(json_files)} JSON files\n")
    
    # Load all posts and deduplicate
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                for post in data.get('posts', []):
                    post_id = post.get('post_id')
                    if post_id not in all_posts:
                        all_posts[post_id] = post
                        post_order.append(post_id)
        except Exception as e:
            print(f"Error reading {json_file}: {e}")
    
    # Create consolidated file
    unique_posts = [all_posts[pid] for pid in post_order]
    
    consolidated_data = {
        'posts': unique_posts,
        'post_count': len(unique_posts),
        'source_file': 'consolidated_unique',
        'parsed_at': 'consolidated from all files'
    }
    
    # Save to consolidated file
    output_path = saved_json_dir / 'consolidated_unique.json'
    with open(output_path, 'w') as f:
        json.dump(consolidated_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Created consolidated file: {output_path}")
    print(f"✓ Total unique posts: {len(unique_posts)}")
    print(f"✓ Duplicates removed: {sum(len(data.get('posts', [])) for data in [json.load(open(f)) for f in json_files]) - len(unique_posts)}")

if __name__ == '__main__':
    deduplicate_posts()
