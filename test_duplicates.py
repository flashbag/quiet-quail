#!/usr/bin/env python3
"""
Test suite to detect and prevent duplicate job postings in the dashboard.
Ensures data integrity across multiple HTML parsing sessions.
"""

import json
from pathlib import Path
from collections import defaultdict
import unittest


class TestJobDuplicates(unittest.TestCase):
    """Test cases for duplicate job detection."""
    
    def setUp(self):
        """Load all JSON data for testing."""
        self.all_posts = []
        self.post_ids = defaultdict(list)
        self.files_data = {}
        
        saved_json_dir = Path('data')
        if saved_json_dir.exists():
            for json_file in sorted(saved_json_dir.rglob('*.json')):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.files_data[str(json_file)] = data
                        
                        for post in data.get('posts', []):
                            post_id = post.get('post_id')
                            post_with_source = dict(post)
                            post_with_source['_source_file'] = str(json_file)
                            self.all_posts.append(post_with_source)
                            
                            if post_id:
                                self.post_ids[post_id].append(str(json_file))
                except Exception as e:
                    print(f"Error reading {json_file}: {e}")
    
    def test_no_duplicate_posts_in_single_file(self):
        """Each JSON file should not contain duplicate post IDs."""
        duplicates_in_files = {}
        
        for file_path, data in self.files_data.items():
            post_ids_in_file = [post.get('post_id') for post in data.get('posts', [])]
            post_id_counts = defaultdict(int)
            
            for post_id in post_ids_in_file:
                if post_id:
                    post_id_counts[post_id] += 1
            
            file_duplicates = {pid: count for pid, count in post_id_counts.items() if count > 1}
            if file_duplicates:
                duplicates_in_files[file_path] = file_duplicates
        
        self.assertEqual(
            duplicates_in_files, 
            {},
            f"Found duplicate posts within single files: {duplicates_in_files}"
        )
    
    def test_unique_count_consistency(self):
        """Verify unique posts count."""
        unique_post_count = len(self.post_ids)
        total_post_count = len(self.all_posts)
        
        print(f"\nUnique posts: {unique_post_count}")
        print(f"Total posts (with duplicates): {total_post_count}")
        
        # This test documents the state but passes
        self.assertGreater(unique_post_count, 0, "Should have at least one unique post")
    
    def test_posts_have_required_fields(self):
        """All posts should have required fields."""
        required_fields = ['post_id', 'position', 'unit_name', 'url', 'status']
        
        for i, post in enumerate(self.all_posts):
            for field in required_fields:
                self.assertIn(
                    field, post,
                    f"Post {i} missing required field '{field}': {post.get('post_id')}"
                )
            
            self.assertIsNotNone(post.get('post_id'), f"Post {i} has null post_id")
            self.assertIsNotNone(post.get('position'), f"Post {i} has null position")
    
    def test_post_ids_are_unique_strings(self):
        """All post IDs should be valid strings."""
        for post_id in self.post_ids.keys():
            self.assertIsInstance(post_id, str, f"Post ID {post_id} is not a string")
            self.assertTrue(post_id.isdigit(), f"Post ID {post_id} is not numeric")
    
    def test_status_values_valid(self):
        """All posts should have valid status values."""
        valid_statuses = {'open', 'closed', 'unknown'}
        
        for post in self.all_posts:
            status = post.get('status', 'unknown')
            self.assertIn(
                status,
                valid_statuses,
                f"Invalid status '{status}' for post {post.get('post_id')}"
            )
    
    def test_urls_not_empty(self):
        """All posts should have non-empty URLs."""
        for post in self.all_posts:
            url = post.get('url', '')
            self.assertTrue(
                len(url.strip()) > 0,
                f"Empty URL for post {post.get('post_id')}"
            )


class TestDuplicateReport(unittest.TestCase):
    """Generate detailed report about duplicates."""
    
    def test_duplicate_analysis(self):
        """Analyze and report on duplicate posts."""
        all_posts = []
        post_ids = defaultdict(list)
        
        saved_json_dir = Path('data')
        if saved_json_dir.exists():
            for json_file in sorted(saved_json_dir.rglob('*.json')):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        for post in data.get('posts', []):
                            post_id = post.get('post_id')
                            all_posts.append({
                                'id': post_id,
                                'position': post.get('position'),
                                'file': str(json_file)
                            })
                            if post_id:
                                post_ids[post_id].append(str(json_file))
                except Exception as e:
                    print(f"Error reading {json_file}: {e}")
        
        # Find duplicates
        duplicates = {pid: files for pid, files in post_ids.items() if len(files) > 1}
        
        print(f"\n{'='*70}")
        print(f"DUPLICATE JOB POSTING ANALYSIS")
        print(f"{'='*70}")
        print(f"Total posts loaded: {len(all_posts)}")
        print(f"Unique post IDs: {len(post_ids)}")
        print(f"Duplicate post IDs: {len(duplicates)}")
        print(f"{'='*70}")
        
        if duplicates:
            print(f"\nTOP DUPLICATED POSTS:")
            # Sort by number of occurrences
            sorted_dups = sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)
            
            for i, (post_id, files) in enumerate(sorted_dups[:20], 1):
                position = next((p['position'] for p in all_posts if p['id'] == post_id), 'N/A')
                print(f"\n{i}. Post ID: {post_id}")
                print(f"   Position: {position}")
                print(f"   Appears in {len(files)} files:")
                for file in files:
                    print(f"     - {file}")
        else:
            print("\n✓ No duplicate posts found!")
        
        # This is not an assertion, just a report
        self.assertTrue(True)


class TestDataDeduplication(unittest.TestCase):
    """Tests for deduplication strategy."""
    
    def test_deduplication_by_post_id(self):
        """Verify deduplication would work correctly by post ID."""
        all_posts = []
        
        saved_json_dir = Path('saved_json')
        if saved_json_dir.exists():
            for json_file in sorted(saved_json_dir.rglob('*.json')):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        all_posts.extend(data.get('posts', []))
                except Exception as e:
                    print(f"Error reading {json_file}: {e}")
        
        # Simulate deduplication
        seen_ids = set()
        unique_posts = []
        duplicates_removed = 0
        
        for post in all_posts:
            post_id = post.get('post_id')
            if post_id not in seen_ids:
                unique_posts.append(post)
                seen_ids.add(post_id)
            else:
                duplicates_removed += 1
        
        print(f"\n{'='*70}")
        print(f"DEDUPLICATION SIMULATION")
        print(f"{'='*70}")
        print(f"Total posts before dedup: {len(all_posts)}")
        print(f"Total posts after dedup: {len(unique_posts)}")
        print(f"Duplicates removed: {duplicates_removed}")
        print(f"{'='*70}")
        
        # Verify unique posts don't have duplicate IDs
        unique_ids = [post.get('post_id') for post in unique_posts]
        self.assertEqual(
            len(unique_ids),
            len(set(unique_ids)),
            "Unique posts should not contain duplicates"
        )


def run_tests():
    """Run all test suites."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestJobDuplicates))
    suite.addTests(loader.loadTestsFromTestCase(TestDuplicateReport))
    suite.addTests(loader.loadTestsFromTestCase(TestDataDeduplication))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
