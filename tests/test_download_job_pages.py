#!/usr/bin/env python3
"""
Unit tests for download_job_pages.py

Tests core functions:
- get_job_page_path: Path generation logic
- extract_main_content: HTML content extraction
- is_already_downloaded: File existence checks
- log_cron_stats: Statistics logging
"""

import unittest
import tempfile
import json
from pathlib import Path
import sys
import os

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from download_job_pages import (
    get_job_page_path,
    extract_main_content,
    is_already_downloaded,
    is_job_closed,
    log_cron_stats
)


class TestJobPagePath(unittest.TestCase):
    """Test get_job_page_path function."""
    
    def test_path_generation(self):
        """Test correct path generation for job IDs."""
        path = get_job_page_path(123456)
        expected = Path('data/job-pages/123/456/job_123456.html')
        self.assertEqual(path, expected)
    
    def test_path_with_small_id(self):
        """Test path generation with small job ID."""
        path = get_job_page_path(42)
        expected = Path('data/job-pages/000/042/job_42.html')
        self.assertEqual(path, expected)
    
    def test_path_with_large_id(self):
        """Test path with large job ID."""
        path = get_job_page_path(999999)
        expected = Path('data/job-pages/999/999/job_999999.html')
        self.assertEqual(path, expected)


class TestExtractMainContent(unittest.TestCase):
    """Test extract_main_content function."""
    
    def test_extract_from_main_tag(self):
        """Test extraction from <main> tag."""
        html = '<html><body><main><h1>Job Title</h1><p>Description</p></main></body></html>'
        result = extract_main_content(html)
        self.assertIn('Job Title', result)
        self.assertIn('Description', result)
    
    def test_remove_scripts(self):
        """Test that scripts are removed."""
        html = '<html><body><script>alert("bad")</script><p>Good content</p></body></html>'
        result = extract_main_content(html)
        self.assertNotIn('alert', result)
        self.assertIn('Good content', result)
    
    def test_remove_styles(self):
        """Test that style tags are removed."""
        html = '<html><body><style>.bad { color: red; }</style><p>Text</p></body></html>'
        result = extract_main_content(html)
        self.assertNotIn('color', result)
        self.assertIn('Text', result)
    
    def test_empty_html(self):
        """Test with empty HTML."""
        result = extract_main_content('')
        self.assertEqual(result, '')
    
    def test_html_without_content_tags(self):
        """Test with HTML without standard content tags."""
        html = '<html><body><div>Some content here</div></body></html>'
        result = extract_main_content(html)
        self.assertIn('Some content', result)


class TestIsAlreadyDownloaded(unittest.TestCase):
    """Test is_already_downloaded function."""
    
    def setUp(self):
        """Create temporary directory for tests."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir.name)
    
    def tearDown(self):
        """Clean up temporary directory."""
        os.chdir(self.original_cwd)
        self.temp_dir.cleanup()
    
    def test_file_not_exists(self):
        """Test when file doesn't exist."""
        result = is_already_downloaded(999999)
        self.assertFalse(result)
    
    def test_file_exists_with_valid_html(self):
        """Test when valid HTML file exists."""
        post_id = 123456
        path = get_job_page_path(post_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create valid HTML file
        html_content = '<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>Test</body></html>'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        result = is_already_downloaded(post_id)
        self.assertTrue(result)
    
    def test_file_empty(self):
        """Test when file is empty."""
        post_id = 111111
        path = get_job_page_path(post_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create empty file
        with open(path, 'w') as f:
            pass
        
        result = is_already_downloaded(post_id)
        self.assertFalse(result)
    
    def test_file_without_meta_charset(self):
        """Test when file has no meta charset tag."""
        post_id = 222222
        path = get_job_page_path(post_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create HTML without meta charset
        html_content = '<!DOCTYPE html><html><body>Test</body></html>'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        result = is_already_downloaded(post_id)
        self.assertFalse(result)


class TestIsJobClosed(unittest.TestCase):
    """Test is_job_closed function."""
    
    def setUp(self):
        """Create temporary directory for tests."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir.name)
    
    def tearDown(self):
        """Clean up temporary directory."""
        os.chdir(self.original_cwd)
        self.temp_dir.cleanup()
    
    def test_job_not_exists(self):
        """Test when job file doesn't exist."""
        result = is_job_closed(999999)
        self.assertFalse(result)
    
    def test_open_job(self):
        """Test open job marking."""
        post_id = 333333
        path = get_job_page_path(post_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        html_content = '<html><body><p>Job is open</p></body></html>'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        result = is_job_closed(post_id)
        self.assertFalse(result)
    
    def test_closed_job(self):
        """Test closed job detection."""
        post_id = 444444
        path = get_job_page_path(post_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        html_content = '<html><body><p>На жаль, вакансія вже закрита!</p></body></html>'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        result = is_job_closed(post_id)
        self.assertTrue(result)


class TestLogCronStats(unittest.TestCase):
    """Test log_cron_stats function."""
    
    def setUp(self):
        """Create temporary directory for tests."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir.name)
    
    def tearDown(self):
        """Clean up temporary directory."""
        os.chdir(self.original_cwd)
        self.temp_dir.cleanup()
    
    def test_stats_file_creation(self):
        """Test that stats file is created."""
        log_cron_stats(5, 3, 3, 0, 8, 10, 0)
        
        stats_file = Path('logs/cron_stats.jsonl')
        self.assertTrue(stats_file.exists())
    
    def test_stats_file_content(self):
        """Test that stats are correctly written."""
        log_cron_stats(5, 3, 3, 0, 8, 10, 0)
        
        stats_file = Path('logs/cron_stats.jsonl')
        with open(stats_file, 'r') as f:
            line = f.readline()
            stats = json.loads(line)
        
        self.assertEqual(stats['new_jobs_found'], 5)
        self.assertEqual(stats['jobs_downloaded'], 3)
        self.assertEqual(stats['download_successful'], 3)
        self.assertEqual(stats['download_failed'], 0)
        self.assertEqual(stats['metadata_generated'], 8)
        self.assertIn('timestamp', stats)
    
    def test_stats_appending(self):
        """Test that multiple stats are appended."""
        log_cron_stats(5, 3, 3, 0, 8, 10, 0)
        log_cron_stats(2, 1, 1, 0, 3, 5, 0)
        
        stats_file = Path('logs/cron_stats.jsonl')
        with open(stats_file, 'r') as f:
            lines = f.readlines()
        
        self.assertEqual(len(lines), 2)


class TestIntegration(unittest.TestCase):
    """Integration tests for script components."""
    
    def setUp(self):
        """Create temporary directory for tests."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir.name)
    
    def tearDown(self):
        """Clean up temporary directory."""
        os.chdir(self.original_cwd)
        self.temp_dir.cleanup()
    
    def test_download_check_flow(self):
        """Test the download checking flow."""
        post_id = 555555
        
        # Should not be downloaded initially
        self.assertFalse(is_already_downloaded(post_id))
        
        # Create a valid job file
        path = get_job_page_path(post_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        html_content = '<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>Job</body></html>'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Should now be marked as downloaded
        self.assertTrue(is_already_downloaded(post_id))


if __name__ == '__main__':
    unittest.main()
