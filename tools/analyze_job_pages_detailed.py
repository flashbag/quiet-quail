#!/usr/bin/env python3
"""
Enhanced job page analyzer - extracts rich structured data from individual job pages.
Analyzes HTML structure to identify all available fields and their patterns.
"""

import os
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict, Counter

DATA_DIR = Path(__file__).parent / 'data'


def extract_all_text_blocks(soup):
    """Extract all major text blocks and their context."""
    blocks = defaultdict(list)
    
    # Find main content area
    main = soup.find('main')
    if not main:
        main = soup.body
    
    if main:
        # Extract all text paragraphs
        for p in main.find_all('p'):
            text = p.get_text(strip=True)
            if len(text) > 20:  # Only significant text
                blocks['paragraphs'].append(text[:300])
        
        # Extract all list items
        for li in main.find_all('li'):
            text = li.get_text(strip=True)
            if text:
                blocks['list_items'].append(text[:200])
        
        # Extract all div content
        for div in main.find_all('div', class_=re.compile(r'(vacancy|info|section|content)')):
            text = div.get_text(strip=True)
            if 50 < len(text) < 500:  # Medium-length text blocks
                class_name = div.get('class', ['unknown'])[0]
                blocks[f'div_{class_name}'].append(text[:250])
    
    return blocks


