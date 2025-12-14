#!/usr/bin/env python3
"""
Development server for Quiet-Quail dashboard with auto-reload on file changes.
Similar to nodemon for Node.js - watches for file changes and restarts the server.
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ServerProcessHandler(FileSystemEventHandler):
    """Handle file changes and restart the server."""
    
    def __init__(self, port=8000):
        super().__init__()
        self.port = port
        self.process = None
        self.restart_pending = False
        self.debounce_time = 0.5
        self.last_restart = 0
        
        # Start the initial server
        self.start_server()
    
    def start_server(self):
        """Start the dashboard server process."""
        try:
            if self.process and self.process.poll() is None:
                print("⚠ Stopping previous server instance...")
                self.process.terminate()
                try:
                    self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
            
            print(f"\n{'='*60}")
            print(f"🚀 Starting dashboard server on port {self.port}...")
            print(f"{'='*60}")
            
            # Start the server process
            project_root = Path(__file__).parent.parent
            os.chdir(project_root / 'web')
            
            self.process = subprocess.Popen(
                [sys.executable, 'dashboard_server.py', str(self.port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Print server output
            while True:
                line = self.process.stdout.readline()
                if not line:
                    break
                print(line.rstrip())
                # Check if server started successfully
                if 'Server running at' in line:
                    print(f"✓ Server ready! Watching for changes...")
                    print(f"📁 Watching: {project_root}/web/")
                    print(f"📁 Watching: {project_root}/data/")
                    print(f"📝 Files: .html, .css, .js, .json")
                    print(f"{'='*60}\n")
                    break
            
            self.last_restart = time.time()
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            sys.exit(1)
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        # Only watch relevant file types
        relevant_extensions = {'.html', '.css', '.js', '.json', '.py'}
        file_ext = Path(event.src_path).suffix.lower()
        
        if file_ext not in relevant_extensions:
            return
        
        # Debounce restarts
        current_time = time.time()
        if current_time - self.last_restart < self.debounce_time:
            return
        
        file_name = Path(event.src_path).name
        print(f"\n⚡ File changed: {file_name}")
        self.schedule_restart()
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        relevant_extensions = {'.html', '.css', '.js', '.json', '.py'}
        file_ext = Path(event.src_path).suffix.lower()
        
        if file_ext not in relevant_extensions:
            return
        
        file_name = Path(event.src_path).name
        print(f"\n📄 File created: {file_name}")
        self.schedule_restart()
    
    def schedule_restart(self):
        """Schedule a server restart."""
        current_time = time.time()
        if current_time - self.last_restart < self.debounce_time:
            self.restart_pending = True
            return
        
        self.restart_pending = False
        print(f"🔄 Restarting server...")
        self.start_server()


def setup_watchers(handler, port):
    """Set up file system watchers."""
    project_root = Path(__file__).parent.parent
    
    # Directories to watch
    watch_dirs = [
        project_root / 'web',
        project_root / 'data',
    ]
    
    observer = Observer()
    
    for watch_dir in watch_dirs:
        if watch_dir.exists():
            observer.schedule(handler, str(watch_dir), recursive=True)
            print(f"👀 Watching: {watch_dir}")
    
    observer.start()
    return observer


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    print("\n\n⏹ Shutting down...")
    sys.exit(0)


def main():
    """Main entry point."""
    port = 8000
    
    # Check for port argument
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Usage: {sys.argv[0]} [port]")
            sys.exit(1)
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print(f"\n{'='*60}")
    print(f"🎯 Quiet-Quail Dashboard - Development Mode")
    print(f"{'='*60}")
    
    # Create handler and start server
    handler = ServerProcessHandler(port=port)
    
    # Set up file watchers
    observer = setup_watchers(handler, port)
    
    try:
        # Keep the observer running
        while True:
            time.sleep(1)
            
            # Check if restart is pending
            if handler.restart_pending:
                current_time = time.time()
                if current_time - handler.last_restart >= handler.debounce_time:
                    handler.restart_pending = False
                    print(f"🔄 Restarting server...")
                    handler.start_server()
    
    except KeyboardInterrupt:
        print("\n\n⏹ Shutting down file watcher...")
        observer.stop()
    
    observer.join()
    
    # Terminate server process
    if handler.process and handler.process.poll() is None:
        handler.process.terminate()
        try:
            handler.process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            handler.process.kill()
    
    print("✓ Shutdown complete")


if __name__ == '__main__':
    main()
