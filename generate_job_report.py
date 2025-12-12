#!/usr/bin/env python3
"""
Generate an HTML report showing job tracking statistics with charts and graphs.
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def parse_date_from_path(file_path):
    """Extract date from file path."""
    parts = file_path.split('/')
    if len(parts) >= 4:
        year, month, day = parts[1], parts[2], parts[3]
        return f"{year}-{month}-{day}"
    return "unknown"


def generate_html_report():
    """Generate comprehensive HTML tracking report."""
    
    job_timeline = defaultdict(list)
    all_dates = set()
    
    saved_json_dir = Path('saved_json')
    json_files = sorted(saved_json_dir.rglob('*.json'))
    json_files = [f for f in json_files if 'consolidated' not in str(f)]
    
    # Load data
    for json_file in json_files:
        date = parse_date_from_path(str(json_file))
        all_dates.add(date)
        
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                for post in data.get('posts', []):
                    post_id = post.get('post_id')
                    if post_id:
                        job_timeline[post_id].append({
                            'date': date,
                            'status': post.get('status', 'unknown'),
                            'position': post.get('position', 'N/A'),
                            'unit': post.get('unit_name', 'N/A')
                        })
        except Exception as e:
            pass
    
    # Calculate statistics
    all_dates = sorted(list(all_dates))
    jobs_by_date = defaultdict(int)
    open_by_date = defaultdict(int)
    closed_by_date = defaultdict(int)
    
    for post_id, occurrences in job_timeline.items():
        for occ in occurrences:
            jobs_by_date[occ['date']] += 1
            if occ['status'] == 'open':
                open_by_date[occ['date']] += 1
            elif occ['status'] == 'closed':
                closed_by_date[occ['date']] += 1
    
    # Jobs appearing in all scrapes
    jobs_all_scrapes = sum(1 for v in job_timeline.values() if len(v) == len(json_files))
    jobs_once = sum(1 for v in job_timeline.values() if len(v) == 1)
    jobs_closed = sum(1 for v in job_timeline.values() if v[-1]['status'] == 'closed')
    
    # Top 20 persistent jobs
    top_jobs = sorted(job_timeline.items(), key=lambda x: len(x[1]), reverse=True)[:20]
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Tracking Statistics Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px 0;
        }}
        .card {{
            border: none;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .stat-box {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        .stat-number {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #0d6efd;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9rem;
            margin-top: 10px;
        }}
        .chart-container {{
            position: relative;
            height: 400px;
            margin-bottom: 30px;
        }}
        .top-jobs {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        .job-row {{
            padding: 15px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .job-row:last-child {{
            border-bottom: none;
        }}
        .job-position {{
            font-weight: 600;
            color: #333;
        }}
        .job-appearances {{
            background: #0d6efd;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container-lg mt-5 mb-5">
        <div class="row mb-5">
            <div class="col-12">
                <div style="background: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <h1 class="mb-3"><i class="fas fa-chart-bar"></i> Job Tracking Statistics Report</h1>
                    <p class="text-muted">Analysis of military IT job postings from {all_dates[0]} to {all_dates[-1]}</p>
                </div>
            </div>
        </div>

        <!-- Summary Statistics -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="stat-box">
                    <div class="stat-number">{len(job_timeline)}</div>
                    <div class="stat-label">Unique Jobs</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-box">
                    <div class="stat-number">{len(json_files)}</div>
                    <div class="stat-label">Scrapes Analyzed</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-box">
                    <div class="stat-number">{jobs_all_scrapes}</div>
                    <div class="stat-label">Persistent Jobs (all scrapes)</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-box">
                    <div class="stat-number">{jobs_once}</div>
                    <div class="stat-label">One-time Postings</div>
                </div>
            </div>
        </div>

        <!-- Charts -->
        <div class="row mb-4">
            <div class="col-lg-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Jobs Over Time</h5>
                        <div class="chart-container">
                            <canvas id="timelineChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-lg-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Open vs Closed Posts by Date</h5>
                        <div class="chart-container">
                            <canvas id="statusChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Top Persistent Jobs -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title"><i class="fas fa-star"></i> Top 20 Persistent Job Postings</h5>
                        <div class="top-jobs">
"""
    
    # Add top jobs
    for idx, (post_id, occurrences) in enumerate(top_jobs, 1):
        position = occurrences[0]['position']
        unit = occurrences[0]['unit']
        appearances = len(occurrences)
        
        html += f"""                            <div class="job-row">
                                <div>
                                    <div class="job-position">{idx}. {position}</div>
                                    <small class="text-muted">{unit}</small>
                                </div>
                                <div class="job-appearances">{appearances} scrapes</div>
                            </div>
"""
    
    # Add chart data
    dates_json = json.dumps(all_dates)
    jobs_data = [jobs_by_date.get(d, 0) for d in all_dates]
    open_data = [open_by_date.get(d, 0) for d in all_dates]
    closed_data = [closed_by_date.get(d, 0) for d in all_dates]
    
    html += f"""                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const dates = {dates_json};
        const jobsData = {json.dumps(jobs_data)};
        const openData = {json.dumps(open_data)};
        const closedData = {json.dumps(closed_data)};

        // Timeline Chart
        const timelineCtx = document.getElementById('timelineChart').getContext('2d');
        new Chart(timelineCtx, {{
            type: 'line',
            data: {{
                labels: dates,
                datasets: [{{
                    label: 'Total Jobs Tracked',
                    data: jobsData,
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 4,
                    pointBackgroundColor: '#0d6efd'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});

        // Status Chart
        const statusCtx = document.getElementById('statusChart').getContext('2d');
        new Chart(statusCtx, {{
            type: 'bar',
            data: {{
                labels: dates,
                datasets: [
                    {{
                        label: 'Open',
                        data: openData,
                        backgroundColor: '#198754'
                    }},
                    {{
                        label: 'Closed',
                        data: closedData,
                        backgroundColor: '#dc3545'
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{
                        stacked: true
                    }},
                    y: {{
                        stacked: true,
                        beginAtZero: true
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    
    # Write to file
    output_file = Path('job_tracking_report.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ HTML report generated: {output_file}")
    return output_file


if __name__ == '__main__':
    generate_html_report()
