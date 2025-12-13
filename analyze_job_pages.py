#!/usr/bin/env python3
"""
Analyze and extract data from saved job pages (job_*.html files).
Gathers available information such as titles, units, requirements, and more.
"""

import os
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict

DATA_DIR = Path(__file__).parent / 'data'


def extract_job_data(html_content):
    """Extract structured data from a job page HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    data = {}
    
    # Extract post_id from body class
    body = soup.find('body')
    if body and body.get('class'):
        for cls in body.get('class', []):
            if cls.startswith('postid-'):
                data['post_id'] = cls.replace('postid-', '')
                break
    
    # Extract job title
    title_tag = soup.find('h1', class_='vacancy-name')
    if title_tag:
        data['title'] = title_tag.get_text(strip=True)
    
    # Extract unit/organization
    unit_link = soup.find('a', href=re.compile(r'/brigades/'))
    if unit_link:
        data['unit'] = unit_link.get_text(strip=True)
        data['unit_url'] = unit_link.get('href')
    
    # Extract unit image
    logo_div = soup.find('div', class_='vacancy-logo-img')
    if logo_div and logo_div.get('style'):
        url_match = re.search(r"url\('([^']+)'\)", logo_div.get('style', ''))
        if url_match:
            data['unit_logo'] = url_match.group(1)
    
    # Extract main vacancy info section
    info_section = soup.find('div', class_='vacancy-info-section')
    if info_section:
        # Look for category/tag items
        categories = []
        category_items = info_section.find_all('a', class_='item')
        for item in category_items:
            cat_text = item.get_text(strip=True)
            if cat_text:
                categories.append(cat_text)
        if categories:
            data['categories'] = categories
    
    # Extract all available field data from info divs
    info_items = soup.find_all('div', class_='vacancy-info-item')
    for item in info_items:
        label_tag = item.find('div', class_='item-label')
        value_tag = item.find('div', class_='item-value')
        
        if label_tag and value_tag:
            label = label_tag.get_text(strip=True).lower()
            value = value_tag.get_text(strip=True)
            
            # Normalize label names
            if label:
                label = label.rstrip(':')
                data[f'field_{label}'] = value
    
    # Extract description/main content
    content = soup.find('div', class_='vacancy-description')
    if content:
        # Get text content
        text = content.get_text(strip=True)
        if text:
            data['description'] = text[:500]  # First 500 chars
            data['description_full_length'] = len(text)
    
    # Extract OG metadata
    og_title = soup.find('meta', property='og:title')
    if og_title:
        data['og_title'] = og_title.get('content', '')
    
    og_description = soup.find('meta', property='og:description')
    if og_description:
        data['og_description'] = og_description.get('content', '')[:300]
    
    # Extract publish date
    date_published = soup.find('meta', property='article:published_time')
    if date_published:
        data['published_date'] = date_published.get('content', '')
    
    date_modified = soup.find('meta', property='article:modified_time')
    if date_modified:
        data['modified_date'] = date_modified.get('content', '')
    
    # Extract structured data (JSON-LD)
    json_ld = soup.find('script', type='application/ld+json')
    if json_ld:
        try:
            ld_data = json.loads(json_ld.string)
            if isinstance(ld_data, dict) and '@graph' in ld_data:
                for item in ld_data['@graph']:
                    if item.get('@type') == 'WebPage':
                        data['json_ld_name'] = item.get('name')
                        data['json_ld_url'] = item.get('url')
                        if 'datePublished' in item:
                            data['json_ld_published'] = item['datePublished']
        except json.JSONDecodeError:
            pass
    
    return data


def analyze_all_job_pages():
    """Scan and analyze all job pages, generating statistics."""
    results = {
        'total_files': 0,
        'successfully_parsed': 0,
        'errors': [],
        'jobs': [],
        'field_types': defaultdict(int),
        'sample_data': None
    }
    
    # Find all job_*.html files
    job_files = sorted(DATA_DIR.glob('*/*/*/job_*.html'))
    results['total_files'] = len(job_files)
    
    print(f"🔍 Found {results['total_files']} job pages")
    print("📊 Analyzing job pages...\n")
    
    for idx, file_path in enumerate(job_files, 1):
        try:
            # Show progress every 50 files
            if idx % 50 == 0:
                print(f"  [{idx}/{results['total_files']}] Processing...")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            job_data = extract_job_data(html_content)
            job_data['file_path'] = str(file_path.relative_to(DATA_DIR))
            job_data['file_size'] = len(html_content)
            
            results['jobs'].append(job_data)
            results['successfully_parsed'] += 1
            
            # Track field types
            for key in job_data.keys():
                if key.startswith('field_'):
                    results['field_types'][key.replace('field_', '')] += 1
            
            # Store first sample
            if results['sample_data'] is None:
                results['sample_data'] = job_data
                
        except Exception as e:
            results['errors'].append({
                'file': str(file_path),
                'error': str(e)
            })
            print(f"  ❌ Error parsing {file_path.name}: {e}")
    
    return results


def print_analysis(results):
    """Print detailed analysis results."""
    print("\n" + "="*70)
    print("📋 JOB PAGES ANALYSIS REPORT")
    print("="*70)
    
    print(f"\n✅ PARSING RESULTS:")
    print(f"   Total job files: {results['total_files']}")
    print(f"   Successfully parsed: {results['successfully_parsed']}")
    print(f"   Errors: {len(results['errors'])}")
    
    if results['errors']:
        print(f"\n❌ PARSING ERRORS:")
        for err in results['errors'][:5]:  # Show first 5 errors
            print(f"   - {err['file']}: {err['error']}")
        if len(results['errors']) > 5:
            print(f"   ... and {len(results['errors']) - 5} more")
    
    # Data field inventory
    print(f"\n📊 DATA FIELDS FOUND:")
    if results['field_types']:
        for field_name in sorted(results['field_types'].keys()):
            count = results['field_types'][field_name]
            percentage = (count / results['successfully_parsed']) * 100
            print(f"   - {field_name}: {count} pages ({percentage:.1f}%)")
    
    # Common fields across all jobs
    print(f"\n🏷️  COMMON FIELDS (available in most pages):")
    common_fields = ['title', 'unit', 'categories', 'description', 'published_date', 'modified_date']
    for field in common_fields:
        count = sum(1 for job in results['jobs'] if field in job)
        if count > 0:
            percentage = (count / results['successfully_parsed']) * 100
            print(f"   - {field}: {percentage:.1f}%")
    
    # Sample data
    if results['sample_data']:
        print(f"\n📄 SAMPLE JOB PAGE DATA:")
        sample = results['sample_data']
        print(f"   Post ID: {sample.get('post_id', 'N/A')}")
        print(f"   Title: {sample.get('title', 'N/A')[:60]}")
        print(f"   Unit: {sample.get('unit', 'N/A')}")
        print(f"   File Size: {sample.get('file_size', 0) / 1024:.1f} KB")
        print(f"   Published: {sample.get('published_date', 'N/A')}")
        print(f"   Categories: {', '.join(sample.get('categories', [])[:3])}")
    
    # Unique values statistics
    print(f"\n📈 UNIQUE VALUES STATISTICS:")
    unique_units = len(set(j.get('unit', '') for j in results['jobs'] if 'unit' in j))
    unique_titles = len(set(j.get('title', '') for j in results['jobs'] if 'title' in j))
    print(f"   Unique units: {unique_units}")
    print(f"   Unique job titles: {unique_titles}")
    
    # File size stats
    file_sizes = [j.get('file_size', 0) for j in results['jobs']]
    if file_sizes:
        avg_size = sum(file_sizes) / len(file_sizes) / 1024
        total_size = sum(file_sizes) / (1024 * 1024)
        print(f"   Average file size: {avg_size:.1f} KB")
        print(f"   Total data: {total_size:.1f} MB")
    
    print(f"\n" + "="*70)


def save_analysis(results):
    """Save analysis results to JSON file."""
    output_file = Path(__file__).parent / 'job_pages_analysis.json'
    
    # Clean up non-serializable data for JSON
    clean_results = {
        'total_files': results['total_files'],
        'successfully_parsed': results['successfully_parsed'],
        'errors': results['errors'],
        'field_types': dict(results['field_types']),
        'jobs': results['jobs'],
        'sample_data': results['sample_data']
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clean_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Analysis saved to: {output_file}")
    print(f"   - Jobs data: {len(results['jobs'])} entries")
    print(f"   - File size: {output_file.stat().st_size / 1024:.1f} KB")


if __name__ == '__main__':
    print("🚀 Starting job pages analysis...\n")
    
    if not DATA_DIR.exists():
        print(f"❌ Data directory not found: {DATA_DIR}")
        exit(1)
    
    results = analyze_all_job_pages()
    print_analysis(results)
    save_analysis(results)
    
    print("\n✅ Analysis complete!")
