# Dashboard Auto-Reload (like nodemon for Node.js)

## Overview

A universal file watcher that monitors your project files and automatically restarts the dashboard server when changes are detected. No need to manually restart the server anymore!

## Quick Start

### Option 1: Using the Shell Script (Recommended)
```bash
./dashboard-watch.sh
```

Or:
```bash
bash dashboard-watch.sh
```

### Option 2: Using Python Directly
```bash
python3 run_dashboard_watch.py
```

## Features

✅ **Auto-restart on file changes** - Dashboard server restarts instantly
✅ **Smart file filtering** - Only watches relevant files (.html, .py, .css, .js, .json)
✅ **Ignores build directories** - Skips .git, __pycache__, venv, etc.
✅ **Clean server output** - Shows server logs with timestamps
✅ **Graceful shutdown** - Press Ctrl+C to stop cleanly
✅ **Like nodemon** - Same experience as Node.js development

## Monitored File Types

- `.html` - Dashboard and web pages
- `.py` - Python scripts
- `.css` - Stylesheets
- `.js` - JavaScript files
- `.json` - Data files

## Ignored Directories

Files in these directories are ignored:
- `.git/` - Version control
- `__pycache__/` - Python cache
- `.pytest_cache/` - Test cache
- `venv/` or `.venv/` - Virtual environments
- `node_modules/` - Node packages

## Usage Examples

### Start with auto-reload
```bash
./dashboard-watch.sh
```

### What you'll see
```
==========================================
Dashboard Server with Auto-Reload
==========================================

📊 Starting dashboard server...

👁️  Watching for changes in: /Users/user/Projects/Quiet-Quail
📁 Monitored file types: .html, .py, .css, .js, .json
🔄 Press Ctrl+C to stop

============================================================
Quiet-Quail Dashboard Server
============================================================
✓ Server running at: http://127.0.0.1:8000
✓ Open in browser: http://localhost:8000
✓ Press Ctrl+C to stop
============================================================
```

### Edit a file
When you edit any monitored file:

```
[2025-12-12 22:30:45] ⟳ File changed, restarting dashboard server...
[2025-12-12 22:30:46] ✓ Dashboard server restarted
```

Server restarts within 1-2 seconds. Refresh your browser to see changes!

## Installation

### Install Dependencies
```bash
# Using pip
pip install watchdog

# Or as part of project setup
pip install -r requirements.txt
```

### Update requirements.txt
```bash
pip freeze | grep watchdog >> requirements.txt
```

## Architecture

### Files

1. **`run_dashboard_watch.py`** - Main watcher script
   - Uses `watchdog` library for file system events
   - Manages server process lifecycle
   - Implements smart restart logic

2. **`dashboard-watch.sh`** - Convenience shell wrapper
   - Easy one-command startup
   - Automatic dependency checking
   - Better user experience

### How It Works

```
┌─────────────────┐
│  File Watcher   │ (monitoring filesystem)
└────────┬────────┘
         │
         ├─► File changed?
         │
         ├─► Should restart? (check extension, path)
         │
         ├─► Terminate current server
         │
         ├─► Start new server
         │
         └─► Print status
```

## Common Issues

### Issue: "watchdog not found"
**Solution:**
```bash
pip install watchdog
```

### Issue: "Port 8000 already in use"
**Solution:** Find and kill the process:
```bash
lsof -i :8000
kill -9 <PID>
```

Then restart the watcher.

### Issue: Server doesn't restart
**Solution:** Check file permissions:
```bash
chmod +x dashboard-watch.sh
```

Ensure the file is in a monitored directory (.html, .py, .css, .js, .json).

## Comparison: Before vs After

### Before (Manual)
```bash
# Terminal 1
python3 dashboard_server.py

# Edit dashboard.html...
# Ctrl+C to stop
# python3 dashboard_server.py to restart
# Repeat every time...
```

### After (Automatic)
```bash
# Terminal 1
./dashboard-watch.sh

# Edit dashboard.html...
# Server restarts automatically ✨
# Just refresh browser!
```

## Performance Notes

- **Restart time**: ~1-2 seconds
- **Initial startup**: ~1 second
- **CPU usage**: Minimal (only checks file timestamps)
- **Memory**: ~30-50MB (Python watcher + server)

## Advanced Usage

### Modify watched extensions
Edit `run_dashboard_watch.py` line with `watched_extensions`:
```python
watched_extensions = {'.html', '.py', '.css', '.js', '.json', '.md'}
```

### Modify restart delay
Edit line in `run_dashboard_watch.py`:
```python
self.restart_delay = 2  # Wait 2 seconds instead of 1
```

### Ignore additional directories
Edit `ignored_dirs` in `run_dashboard_watch.py`:
```python
ignored_dirs = {'.git', '__pycache__', 'build', 'dist'}
```

## Development Workflow

1. **Start the watcher** once in the morning:
   ```bash
   ./dashboard-watch.sh
   ```

2. **Open browser** to http://localhost:8000

3. **Edit files** freely - server auto-restarts

4. **Refresh browser** to see changes

5. **Done** - no manual server restarts needed!

## Stopping the Watcher

Press `Ctrl+C` in the terminal:

```
^C

🛑 Stopping file watcher and server...
✓ Server stopped gracefully
```

## Related Scripts

- `dashboard_server.py` - The actual HTTP server
- `run_dashboard_watch.py` - File watcher and auto-reloader
- `dashboard-watch.sh` - Convenience shell script (this one!)

## Requirements

- Python 3.6+
- watchdog library (`pip install watchdog`)
- Bash shell (for .sh script)

## Notes

- Works on macOS, Linux, and Windows
- Safe to use in development (not for production)
- Zero configuration needed
- Restarts are graceful (existing connections handled properly)

---

*Made for Quiet-Quail dashboard development*
*Inspired by nodemon for Node.js*
