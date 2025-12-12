#!/usr/bin/env python3
"""
Universal file watcher and server reloader (like nodemon for Node.js).
Monitors file changes and automatically restarts the dashboard server.
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class DashboardServerHandler(FileSystemEventHandler):
    """Handles file system events and restarts the server."""
    
    def __init__(self, server_process):
        self.server_process = server_process
        self.last_restart = time.time()
        self.restart_delay = 1  # Wait 1 second before restarting
        self.restart_scheduled = False
    
    def on_modified(self, event):
        """Handle file modification."""
        if self._should_restart(event):
            self._schedule_restart()
    
    def on_created(self, event):
        """Handle file creation."""
        if self._should_restart(event):
            self._schedule_restart()
    
    def _should_restart(self, event):
        """Determine if we should restart the server."""
        # Ignore certain files
        if event.is_directory:
            return False
        
        path = Path(event.src_path)
        
        # Watch these file types
        watched_extensions = {'.html', '.py', '.css', '.js', '.json'}
        if path.suffix not in watched_extensions:
            return False
        
        # Ignore certain directories
        ignored_dirs = {'.git', '__pycache__', '.pytest_cache', 'venv', '.venv', 'node_modules'}
        for ignored in ignored_dirs:
            if ignored in path.parts:
                return False
        
        return True
    
    def _schedule_restart(self):
        """Schedule a server restart."""
        if self.restart_scheduled:
            return
        
        self.restart_scheduled = True
        time.sleep(self.restart_delay)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] ⟳ File changed, restarting dashboard server...")
        
        # Kill the current server
        if self.server_process and self.server_process.poll() is None:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
        
        # Restart the server
        try:
            self.server_process = start_server()
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✓ Dashboard server restarted")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✗ Error restarting server: {e}")
        
        self.restart_scheduled = False


def start_server():
    """Start the dashboard server."""
    return subprocess.Popen(
        ['python3', 'dashboard_server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )


def monitor_server_output(process):
    """Monitor and print server output in a separate thread."""
    try:
        for line in process.stdout:
            print(f"[SERVER] {line.rstrip()}")
    except:
        pass


def main():
    """Main entry point."""
    print("=" * 70)
    print("Dashboard Server Auto-Reloader (like nodemon for Node.js)")
    print("=" * 70)
    
    # Start the server
    print("\n📊 Starting dashboard server...\n")
    server_process = start_server()
    
    # Start monitoring server output
    import threading
    output_thread = threading.Thread(target=monitor_server_output, args=(server_process,), daemon=True)
    output_thread.start()
    
    # Set up file system observer
    observer = Observer()
    event_handler = DashboardServerHandler(server_process)
    
    # Watch current directory and subdirectories
    watch_path = Path.cwd()
    observer.schedule(event_handler, str(watch_path), recursive=True)
    
    print(f"👁️  Watching for changes in: {watch_path}")
    print("📁 Monitored file types: .html, .py, .css, .js, .json")
    print("🔄 Press Ctrl+C to stop\n")
    
    observer.start()
    
    try:
        while True:
            # Keep the main thread alive
            if server_process.poll() is not None:
                print("⚠️  Server process ended unexpectedly, restarting...")
                event_handler.server_process = start_server()
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping file watcher and server...")
        observer.stop()
        
        if server_process and server_process.poll() is None:
            server_process.terminate()
            try:
                server_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                server_process.kill()
        
        print("✓ Server stopped gracefully")
        sys.exit(0)
    finally:
        observer.join()


if __name__ == '__main__':
    # Check if watchdog is installed
    try:
        import watchdog
    except ImportError:
        print("Error: watchdog module not installed")
        print("\nInstall it with:")
        print("  pip install watchdog")
        sys.exit(1)
    
    main()
