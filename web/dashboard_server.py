#!/usr/bin/env python3
"""
Simple HTTP server to serve the dashboard with CORS support.
Serves the Quiet-Quail dashboard and JSON data.
"""

import http.server
import socketserver
import os
import json
from pathlib import Path
from urllib.parse import urlparse

PORT = 8000
HOST = '127.0.0.1'


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler with CORS headers and JSON API support."""
    
    def do_GET(self):
        """Handle GET requests with CORS headers."""
        # Parse the URL
        path = urlparse(self.path).path
        
        # Handle API endpoints
        if path == '/api/files':
            self.serve_file_list()
        elif path.startswith('/data/'):
            self.serve_json_file(path)
        elif path == '/' or path == '':
            self.serve_file('dashboard.html', 'text/html; charset=utf-8')
        else:
            # Try to serve static files
            try:
                self.serve_file(path.lstrip('/'), None)
            except FileNotFoundError:
                self.send_error(404)
    
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
            # Try to use pre-generated API file first
            api_file = Path('api/list-json-files.json')
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
            
            # Fallback: scan data directory
            data_dir = Path('data')
            files_list = []
            
            if data_dir.exists():
                for json_file in sorted(data_dir.rglob('*.json'), reverse=True):
                    # Skip consolidated_unique.json in the listing (handle separately)
                    if json_file.name == 'consolidated_unique.json':
                        continue
                    relative_path = json_file.relative_to('.')
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
    
    try:
        with socketserver.TCPServer((HOST, PORT), DashboardHandler) as httpd:
            print("=" * 60)
            print("Quiet-Quail Dashboard Server")
            print("=" * 60)
            print(f"✓ Server running at: http://{HOST}:{PORT}")
            print(f"✓ Open in browser: http://localhost:{PORT}")
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
