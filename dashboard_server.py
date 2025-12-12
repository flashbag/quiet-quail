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
from urllib.parse import urlparse, parse_qs

PORT = 8000
HOST = '0.0.0.0'


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler with CORS headers and JSON API support."""
    
    def do_GET(self):
        """Handle GET requests with CORS headers."""
        # Parse the URL
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Add CORS headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json' if path.endswith('.json') else 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        
        # Handle API endpoints
        if path == '/api/files':
            self.serve_file_list()
        elif path.startswith('/saved_json/'):
            self.serve_json_file(path)
        elif path == '/' or path == '':
            self.serve_dashboard()
        else:
            self.serve_static_file(path)
    
    def serve_dashboard(self):
        """Serve the main dashboard HTML."""
        dashboard_path = Path('dashboard.html')
        if dashboard_path.exists():
            with open(dashboard_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.wfile.write(b'Dashboard not found')
    
    def serve_file_list(self):
        """Serve the API file list as JSON."""
        api_path = Path('api/list-json-files.json')
        if api_path.exists():
            with open(api_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            # Generate on the fly if doesn't exist
            self.generate_file_list()
    
    def serve_json_file(self, path):
        """Serve a specific JSON file."""
        file_path = Path(path.lstrip('/'))
        if file_path.exists() and file_path.suffix == '.json':
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.wfile.write(json.dumps({'error': 'File not found'}).encode())
    
    def serve_static_file(self, path):
        """Serve static files."""
        file_path = Path(path.lstrip('/'))
        if file_path.exists() and file_path.is_file():
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.wfile.write(b'File not found')
    
    def generate_file_list(self):
        """Generate and serve the file list."""
        saved_json_dir = Path('saved_json')
        files_list = []
        
        if saved_json_dir.exists():
            for json_file in sorted(saved_json_dir.rglob('*.json')):
                relative_path = json_file.relative_to('.')
                files_list.append({
                    'path': str(relative_path),
                    'name': json_file.stem,
                    'date': str(json_file.parent)
                })
        
        response = json.dumps({
            'files': files_list,
            'count': len(files_list)
        })
        self.wfile.write(response.encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom logging."""
        print(f"[{self.client_address[0]}] {format % args}")


def run_server():
    """Run the HTTP server."""
    os.chdir(Path(__file__).parent)
    
    with socketserver.TCPServer((HOST, PORT), DashboardHandler) as httpd:
        print("=" * 60)
        print("Quiet-Quail Dashboard Server")
        print("=" * 60)
        print(f"Server running at: http://localhost:{PORT}")
        print(f"Press Ctrl+C to stop")
        print("=" * 60)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == '__main__':
    run_server()
