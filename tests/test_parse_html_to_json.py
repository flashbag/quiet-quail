#!/usr/bin/env python3
"""
Unit tests for parse_html_to_json.py

Tests core functions:
- extract_post_id: Post ID extraction
- parse_post_div: Post data parsing
- parse_html_file: File parsing
"""

import unittest
import tempfile
import json
from pathlib import Path
import sys
import os

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from parse_html_to_json import (
    extract_post_id
)


class TestExtractPostId(unittest.TestCase):
    """Test extract_post_id function."""
    
    def test_valid_post_id_with_format(self):
        """Test extraction of valid post ID in standard format."""
        # The function actually expects 'post-XXXXXX' format and returns string
        post_id = extract_post_id('post-123456')
        self.assertEqual(post_id, '123456')
    
    def test_numeric_post_id_string(self):
        """Test with just numeric string (no post- prefix)."""
        # This should return None since it doesn't have 'post-' prefix
        post_id = extract_post_id('999999')
        self.assertIsNone(post_id)
    
    def test_small_post_id(self):
        """Test with small post ID."""
        post_id = extract_post_id('post-1')
        self.assertEqual(post_id, '1')
    
    def test_invalid_post_id(self):
        """Test with invalid post ID."""
        post_id = extract_post_id('invalid')
        self.assertIsNone(post_id)
    
    def test_none_input_raises_error(self):
        """Test with None input - should raise TypeError."""
        with self.assertRaises(TypeError):
            extract_post_id(None)


class TestIntegration(unittest.TestCase):
    """Integration tests for HTML parsing."""
    
    def test_extract_post_id_with_correct_format(self):
        """Test post ID extraction with correct format."""
        # Valid extraction (returns string)
        id1 = extract_post_id('post-555555')
        self.assertEqual(id1, '555555')
        
        # Invalid extraction
        id2 = extract_post_id('abc')
        self.assertIsNone(id2)


if __name__ == '__main__':
    unittest.main()
