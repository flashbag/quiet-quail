# Quiet-Quail Dashboard Guide

## Overview

The Quiet-Quail Dashboard is a modern, responsive web interface that visualizes job postings data from the LobbyX military recruitment platform.

## Features

### 📊 Statistics Dashboard
- **Total Posts**: Sum of all job postings
- **Open Positions**: Active job listings
- **Closed Positions**: Filled or unavailable positions
- **Data Files**: Number of JSON files processed

### 📅 Data Collection Timeline
- Shows when data was collected
- Displays post count per date
- Historical view of scraping activity

### 🏢 Military Units Section
- Top 12 military organizations by position count
- Quick overview of where most jobs are

### 📋 Job Postings List
- Comprehensive list of all positions
- Status badges (Open/Closed)
- Category tags
- Search and filter functionality
- Direct links to full job descriptions

### 🔍 Search & Filter
- **Search**: Find positions or units by name
- **Status Filter**: View only open or closed positions
- Real-time filtering

## Accessing the Dashboard

### Local Development
```bash
cd /var/www/quiet-quail
python3 -m http.server 8000
# Visit http://localhost:8000/dashboard.html
```

### On Server
Once deployed to your server, the dashboard can be accessed at:
```
http://your-server.com/path/to/quiet-quail/dashboard.html
```

### With Web Server (Recommended for Production)

#### Using Nginx:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /var/www/quiet-quail;
        index dashboard.html;
    }
}
```

#### Using Apache:
```apache
<VirtualHost *:80>
    ServerName your-domain.com
    DocumentRoot /var/www/quiet-quail
    
    <Directory /var/www/quiet-quail>
        Options Indexes FollowSymLinks
        AllowOverride All
    </Directory>
</VirtualHost>
```

## How It Works

### Data Flow
1. **Scraper** (`fetch_lobbyx.py`)
   - Downloads latest HTML from LobbyX
   - Saves to `saved_html/YYYY/MM/DD/`

2. **Parser** (`parse_html_to_json.py`)
   - Automatically runs after scraping
   - Extracts job data from HTML
   - Saves to `saved_json/YYYY/MM/DD/`

3. **API Generator** (`generate_dashboard_api.py`)
   - Creates file list: `api/list-json-files.json`
   - Lists all available JSON files

4. **Dashboard** (`dashboard.html`)
   - Loads file list from API
   - Fetches all JSON data
   - Renders interactive visualization

### File Structure
```
/var/www/quiet-quail/
├── dashboard.html                # Dashboard UI
├── api/
│   └── list-json-files.json     # File list for dashboard
├── saved_json/                   # Parsed data
│   └── 2025/12/10/
│       └── output_20251210_202928.json
└── saved_html/                   # Source HTML
    └── 2025/12/10/
        └── output_20251210_202928.html
```

## Customization

### Colors & Theme
Edit the CSS variables in `dashboard.html`:
```css
:root {
    --primary-color: #0d6efd;
    --success-color: #198754;
    --danger-color: #dc3545;
    --warning-color: #ffc107;
    --info-color: #0dcaf0;
}
```

### Layout Changes
The dashboard uses Bootstrap 5 grid system. Edit the classes to adjust layouts:
- `col-md-3`: 25% width on medium+ screens
- `col-md-6`: 50% width on medium+ screens
- `col-md-4`: 33% width on medium+ screens

### Data Display
Modify JavaScript in dashboard.html to change:
- Number of displayed jobs: Change `slice(0, 50)` to desired number
- Number of units shown: Change `slice(0, 12)` to desired number
- Sort order and filters

## Troubleshooting

### Dashboard Shows "No Data"
1. Verify JSON files exist: `ls saved_json/`
2. Generate API file: `python3 generate_dashboard_api.py`
3. Check browser console (F12) for errors
4. Ensure `api/list-json-files.json` exists

### Data Not Updating
1. Run scraper: `python3 fetch_lobbyx.py`
2. Verify parser ran: Check for new files in `saved_json/`
3. Regenerate API: `python3 generate_dashboard_api.py`
4. Clear browser cache: Ctrl+Shift+Delete

### CORS Issues (if using different domain)
The dashboard loads JSON files from the same domain. If hosted separately, you'll need to:
1. Enable CORS headers on your server
2. Use a proxy service
3. Or host dashboard and data on the same domain

## Performance Tips

### For Large Datasets
- The dashboard loads all JSON files into memory
- For 20+ files, consider:
  - Implementing pagination
  - Loading files on-demand
  - Using a backend API instead

### Optimization
- Minify CSS/JavaScript in production
- Use gzip compression on server
- Cache static files (dashboard.html, CSS, JS)

## Browser Compatibility

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Android Chrome)

## License

Same as Quiet-Quail project.

## Support

For issues or improvements:
1. Check existing logs: `tail -f debug.log`
2. Review browser console: F12 → Console
3. Check cron logs: `tail -f cron.log`
