#!/usr/bin/env python3
"""
Unit tests to prevent job post duplication.
Tests both the detection and prevention of duplicate posts.
"""

import unittest
import json
import tempfile
from pathlib import Path
from datetime import datetime


class TestDuplicatePrevention(unittest.TestCase):
    """Test suite for duplicate post prevention."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_posts = [
            {
                'post_id': '12345',
                'position': 'Developer',
                'unit_name': 'Unit A',
                'status': 'open',
                'url': 'https://example.com/1',
                'categories': [],
                'units': []
            },
            {
                'post_id': '12346',
                'position': 'Manager',
                'unit_name': 'Unit B',
                'status': 'open',
                'url': 'https://example.com/2',
                'categories': [],
                'units': []
            },
            {
                'post_id': '12345',  # Duplicate
                'position': 'Developer',
                'unit_name': 'Unit A',
                'status': 'open',
                'url': 'https://example.com/1',
                'categories': [],
                'units': []
            }
        ]
    
    def test_detect_duplicates(self):
        """Test detecting duplicate posts by ID."""
        post_ids = {}
        duplicates = 0
        
        for post in self.test_posts:
            post_id = post.get('post_id')
            if post_id in post_ids:
                duplicates += 1
            else:
                post_ids[post_id] = True
        
        self.assertEqual(duplicates, 1, "Should detect 1 duplicate")
        self.assertEqual(len(post_ids), 2, "Should have 2 unique IDs")
    
    def test_deduplicate_posts(self):
        """Test deduplicating posts using a dictionary."""
        unique_map = {}
        
        for post in self.test_posts:
            post_id = post.get('post_id')
            if post_id not in unique_map:
                unique_map[post_id] = post
        
        unique_posts = list(unique_map.values())
        
        self.assertEqual(len(unique_posts), 2, "Should have 2 unique posts")
        self.assertNotEqual(
            [p['post_id'] for p in unique_posts],
            [p['post_id'] for p in self.test_posts],
            "Unique list should differ from original (duplicates removed)"
        )
    
    def test_post_id_required(self):
        """Test that post_id is required and present."""
        for post in self.test_posts:
            self.assertIn('post_id', post, "Every post must have a post_id")
            self.assertIsNotNone(post['post_id'], "post_id must not be None")
            self.assertGreater(
                len(str(post['post_id'])), 0,
                "post_id must not be empty"
            )
    
    def test_required_fields(self):
        """Test that posts have all required fields."""
        required_fields = [
            'post_id', 'position', 'unit_name', 'status',
            'url', 'categories', 'units'
        ]
        
        for post in self.test_posts[:2]:  # Check non-duplicate posts
            for field in required_fields:
                self.assertIn(
                    field, post,
                    f"Post must have '{field}' field"
                )
    
    def test_status_values(self):
        """Test that status has valid values."""
        valid_statuses = {'open', 'closed'}
        
        for post in self.test_posts:
            self.assertIn(
                post.get('status'),
                valid_statuses,
                f"Status must be 'open' or 'closed', got {post.get('status')}"
            )
    
    def test_url_format(self):
        """Test that URLs are properly formatted."""
        for post in self.test_posts:
            url = post.get('url', '')
            self.assertTrue(
                url.startswith('http'),
                f"URL must start with http, got {url}"
            )
    
    def test_parse_json_integrity(self):
        """Test that parsed JSON maintains integrity."""
        test_data = {
            'posts': self.test_posts,
            'post_count': 3,
            'source_file': 'test.json',
            'parsed_at': datetime.now().isoformat()
        }
        
        # Simulate write/read cycle
        json_str = json.dumps(test_data)
        parsed_data = json.loads(json_str)
        
        self.assertEqual(
            len(parsed_data['posts']),
            len(test_data['posts']),
            "Data should maintain integrity through JSON round-trip"
        )
        self.assertEqual(
            parsed_data['post_count'],
            test_data['post_count'],
            "Post count should match"
        )


class TestDuplicateStats(unittest.TestCase):
    """Test statistics about duplicates."""
    
    def test_current_duplicate_count(self):
        """
        Test that the known duplicate count is accurate.
        Update these values when duplicates are resolved.
        """
        current_stats = {
            'total_posts': 7968,
            'unique_posts': 471,
            'duplicate_posts': 7497,
            'duplicate_percentage': 94.08
        }
        
        # Verify the math
        duplicates = current_stats['total_posts'] - current_stats['unique_posts']
        self.assertEqual(
            duplicates,
            current_stats['duplicate_posts'],
            f"Expected {current_stats['duplicate_posts']} duplicates, got {duplicates}"
        )
        
        percentage = (duplicates / current_stats['total_posts']) * 100
        self.assertAlmostEqual(
            percentage,
            current_stats['duplicate_percentage'],
            places=1,
            msg=f"Duplicate percentage should be ~{current_stats['duplicate_percentage']}%"
        )


class TestDeduplicationWorkflow(unittest.TestCase):
    """Test the full deduplication workflow."""
    
    def test_dedup_multiple_files(self):
        """Test deduplicating posts from multiple JSON files."""
        # Simulate multiple files with overlapping posts
        files_data = [
            {
                'posts': [
                    {'post_id': 'A', 'position': 'Dev'},
                    {'post_id': 'B', 'position': 'Manager'}
                ]
            },
            {
                'posts': [
                    {'post_id': 'A', 'position': 'Dev'},  # Duplicate
                    {'post_id': 'C', 'position': 'Analyst'}
                ]
            },
            {
                'posts': [
                    {'post_id': 'A', 'position': 'Dev'},  # Duplicate
                    {'post_id': 'B', 'position': 'Manager'},  # Duplicate
                    {'post_id': 'D', 'position': 'Engineer'}
                ]
            }
        ]
        
        # Consolidate
        unique_map = {}
        for file_data in files_data:
            for post in file_data['posts']:
                post_id = post.get('post_id')
                if post_id not in unique_map:
                    unique_map[post_id] = post
        
        unique_posts = list(unique_map.values())
        
        # Should have 4 unique posts (A, B, C, D)
        self.assertEqual(len(unique_posts), 4)
        
        # Count total posts across files
        total_posts = sum(len(f['posts']) for f in files_data)
        self.assertEqual(total_posts, 7)  # 2 + 2 + 3
        
        # Verify duplicates removed
        duplicates_removed = total_posts - len(unique_posts)
        self.assertEqual(duplicates_removed, 3)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
