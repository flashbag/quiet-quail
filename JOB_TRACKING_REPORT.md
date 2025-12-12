# Job Tracking Statistics - Detailed Analysis

## Overview

Comprehensive tracking of all unique job postings across all scraping sessions. Shows when jobs appeared, how many times they appeared, and whether they're still open or closed.

## Key Findings

- **Total Unique Jobs**: 471
- **Total Scrapes Analyzed**: 22
- **Data Range**: 2025-10-21 to 2025-12-10 (52 days)
- **Average Appearances**: 16.9 times per job
- **Persistent Jobs** (appearing in all 22 scrapes): 240 positions
- **One-time Postings**: 10 positions (appeared in only 1 scrape)
- **Jobs That Closed**: 0 (all remain open)

## Files Generated

### 1. `job_tracking_stats.py`
Main analysis script that generates detailed tracking statistics.

**Usage:**
```bash
python3 job_tracking_stats.py
```

**Output:**
- Displays detailed timeline for each unique job (471 total)
- Shows when each job first appeared
- Shows when each job was last seen
- Number of times each job appeared in scrapes
- Status history (open → closed transitions)

### 2. `job_tracking_report.csv`
Spreadsheet-compatible CSV export with all tracking data.

**Columns:**
- `Post_ID` - Unique identifier
- `Position` - Job title
- `Unit` - Military unit/organization
- `First_Date` - First appearance date
- `Last_Date` - Most recent appearance date
- `Appearances` - Number of times this job appeared in scrapes
- `Status_History` - Complete status timeline (e.g., "open → open → open...")

**Usage:**
- Open in Excel, Google Sheets, or any spreadsheet application
- Sort by "Appearances" to find most persistent jobs
- Filter by "Unit" to see jobs by organization

### 3. `job_tracking_report.html`
Interactive visual dashboard with charts and statistics.

**Features:**
- Summary statistics cards
- Timeline chart showing job count evolution
- Open vs Closed status distribution over time
- Top 20 persistent job postings with appearance counts
- Responsive Bootstrap design

**Access:**
```bash
# Serve locally
python3 -m http.server 8000
# Then open: http://localhost:8000/job_tracking_report.html
```

## Top Persistent Jobs (22/22 scrapes)

Jobs appearing in all 22 scraping sessions:

1. **Java Developer** - 414 okr. brigade
2. **Tech Support** - 414 okr. brigade
3. **Senior Backend Engineer (Node.js)** - 414 okr. brigade
4. **Data Engineer** - 414 okr. brigade
5. **DevOps** - 414 okr. brigade
6. **CyberSec Engineer** - 414 okr. brigade
7. **Data Analytics** - 414 okr. brigade
8. **Frontend/React/Backend Developer** - 414 okr. brigade
9. **System Administrator (AD/DHCP/DNS)** - 414 okr. brigade
10. **Full Stack Developer** - 17 brigade "Raid"

*...and 230 more persistent positions*

## Job Status Summary

- **All Open**: 471 positions remain open (100%)
- **Closed**: 0 positions have closed
- **Status Stable**: No jobs have changed from open to closed during tracking period

This indicates consistent, active recruitment across all tracked positions with no terminations.

## One-Time Postings (appeared only once)

These positions appeared in only one scraping session:

- **103977**: Data Manager - 13 brigade (2025-10-21)
- **103036**: DevOps/DataOps Engineer - 13 brigade (2025-10-21)
- **103034**: Data Engineer - 13 brigade (2025-10-21)
- **103032**: Data Analyst - 13 brigade (2025-10-21)
- **149580**: Project Manager - 20 brigade (2025-10-31)
- **152453**: Radio Station Chief - 1 battalion (2025-11-15)
- **157851**: HUMINT Analyst - Defense Forces (2025-12-04)
- **158854**: Security Administrator - National Guard (2025-12-10)
- **158851**: Communications/System Admin - National Guard (2025-12-10)
- **158645**: OSINT Analyst - Border Unit (2025-12-10)

These may represent temporary postings or positions that were quickly filled.

## Analysis Insights

### Recruitment Patterns

1. **Stable Core**: 240 positions (51% of total) remain consistently open across all scrapes, indicating:
   - Ongoing recruitment efforts
   - High demand for IT specialists
   - Possibly difficulty filling positions
   - Continuous military IT operations needs

2. **Fresh Postings**: New jobs appear regularly:
   - 10 one-time postings suggest periodic recruitment
   - Jobs added across the 52-day period
   - Latest postings from 2025-12-10

3. **Zero Closures**: No jobs have closed during tracking period, indicating:
   - No positions were filled
   - All recruitment campaigns remain active
   - Sustained military IT staffing needs

### Top Recruiting Units

**By Job Count (among persistent jobs):**
1. 414 Separate Brigade of Unmanned Systems "Birds of Madyar" - ~50+ positions
2. 17 Brigade "Raid" - ~30+ positions
3. 12 Brigade Special Purpose "Azov" - ~15+ positions
4. Multiple other units with 5-20 positions each

## Deduplication Context

**Original Data:**
- 7,968 total posts across 22 JSON files
- Massive duplication (94% duplicate entries)
- Same positions repeated in every scrape

**Processed Data:**
- 471 unique positions identified
- Duplicates removed for accurate counting
- Each unique job ID tracked separately

**Impact:**
- Corrected dashboard display (471 vs 7,968)
- Accurate statistics for recruitment trends
- Clean dataset for analysis

## Scripts Reference

### Generate All Reports

```bash
# Run tracking analysis
python3 job_tracking_stats.py

# Generate interactive dashboard
python3 generate_job_report.py

# View HTML dashboard
# Copy job_tracking_report.html to dashboard or open directly
```

### Key Data Files

- `saved_json/consolidated_unique.json` - Single file with all 471 unique posts
- `job_tracking_report.csv` - Exportable data
- `job_tracking_report.html` - Interactive visualization
- `job_tracking_stats.py` - Analysis tool
- `generate_job_report.py` - Report generator

## Usage Examples

### Find all jobs by specific unit
```bash
grep "414 окрема бригада" job_tracking_report.csv | wc -l
```

### Find jobs that appeared most frequently
```bash
# Sort by Appearances column (descending)
sort -t',' -k6 -nr job_tracking_report.csv | head -20
```

### Export jobs from specific date range
```bash
# Jobs first appearing in November
grep "2025-11" job_tracking_report.csv
```

## Real-World Applications

1. **Recruitment Analysis**: Understand military IT staffing needs
2. **Trend Identification**: Track how positions evolve over time
3. **Historical Perspective**: See which roles are persistently in demand
4. **Unit Analysis**: Compare recruitment intensity by unit
5. **Forecasting**: Predict future recruitment patterns

## Notes

- Data collected via web scraping from LobbyX.army
- 22 scraping sessions over ~7 weeks (October - December 2025)
- All timestamps are in 2025
- Job descriptions and requirements in Ukrainian/English mix
- Some positions include international recruitment indicators
- Military IT roles span multiple specializations (DevOps, Security, Analysis, etc.)

---

*Last Updated: December 12, 2025*
*Data Range: October 21 - December 10, 2025*
