#!/usr/bin/env python3
"""
Validate the data structure in data/ directory.
Checks for:
- HTML and JSON file pairs
- Valid JSON structure
- Required fields in job postings
- Filename format consistency
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class DataValidator:
    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)
        self.errors = []
        self.warnings = []
        self.stats = {
            'html_files': 0,
            'json_files': 0,
            'job_pages': 0,
            'total_jobs': 0,
            'unique_posts': set(),
            'date_range': [],
            'invalid_files': [],
            'missing_pairs': [],
        }

    def validate(self):
        """Run all validation checks."""
        print("=" * 70)
        print("DATA STRUCTURE VALIDATION")
        print("=" * 70)

        if not self.data_dir.exists():
            print(f"❌ ERROR: Data directory not found: {self.data_dir}")
            return False

        print(f"\n📁 Validating: {self.data_dir.absolute()}\n")

        # Validate all files
        self.validate_files()

        # Validate JSON structure
        self.validate_json_structure()

        # Validate file pairs
        self.validate_file_pairs()

        # Print results
        self.print_results()

        return len(self.errors) == 0

    def validate_files(self):
        """Validate individual files."""
        print("Checking files...")
        
        for filepath in self.data_dir.rglob('*'):
            if not filepath.is_file():
                continue

            filename = filepath.name
            
            # Count files
            if filename.endswith('.html'):
                self.stats['html_files'] += 1
                self.validate_html_filename(filepath)
            elif filename.endswith('.json'):
                self.stats['json_files'] += 1
                self.validate_json_filename(filepath)
            else:
                self.warnings.append(f"Unknown file type: {filepath}")

    def validate_html_filename(self, filepath):
        """Validate HTML filename format: output_YYYYMMDDhhmmss.html OR job_*.html"""
        filename = filepath.name
        
        # Accept both formats:
        # 1. output_YYYYMMDDhhmmss.html (scraped pages)
        # 2. job_*.html (individual job pages)
        
        if filename.startswith('job_') and filename.endswith('.html'):
            # Job page format - always valid
            return
        
        pattern = r'^output_(\d{8})_(\d{6})\.html$'
        
        if not re.match(pattern, filename):
            self.errors.append(f"Invalid HTML filename format: {filepath}")
            self.stats['invalid_files'].append(str(filepath))
            return

        match = re.match(pattern, filename)
        if match:
            date_str, time_str = match.groups()
            try:
                datetime.strptime(date_str + time_str, '%Y%m%d%H%M%S')
            except ValueError:
                self.errors.append(f"Invalid date/time in filename: {filepath}")

    def validate_json_filename(self, filepath):
        """Validate JSON filename format: output_YYYYMMDDhhmmss.json"""
        filename = filepath.name
        
        # Allow both output_*.json and consolidated_unique.json
        if filename == 'consolidated_unique.json':
            return
            
        pattern = r'^output_(\d{8})_(\d{6})\.json$'
        
        if not re.match(pattern, filename):
            self.errors.append(f"Invalid JSON filename format: {filepath}")
            self.stats['invalid_files'].append(str(filepath))
            return

        match = re.match(pattern, filename)
        if match:
            date_str, time_str = match.groups()
            try:
                dt = datetime.strptime(date_str + time_str, '%Y%m%d%H%M%S')
                self.stats['date_range'].append(dt)
            except ValueError:
                self.errors.append(f"Invalid date/time in filename: {filepath}")

    def validate_json_structure(self):
        """Validate JSON file structure and content."""
        print("Checking JSON structure...")
        
        for json_file in self.data_dir.rglob('*.json'):
            if json_file.name == '.gitkeep':
                continue

            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Validate main file structure
                if json_file.name == 'consolidated_unique.json':
                    self.validate_consolidated_json(data, json_file)
                elif json_file.name.startswith('output_'):
                    self.validate_output_json(data, json_file)
                else:
                    self.warnings.append(f"Unknown JSON file: {json_file}")

            except json.JSONDecodeError as e:
                self.errors.append(f"Invalid JSON in {json_file}: {e}")
            except Exception as e:
                self.errors.append(f"Error reading {json_file}: {e}")

    def validate_output_json(self, data, filepath):
        """Validate output_*.json structure."""
        required_fields = ['posts']
        
        # Check main structure
        for field in required_fields:
            if field not in data:
                self.errors.append(f"Missing '{field}' in {filepath}")
                return

        # Validate posts
        posts = data.get('posts', [])
        if not isinstance(posts, list):
            self.errors.append(f"'posts' is not a list in {filepath}")
            return

        self.stats['total_jobs'] += len(posts)

        # Validate each post
        for idx, post in enumerate(posts):
            if not isinstance(post, dict):
                self.errors.append(f"Post {idx} is not a dict in {filepath}")
                continue

            required_post_fields = ['post_id', 'url', 'position']
            for field in required_post_fields:
                if field not in post:
                    self.warnings.append(
                        f"Missing '{field}' in post {idx} of {filepath}"
                    )

            # Track unique posts
            post_id = post.get('post_id')
            if post_id:
                self.stats['unique_posts'].add(post_id)

    def validate_consolidated_json(self, data, filepath):
        """Validate consolidated_unique.json structure."""
        if 'posts' not in data:
            self.errors.append(f"Missing 'posts' in {filepath}")
            return

        posts = data.get('posts', [])
        if not isinstance(posts, list):
            self.errors.append(f"'posts' is not a list in {filepath}")
            return

        # Track unique posts from consolidated file
        for post in posts:
            post_id = post.get('post_id')
            if post_id:
                self.stats['unique_posts'].add(post_id)

    def validate_file_pairs(self):
        """Check if HTML and JSON files have matching pairs."""
        print("Checking file pairs...")
        
        html_files = set()
        json_files = set()

        # Collect output_*.html files (scraped pages, need JSON pairs)
        for filepath in self.data_dir.rglob('output_*.html'):
            stem = filepath.stem  # output_YYYYMMDDhhmmss
            html_files.add(stem)

        # Collect output_*.json files
        for filepath in self.data_dir.rglob('output_*.json'):
            stem = filepath.stem
            json_files.add(stem)

        # Check for missing pairs (only for output_* files)
        html_only = html_files - json_files
        json_only = json_files - html_files

        for stem in html_only:
            self.warnings.append(f"HTML without JSON pair: {stem}.html")

        for stem in json_only:
            self.warnings.append(f"JSON without HTML pair: {stem}.json")
        
        # Count job_*.html files (individual job pages, don't need pairs)
        job_pages = list(self.data_dir.rglob('job_*.html'))
        if job_pages:
            self.stats['job_pages'] = len(job_pages)

    def print_results(self):
        """Print validation results."""
        print("\n" + "=" * 70)
        print("VALIDATION RESULTS")
        print("=" * 70)

        # Statistics
        print(f"\n📊 Statistics:")
        print(f"  HTML files: {self.stats['html_files']}")
        print(f"  JSON files: {self.stats['json_files']}")
        if self.stats['job_pages'] > 0:
            print(f"  Job pages: {self.stats['job_pages']}")
        print(f"  Total job records: {self.stats['total_jobs']}")
        print(f"  Unique post IDs: {len(self.stats['unique_posts'])}")

        if self.stats['date_range']:
            dates = sorted(self.stats['date_range'])
            print(f"  Date range: {dates[0].date()} to {dates[-1].date()}")

        # Errors
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors[:10]:  # Show first 10
                print(f"   - {error}")
            if len(self.errors) > 10:
                print(f"   ... and {len(self.errors) - 10} more")
        else:
            print(f"\n✅ No errors found")

        # Warnings
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"   - {warning}")
            if len(self.warnings) > 10:
                print(f"   ... and {len(self.warnings) - 10} more")
        else:
            print(f"\n✅ No warnings")

        # Overall status
        print("\n" + "=" * 70)
        if len(self.errors) == 0:
            print("✅ DATA STRUCTURE IS VALID")
        else:
            print("❌ DATA STRUCTURE HAS ERRORS")
        print("=" * 70)


def main():
    """Main entry point."""
    validator = DataValidator()
    success = validator.validate()
    exit(0 if success else 1)


if __name__ == '__main__':
    main()