def extract_comprehensive_data(html_content, file_path):
    """Extract comprehensive job data from HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    data = {
        'file_path': str(file_path),
        'file_size_kb': len(html_content) / 1024,
    }
    
    # 1. IDENTIFIERS
    body = soup.find('body')
    if body:
        classes = body.get('class', [])
        data['body_classes'] = classes
        
        # Extract post_id
        for cls in classes:
            if cls.startswith('postid-'):
                data['post_id'] = cls.replace('postid-', '')
                break
        
        # Extract status
        for cls in classes:
            if 'tors-status-' in cls:
                data['status'] = cls.replace('tors-status-', '')
                break
        
        # Extract categories from body classes
        data['body_categories'] = [c for c in classes if c not in data.get('body_classes', [])[:5]]
    
    # 2. BASIC INFO
    title_tag = soup.find('h1', class_='vacancy-name')
    if title_tag:
        data['title'] = title_tag.get_text(strip=True)
    
    subtitle_tag = soup.find('h2', class_='vacancy-title')
    if subtitle_tag:
        data['vacancy_type'] = subtitle_tag.get_text(strip=True)
    
    # 3. DATES
    date_published = soup.find('meta', property='article:published_time')
    if date_published:
        data['published_date'] = date_published.get('content')
    
    date_modified = soup.find('meta', property='article:modified_time')
    if date_modified:
        data['modified_date'] = date_modified.get('content')
    
    # 4. UNIT/ORGANIZATION
    unit_button = soup.find('a', class_='about__unit--button')
    if unit_button:
        data['unit_name'] = unit_button.get_text(strip=True)
    
    unit_link = soup.find('a', href=re.compile(r'/brigades/'))
    if unit_link:
        data['unit'] = unit_link.get_text(strip=True)
        data['unit_url'] = unit_link.get('href')
    
    logo_div = soup.find('div', class_='vacancy-logo-img')
    if logo_div and logo_div.get('style'):
        url_match = re.search(r"url\('([^']+)'\)", logo_div.get('style', ''))
        if url_match:
            data['unit_logo_url'] = url_match.group(1)
    
    # 5. VACANCY INFO ITEMS
    info_items = {}
    for item_div in soup.find_all('div', class_='vacancy-info-item'):
        label = item_div.find('div', class_='item-label')
        value = item_div.find('div', class_='item-value')
        
        if label and value:
            label_text = label.get_text(strip=True).lower().rstrip(':')
            value_text = value.get_text(strip=True)
            
            if label_text and value_text:
                info_items[label_text] = value_text
    
    if info_items:
        data['vacancy_info'] = info_items
    
    # 6. MAIN DESCRIPTION
    vacancy_content = soup.find('div', class_='vacancy-content')
    if vacancy_content:
        # Get full text
        full_text = vacancy_content.get_text(strip=True)
        data['full_description_length'] = len(full_text)
        data['full_description_preview'] = full_text[:500]
        
        # Count sections by headers
        h3_headers = [h.get_text(strip=True) for h in vacancy_content.find_all('h3')]
        if h3_headers:
            data['description_sections'] = h3_headers
    
    # 7. REQUIREMENTS/SKILLS (look for lists)
    req_section = None
    for div in soup.find_all('div', class_=re.compile(r'vacancy')):
        text = div.get_text(strip=True).lower()
        if any(word in text for word in ['вимоги', 'умови', 'потрібно', 'інші вимоги']):
            req_section = div
            break
    
    if req_section:
        requirements = []
        for li in req_section.find_all('li'):
            req_text = li.get_text(strip=True)
            if req_text:
                requirements.append(req_text)
        if requirements:
            data['requirements'] = requirements[:15]  # Limit to 15
    
    # 8. TAGS/CATEGORIES (from info items)
    category_links = soup.find_all('a', class_=re.compile(r'(category|tag|item)'))
    categories = []
    for link in category_links:
        text = link.get_text(strip=True)
        if text and len(text) < 50:
            categories.append(text)
    if categories:
        data['tags'] = list(set(categories))[:20]
    
    # 9. SEO METADATA
    og_title = soup.find('meta', property='og:title')
    if og_title:
        data['og_title'] = og_title.get('content')
    
    og_description = soup.find('meta', property='og:description')
    if og_description:
        data['og_description'] = og_description.get('content')[:500]
    
    og_url = soup.find('meta', property='og:url')
    if og_url:
        data['canonical_url'] = og_url.get('content')
    
    # 10. STRUCTURED DATA (JSON-LD)
    json_ld = soup.find('script', type='application/ld+json')
    if json_ld:
        try:
            ld_data = json.loads(json_ld.string)
            if isinstance(ld_data, dict) and '@graph' in ld_data:
                for item in ld_data['@graph']:
                    if item.get('@type') == 'WebPage':
                        data['schema_name'] = item.get('name')
                        data['schema_url'] = item.get('url')
                        data['schema_published'] = item.get('datePublished')
                        data['schema_modified'] = item.get('dateModified')
        except Exception:
            pass
    
    # 11. TEXT BLOCKS ANALYSIS
    text_blocks = extract_all_text_blocks(soup)
    if text_blocks:
        data['text_block_summary'] = {
            'paragraphs_count': len(text_blocks.get('paragraphs', [])),
            'list_items_count': len(text_blocks.get('list_items', [])),
            'sample_paragraphs': text_blocks.get('paragraphs', [])[:2],
            'sample_list_items': text_blocks.get('list_items', [])[:3]
        }
    
    return data


def analyze_job_pages_enhanced():
    """Analyze all job pages with comprehensive data extraction."""
    print(f"🔍 Found job pages in {DATA_DIR}")
    
    job_files = sorted(DATA_DIR.glob('*/*/*/job_*.html'))
    print(f"📊 Total files to analyze: {len(job_files)}\n")
    
    all_jobs = []
    field_frequency = Counter()
    errors = []
    
    for idx, file_path in enumerate(job_files, 1):
        if idx % 100 == 0:
            print(f"  [{idx}/{len(job_files)}] Processing...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html = f.read()
            
            job_data = extract_comprehensive_data(html, file_path.name)
            all_jobs.append(job_data)
            
            # Track field frequency
            for field in job_data.keys():
                if job_data[field] is not None:
                    field_frequency[field] += 1
        
        except Exception as e:
            errors.append({'file': file_path.name, 'error': str(e)})
    
    return all_jobs, field_frequency, errors


def print_detailed_report(all_jobs, field_frequency, errors):
    """Print comprehensive analysis report."""
    print("\n" + "="*80)
    print("🎯 COMPREHENSIVE JOB PAGES ANALYSIS")
    print("="*80)
    
    print(f"\n✅ PROCESSING SUMMARY:")
    print(f"   Total pages analyzed: {len(all_jobs)}")
    print(f"   Errors: {len(errors)}")
    
    if all_jobs:
        print(f"\n📋 DATA AVAILABILITY:")
        print(f"   Most common fields:")
        for field, count in field_frequency.most_common(20):
            pct = (count / len(all_jobs)) * 100
            print(f"      - {field:<30} {count:3d} pages ({pct:5.1f}%)")
    
    if all_jobs and 'title' in all_jobs[0]:
        print(f"\n🏆 SAMPLE JOB ENTRY (First page):")
        sample = all_jobs[0]
        for key in ['post_id', 'title', 'unit_name', 'unit', 'modified_date', 'status']:
            if key in sample:
                print(f"   {key:<20} {str(sample[key])[:60]}")
    
    # Statistics on specific fields
    if all_jobs:
        print(f"\n📊 FIELD STATISTICS:")
        
        # Titles
        titles = [j.get('title') for j in all_jobs if 'title' in j]
        print(f"   Unique titles: {len(set(titles))}")
        
        # Units
        units = [j.get('unit_name') for j in all_jobs if 'unit_name' in j and j.get('unit_name')]
        print(f"   Unique units: {len(set(units))}")
        
        # Status
        statuses = Counter(j.get('status') for j in all_jobs if 'status' in j)
        print(f"   Job statuses: {dict(statuses)}")
        
        # Requirements
        with_req = sum(1 for j in all_jobs if 'requirements' in j)
        print(f"   Pages with requirements: {with_req} ({(with_req/len(all_jobs))*100:.1f}%)")
        
        # Description sections
        with_sections = sum(1 for j in all_jobs if 'description_sections' in j)
        print(f"   Pages with section headers: {with_sections}")
    
    print(f"\n" + "="*80)


def save_detailed_analysis(all_jobs, field_frequency):
    """Save detailed analysis to JSON."""
    output_file = Path(__file__).parent / 'job_pages_detailed_analysis.json'
    
    # Prepare output
    output_data = {
        'total_jobs': len(all_jobs),
        'field_frequency': dict(field_frequency),
        'jobs': all_jobs,
        'summary': {
            'unique_titles': len(set(j.get('title') for j in all_jobs if 'title' in j)),
            'unique_units': len(set(j.get('unit_name') for j in all_jobs if 'unit_name' in j and j.get('unit_name'))),
            'pages_with_requirements': sum(1 for j in all_jobs if 'requirements' in j),
            'pages_with_tags': sum(1 for j in all_jobs if 'tags' in j),
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed analysis saved to: job_pages_detailed_analysis.json")
    print(f"   File size: {output_file.stat().st_size / 1024:.1f} KB")


if __name__ == '__main__':
    print("🚀 Starting comprehensive job pages analysis...\n")
    
    if not DATA_DIR.exists():
        print(f"❌ Data directory not found: {DATA_DIR}")
        exit(1)
    
    all_jobs, field_frequency, errors = analyze_job_pages_enhanced()
    print_detailed_report(all_jobs, field_frequency, errors)
    save_detailed_analysis(all_jobs, field_frequency)
    
    print("\n✅ Analysis complete!")
