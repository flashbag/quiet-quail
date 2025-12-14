#!/usr/bin/env python3
"""
Check for duplicate job posts across all JSON files.
"""

import json
from pathlib import Path
from collections import defaultdict

def check_duplicates():
    """Analyze JSON files for duplicate posts."""
    all_posts = []
    post_ids = defaultdict(list)
    
    saved_json_dir = Path('saved_json')
    
    if not saved_json_dir.exists():
        print("No saved_json directory found")
        return
    
    # Load all JSON files
    json_files = list(saved_json_dir.rglob('*.json'))
    print(f"Found {len(json_files)} JSON files\n")
    
    for json_file in sorted(json_files):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                for post in data.get('posts', []):
                    post_id = post.get('post_id')
                    all_posts.append({
                        'id': post_id,
                        'position': post.get('position'),
                        'unit': post.get('unit_name'),
                        'file': str(json_file)
                    })
                    if post_id:
                        post_ids[post_id].append(str(json_file))
        except Exception as e:
            print(f"Error reading {json_file}: {e}")
    
    # Find duplicates
    duplicates = {pid: files for pid, files in post_ids.items() if len(files) > 1}
    
    print(f"Total posts loaded: {len(all_posts)}")
    print(f"Unique post IDs: {len(post_ids)}")
    print(f"Duplicate post IDs: {len(duplicates)}")
    print(f"Duplicate posts: {sum(len(files) - 1 for files in duplicates.values())}")
    print()
    
    if duplicates:
        print("=" * 80)
        print("TOP 20 DUPLICATED POSTS:")
        print("=" * 80)
        for i, (post_id, files) in enumerate(list(duplicates.items())[:20], 1):
            position = next((p['position'] for p in all_posts if p['id'] == post_id), 'N/A')
            unit = next((p['unit'] for p in all_posts if p['id'] == post_id), 'N/A')
            print(f"\n{i}. Post ID {post_id}")
            print(f"   Position: {position}")
            print(f"   Unit: {unit}")
            print(f"   Appears in {len(files)} files:")
            for file in files:
                print(f"     - {file}")
    else:
        print("No duplicates found!")

if __name__ == '__main__':
    check_duplicates()
