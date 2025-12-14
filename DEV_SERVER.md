# Dashboard Development Server (Auto-Reload)

The Quiet-Quail dashboard includes a development server with automatic reload functionality, similar to **nodemon** for Node.js.

## Features

✨ **Auto-Reload**: Automatically restarts the server when files change
📁 **Smart Watching**: Monitors HTML, CSS, JavaScript, JSON, and Python files
⚡ **Fast Debouncing**: Prevents multiple restarts from rapid file changes
🎯 **Clean Output**: Shows when files change and when server restarts
🔧 **Easy Setup**: Just run one command

## Installation

1. Install dependencies (if not already installed):
```bash
pip install -r requirements.txt
```

This will install `watchdog` which powers the file watching.

## Usage

### Run in Development Mode (Local Machine)

```bash
./dev.sh
```

Or from the web directory:
```bash
python3 dashboard_dev.py
```

### Specify Custom Port

```bash
./dev.sh 8001
```

## What Gets Watched

The dev server monitors for changes in:

- **Web files**: `web/dashboard.html`, `web/dashboard_server.py`, CSS, JavaScript
- **Data files**: `data/*.json` (triggers when new data is imported)

**File types monitored**:
- `.html` - HTML markup changes
- `.css` - Stylesheet changes  
- `.js` - JavaScript changes
- `.json` - JSON data changes
- `.py` - Python code changes (for server logic)

## Example Output

```
============================================================
🎯 Quiet-Quail Dashboard - Development Mode
============================================================
👀 Watching: /Users/user/Projects/Quiet-Quail/web
👀 Watching: /Users/user/Projects/Quiet-Quail/data

============================================================
🚀 Starting dashboard server on port 8000...
============================================================
✓ Server running at: http://127.0.0.1:8000
✓ Open in browser: http://localhost:8000
✓ Press Ctrl+C to stop
============================================================
✓ Server ready! Watching for changes...
📁 Watching: /Users/user/Projects/Quiet-Quail/web/
📁 Watching: /Users/user/Projects/Quiet-Quail/data/
📝 Files: .html, .css, .js, .json
============================================================

⚡ File changed: dashboard.html
🔄 Restarting server...
✓ Server running at: http://127.0.0.1:8000
✓ Server ready! Watching for changes...
```

## How It Works

1. **Start**: Launches the dashboard server process
2. **Watch**: File watcher monitors for changes in web and data directories
3. **Detect**: When a file changes, the watcher is notified
4. **Debounce**: Multiple rapid changes are buffered (0.5 second delay)
5. **Restart**: Gracefully terminates the old server and starts a new one
6. **Reload**: Browser auto-refresh plugins (optional) can detect the restart

## Tips

### Browser Auto-Refresh
For automatic browser refresh, install one of these extensions:
- **Chrome**: [LiveJS](https://chrome.google.com/webstore/detail/livejs/)
- **Firefox**: [LiveReload](https://addons.mozilla.org/firefox/addon/livereload-web-extension/)
- **Safari**: Built-in Live Reload support

Or use the browser's developer tools:
- Open DevTools (F12)
- Go to Sources or Network tab
- The server logs will show refresh points

### Manual Refresh
Simply refresh your browser (Cmd+R or Ctrl+R) after changes - the server is ready immediately.

### Stopping the Server

Press `Ctrl+C` to gracefully shutdown:
```
⏹ Shutting down...
⏹ Shutting down file watcher...
✓ Shutdown complete
```

## Troubleshooting

### "watchdog not found"
Install it manually:
```bash
pip install watchdog>=4.0.0
```

### Port Already in Use
Specify a different port:
```bash
./dev.sh 8001
```

Or kill the process using the port:
```bash
lsof -i :8000 | awk 'NR>1 {print $2}' | xargs kill -9
```

### Files Not Being Watched
Ensure files are being created in the monitored directories:
- `web/` - Dashboard files
- `data/` - Data files

Add more watch directories by editing `dashboard_dev.py` in the `setup_watchers()` function.

## Comparison: dev.sh vs dashboard_server.py

| Feature | `dev.sh` | `dashboard_server.py` |
|---------|----------|----------------------|
| Auto-reload | ✓ Yes | ✗ No |
| File watching | ✓ Yes | ✗ No |
| Production-ready | ✗ No | ✓ Yes |
| Overhead | Higher | Lower |
| Use case | Development | Production |

## Production Deployment

For production servers, use the standard server without dev mode:

```bash
# Simple start
python3 web/dashboard_server.py

# With systemd
sudo systemctl start quiet-quail
```

The dev server is only intended for local development.

---

Made with ♥️ for the Quiet-Quail dashboard team
