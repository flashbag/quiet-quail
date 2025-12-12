# Quiet-Quail - LobbyX Job Scraper

A Python-based scraper for [LobbyX.army](https://lobbyx.army/?sphere=it) job postings. Automatically fetches IT job listings from the Ukrainian military recruitment platform and parses them into structured JSON data.

## Features

- 🔄 **Automated scraping** with Playwright (headless browser)
- 📦 **HTML archival** with organized date-based structure
- 🔍 **JSON parsing** extracts structured data from HTML
- ⏰ **Cron support** for scheduled execution (every 6 hours)
- 🚀 **Easy deployment** scripts for server setup

## Project Structure

```
Quiet-Quail/
├── fetch_lobbyx.py              # Main scraper script
├── parse_html_to_json.py        # HTML to JSON parser
├── requirements.txt             # Python dependencies
├── saved_html/                  # Archived HTML files (YYYY/MM/DD structure)
├── saved_json/                  # Parsed JSON data (mirrors HTML structure)
│
├── deploy.sh                    # Deploy to server
├── setup_server.sh              # Environment setup
├── setup_cron.sh                # Configure cron job
│
├── README_DEPLOYMENT.md         # Deployment guide
└── README.md                    # This file
```

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Run the scraper:**
   ```bash
   python3 fetch_lobbyx.py
   ```
   This automatically parses HTML to JSON after scraping.

3. **View the dashboard:**
   ```bash
   python3 -m http.server 8000
   # Visit http://localhost:8000/dashboard.html
   ```

### Server Deployment

See [README_DEPLOYMENT.md](README_DEPLOYMENT.md) for detailed deployment instructions.

**Quick deploy:**
```bash
./deploy.sh user@your-server.com /path/on/server
ssh user@your-server.com
cd /path/on/server
./setup_server.sh
./setup_cron.sh
```

## Scripts

### `fetch_lobbyx.py`

Main scraper that:
- Launches headless Chromium browser
- Navigates to https://lobbyx.army/?sphere=it
- Clicks "Load More" until all content is loaded
- Saves HTML to `saved_html/YYYY/MM/DD/output_YYYYMMDD_HHMMSS.html`
- Logs all activity to `debug.log`

### `parse_html_to_json.py`

Parser that:
- Processes all HTML files in `saved_html/`
- Extracts job posting data from each `<div id="post-XXXXX">`
- Creates JSON files in `saved_json/` with identical directory structure
- Extracts:
  - Post ID
  - Job URL
  - Unit name
  - Position title
  - Image URL
  - Categories/tags
  - Status (open/closed)

**Output format:**
```json
{
  "source_file": "2025/12/10/output_20251210_202928.html",
  "parsed_at": "2025-12-10T21:00:23.204672",
  "post_count": 384,
  "posts": [
    {
      "post_id": "158854",
      "url": "https://lobbyx.army/tor/...",
      "unit_name": "Національна гвардія України",
      "position": "Адміністратор безпеки",
      "image_url": "https://lobbyx.army/wp-content/uploads/...",
      "categories": ["category-militari", "category-it", ...],
      "units": ["units-natsionalna-hvardiia-ukrainy"],
      "status": "open"
    }
  ]
}
```

## Cron Schedule

The default cron configuration runs every 6 hours:
- 00:00 (midnight)
- 06:00 (6 AM)
- 12:00 (noon)
- 18:00 (6 PM)

Edit with: `crontab -e`

## Data Structure

### HTML Files
```
saved_html/
└── 2025/
    └── 12/
        └── 10/
            └── output_20251210_202928.html
```

### JSON Files
```
saved_json/
└── 2025/
    └── 12/
        └── 10/
            └── output_20251210_202928.json
```

## Dependencies

- **playwright** - Browser automation
- **beautifulsoup4** - HTML parsing
- **Python 3.7+**

## Logs

- `debug.log` - Scraper execution logs
- `cron.log` - Cron job execution logs

## Troubleshooting

### DNS Issues
If you encounter DNS resolution errors on your server (especially with VPN):
```bash
./fix_dns_comprehensive.sh
```

See [DNS_TROUBLESHOOTING.md](DNS_TROUBLESHOOTING.md) for detailed help.

### Playwright Issues
```bash
playwright install-deps chromium  # Install system dependencies
playwright install chromium        # Reinstall browser
```

### Manual Test
```bash
cd /path/to/project
source venv/bin/activate
python3 fetch_lobbyx.py
python3 parse_html_to_json.py
```

## Statistics (as of 2025-12-10)

- **HTML files archived:** 22
- **Total job posts extracted:** 7,968
- **Date range:** Oct 21, 2025 - Dec 10, 2025
- **Latest post count:** 384 (Dec 10)

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is for educational and archival purposes.

## Acknowledgments

Data sourced from [LobbyX.army](https://lobbyx.army/) - Ukrainian military recruitment platform.
