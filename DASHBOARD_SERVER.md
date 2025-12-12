# Dashboard Server Instructions

## Local Development

### Start the Dashboard Server

```bash
chmod +x run_dashboard.sh
./run_dashboard.sh
```

Then open your browser to: **http://localhost:8000**

### Alternative: Python Built-in Server

```bash
python3 -m http.server 8000
```

Then open: **http://localhost:8000/dashboard.html**

## Server Deployment

### Option 1: Manual Service with systemd

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/quiet-quail-dashboard.service
```

Add this content:

```ini
[Unit]
Description=Quiet-Quail Dashboard Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/quiet-quail
ExecStart=/usr/bin/python3 /var/www/quiet-quail/dashboard_server.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable quiet-quail-dashboard
sudo systemctl start quiet-quail-dashboard
```

Check status:

```bash
sudo systemctl status quiet-quail-dashboard
```

### Option 2: Using Gunicorn (Production)

Install Gunicorn:

```bash
pip install gunicorn
```

Start the server:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 dashboard_server:httpd
```

### Option 3: Using Nginx as Reverse Proxy

Configure Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Then start the dashboard server in the background:

```bash
nohup python3 dashboard_server.py > /var/www/quiet-quail/dashboard.log 2>&1 &
```

## Access the Dashboard

### Local
- http://localhost:8000

### Remote (adjust domain)
- http://your-domain.com
- http://your-ip-address:8000

## Features

- 📊 Real-time statistics (total posts, open/closed positions)
- 📅 Data collection timeline showing historical data
- 🏢 Military units card display with post counts
- 🔍 Searchable job postings with filters
- 📱 Responsive design for mobile devices
- ⚡ Auto-updates when new data is scraped

## Troubleshooting

### Port Already in Use

Use a different port:

```bash
./run_dashboard.sh 8080
# or
python3 -m http.server 8080
```

### Permission Denied

Ensure the script is executable:

```bash
chmod +x dashboard_server.py
chmod +x run_dashboard.sh
```

### CORS Issues

The custom dashboard server handles CORS automatically. If using Python's built-in server, use:

```bash
python3 -m http.server --bind 127.0.0.1 8000
```

And access from the same machine.

### Dashboard Shows No Data

1. Make sure the scraper has run: `python3 fetch_lobbyx.py`
2. Check that JSON files exist: `ls saved_json/`
3. Verify the API file was generated: `ls api/list-json-files.json`
4. Check browser console for errors (F12 → Console)

## Auto-start on Boot

On Linux servers, use systemd (Option 1 above).

For manual startup in a tmux/screen session:

```bash
tmux new-session -d -s dashboard 'cd /var/www/quiet-quail && python3 dashboard_server.py'
```

Reattach with:

```bash
tmux attach-session -t dashboard
```
