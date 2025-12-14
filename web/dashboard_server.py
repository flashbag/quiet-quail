#!/usr/bin/env python3
"""
Simple HTTP server to serve the dashboard with CORS support.
Serves the Quiet-Quail dashboard and JSON data.
"""

import http.server
import socketserver
import os
import json
import sys
import re
from pathlib import Path
from urllib.parse import urlparse

PORT = 8000
HOST = '127.0.0.1'


def get_port():
    """Get port from command line argument or environment variable."""
    # Check for environment variable (set by tests)
    if 'DASHBOARD_PORT' in os.environ:
        return int(os.environ['DASHBOARD_PORT'])
    # Check for command line argument
    if len(sys.argv) > 1:
        try:
            return int(sys.argv[1])
        except ValueError:
            pass
    return PORT


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler with CORS headers and JSON API support."""
    
    def do_GET(self):
        """Handle GET requests with CORS headers."""
        # Parse the URL
        path = urlparse(self.path).path
        
        # Handle API endpoints
        if path == '/api/files':
            self.serve_file_list()
        elif path == '/api/downloaded-jobs':
            self.serve_downloaded_jobs()
        elif path.startswith('/api/job-content/'):
            self.serve_job_content(path)
        elif path.startswith('/data/'):
            # Serve data files (JSON, etc)
            self.serve_data_file(path)
        elif path == '/' or path == '':
            self.serve_file('dashboard.html', 'text/html; charset=utf-8')
        else:
            # Try to serve static files
            try:
                self.serve_file(path.lstrip('/'), None)
            except FileNotFoundError:
                self.send_error(404)
    
    def serve_data_file(self, path):
        """Serve data files (JSON) from the data directory."""
        # Remove /data/ prefix and construct safe path
        relative_path = path[6:]  # Remove '/data/'
        
        # Security: prevent directory traversal
        if '..' in relative_path or relative_path.startswith('/'):
            self.send_error(403)
            return
        
        # Construct full path
        project_root = Path(__file__).parent.parent
        file_path = project_root / 'data' / relative_path
        
        # Verify file is within data directory
        try:
            file_path.resolve().relative_to(project_root.resolve() / 'data')
        except ValueError:
            self.send_error(403)
            return
        
        if not file_path.exists() or not file_path.is_file():
            self.send_error(404)
            return
        
        # Read and serve file
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, str(e))

    def serve_file(self, file_path, content_type=None):
        """Serve a static file with proper headers."""
        file_path = Path(file_path)
        
        # Security: prevent directory traversal
        if '..' in str(file_path):
            self.send_error(403)
            return
        
        if not file_path.exists() or not file_path.is_file():
            self.send_error(404)
            return
        
        # Determine content type
        if content_type is None:
            if str(file_path).endswith('.json'):
                content_type = 'application/json'
            elif str(file_path).endswith('.html'):
                content_type = 'text/html; charset=utf-8'
            elif str(file_path).endswith('.css'):
                content_type = 'text/css'
            elif str(file_path).endswith('.js'):
                content_type = 'application/javascript'
            else:
                content_type = 'application/octet-stream'
        
        # Read and serve file
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_file_list(self):
        """Serve the file list as JSON."""
        try:
            # Get project root
            project_root = Path(__file__).parent.parent
            
            # Try to use pre-generated API file first
            api_file = project_root / 'api' / 'list-json-files.json'
            if api_file.exists():
                with open(api_file, 'r') as f:
                    response = f.read().encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Length', len(response))
                self.end_headers()
                self.wfile.write(response)
                return
            
            # Fallback: scan data directory for JSON files
            data_dir = project_root / 'data'
            files_list = []
            
            if data_dir.exists():
                # Find all JSON files in data directory (recursive)
                for json_file in sorted(data_dir.rglob('*.json'), reverse=True):
                    # Skip analysis directory JSON files and consolidated files
                    if 'analysis' in json_file.parts or json_file.name in ['consolidated_unique.json', 'downloaded_urls.json']:
                        continue
                    # Skip job-pages directory (these are HTML not analysis JSON)
                    if 'job-pages' in json_file.parts:
                        continue
                    relative_path = json_file.relative_to(project_root)
                    files_list.append({
                        'path': str(relative_path),
                        'name': json_file.stem,
                        'date': str(json_file.parent)
                    })
            
            response = json.dumps({
                'files': files_list,
                'count': len(files_list)
            }).encode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', len(response))
            self.end_headers()
            self.wfile.write(response)
        except Exception as e:
            self.send_error(500, str(e))

    def serve_downloaded_jobs(self):
        """Serve list of job IDs that have downloaded HTML pages."""
        try:
            project_root = Path(__file__).parent.parent
            job_pages_dir = project_root / 'data' / 'job-pages'
            downloaded_jobs = {}
            
            # Find all downloaded job pages
            if job_pages_dir.exists():
                for job_file in sorted(job_pages_dir.rglob('job_*.html')):
                    # Extract post_id from filename (job_12345.html -> 12345)
                    try:
                        post_id = int(job_file.stem.split('_')[1])
                        # Check if file is valid (non-empty, contains DOCTYPE)
                        file_size = job_file.stat().st_size
                        if file_size > 0:
                            with open(job_file, 'r', encoding='utf-8') as f:
                                content = f.read(500)
                                if '<!DOCTYPE html>' in content:
                                    # Get relative path from data root
                                    rel_path = job_file.relative_to(project_root / 'data')
                                    downloaded_jobs[str(post_id)] = {
                                        'path': f'/data/{rel_path}',
                                        'size': file_size
                                    }
                    except (ValueError, OSError):
                        continue
            
            response = json.dumps({
                'downloaded': downloaded_jobs,
                'count': len(downloaded_jobs)
            }).encode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', len(response))
            self.end_headers()
            self.wfile.write(response)
        except Exception as e:
            self.send_error(500, str(e))

    def extract_main_content(self, html_content):
        """Extract main job posting content from HTML."""
        try:
            # Remove scripts and styles
            html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            
            # Try to find main article/content area
            # Look for common patterns: main, article, .content, .job-posting, etc.
            patterns = [
                r'<main[^>]*>(.*?)</main>',
                r'<article[^>]*>(.*?)</article>',
                r'<div[^>]*class="[^"]*(?:content|main|posting)[^"]*"[^>]*>(.*?)</div>',
                r'<section[^>]*>(.*?)</section>',
            ]
            
            main_content = None
            for pattern in patterns:
                match = re.search(pattern, html_content, flags=re.DOTALL | re.IGNORECASE)
                if match:
                    main_content = match.group(1)
                    break
            
            # Fallback: find the largest div or section
            if not main_content:
                divs = re.findall(r'<div[^>]*>(.*?)</div>', html_content, flags=re.DOTALL | re.IGNORECASE)
                if divs:
                    main_content = max(divs, key=len)
            
            # If still nothing, use body content
            if not main_content:
                body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, flags=re.DOTALL | re.IGNORECASE)
                if body_match:
                    main_content = body_match.group(1)
                else:
                    main_content = html_content
            
            # Clean up: remove navigation, footer, headers, sidebars
            main_content = re.sub(r'<nav[^>]*>.*?</nav>', '', main_content, flags=re.DOTALL | re.IGNORECASE)
            main_content = re.sub(r'<footer[^>]*>.*?</footer>', '', main_content, flags=re.DOTALL | re.IGNORECASE)
            main_content = re.sub(r'<header[^>]*>.*?</header>', '', main_content, flags=re.DOTALL | re.IGNORECASE)
            main_content = re.sub(r'<aside[^>]*>.*?</aside>', '', main_content, flags=re.DOTALL | re.IGNORECASE)
            
            # Remove common non-content elements
            main_content = re.sub(r'<div[^>]*class="[^"]*(?:sidebar|nav|menu|ad)[^"]*"[^>]*>.*?</div>', '', main_content, flags=re.DOTALL | re.IGNORECASE)
            
            # Clean up excessive whitespace
            main_content = re.sub(r'\s+', ' ', main_content)
            main_content = main_content.strip()
            
            return main_content[:50000] if main_content else ""  # Limit to 50KB
        except Exception as e:
            return ""

    def serve_job_content(self, path):
        """Serve extracted main content from a job HTML page."""
        try:
            # Extract post_id from path (/api/job-content/12345 -> 12345)
            post_id = path.split('/')[-1]
            
            # Security: validate post_id is numeric
            if not post_id.isdigit():
                self.send_error(400)
                return
            
            project_root = Path(__file__).parent.parent
            
            # Try to find the job file in organized structure (ID-based)
            # Format: data/job-pages/XXX/YYY/job_XXXYYYY.html
            job_file = None
            job_pages_dir = project_root / 'data' / 'job-pages'
            
            if job_pages_dir.exists():
                # Search for the job file recursively
                for found_file in job_pages_dir.rglob(f'job_{post_id}.html'):
                    job_file = found_file
                    break
            
            if not job_file or not job_file.exists():
                self.send_error(404)
                return
            
            # Security: verify file is within job-pages directory
            try:
                job_file.resolve().relative_to(job_pages_dir.resolve())
            except ValueError:
                self.send_error(403)
                return
            
            # Read HTML file
            with open(job_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Extract main content
            main_content = self.extract_main_content(html_content)
            
            # Return as JSON
            response = json.dumps({
                'post_id': post_id,
                'content': main_content,
                'success': bool(main_content)
            }).encode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', len(response))
            self.end_headers()
            self.wfile.write(response)
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_json_file(self, path):
        """Serve a specific JSON file."""
        try:
            file_path = Path(path.lstrip('/'))
            self.serve_file(str(file_path), 'application/json')
        except Exception as e:
            self.send_error(500, str(e))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom logging - only log errors."""
        if args[0] not in (200, 304):
            print(f"[{self.client_address[0]}] {format % args}")


def run_server():
    """Run the HTTP server."""
    os.chdir(Path(__file__).parent)
    port = get_port()
    
    try:
        with socketserver.TCPServer((HOST, port), DashboardHandler) as httpd:
            print("=" * 60)
            print("Quiet-Quail Dashboard Server")
            print("=" * 60)
            print(f"✓ Server running at: http://{HOST}:{port}")
            print(f"✓ Open in browser: http://localhost:{port}")
            print(f"✓ Press Ctrl+C to stop")
            print("=" * 60)
            
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"Error: Port {PORT} is already in use")
            print("Try: lsof -i :{PORT} to find the process")
        else:
            print(f"Error: {e}")
        exit(1)
    except KeyboardInterrupt:
        print("\n✓ Server stopped.")


if __name__ == '__main__':
    run_server()
