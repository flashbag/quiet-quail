#!/usr/bin/env python3
"""
Dashboard error detection and console log analyzer.
Tests for JavaScript errors and console issues.
"""

import json
import re
from pathlib import Path


def validate_js_syntax():
    """Validate JavaScript syntax in dashboard.html"""
    
    dashboard_file = Path('dashboard.html')
    
    if not dashboard_file.exists():
        print("Error: dashboard.html not found")
        return False
    
    content = dashboard_file.read_text()
    
    errors = []
    warnings = []
    
    # Check for unclosed tags
    if content.count('<script') != content.count('</script'):
        errors.append("Unclosed <script> tags")
    
    if content.count('<div') != content.count('</div'):
        warnings.append(f"Mismatched <div> tags: {content.count('<div')} opens, {content.count('</div')} closes")
    
    # Check for common JS errors
    if 'window.persistenceChart.destroy()' in content:
        if 'typeof window.persistenceChart.destroy === \'function\'' not in content:
            warnings.append("Potential: persistenceChart.destroy() called without type check")
    
    # Check for undefined variables
    js_patterns = {
        'allData': r'\ballData\b',
        'window.uniquePosts': r'window\.uniquePosts',
        'displayJobTracking': r'displayJobTracking\(',
    }
    
    for var_name, pattern in js_patterns.items():
        matches = re.findall(pattern, content)
        if not matches:
            warnings.append(f"Variable '{var_name}' not found in code")
    
    # Check for Chart.js initialization
    if 'Chart(' in content:
        if 'if (typeof Chart === \'undefined\')' not in content:
            warnings.append("Chart.js availability not checked before use")
    
    # Check for fetch calls
    fetch_count = content.count('fetch(')
    print(f"Found {fetch_count} fetch() calls")
    
    # Check for error handlers
    catch_count = content.count('} catch (e) {')
    try_count = content.count('try {')
    
    if try_count > 0 and catch_count == 0:
        errors.append(f"Found {try_count} try blocks but no catch handlers")
    
    # Report results
    print("\n" + "=" * 70)
    print("JAVASCRIPT VALIDATION REPORT")
    print("=" * 70)
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for error in errors:
            print(f"   - {error}")
    
    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"   - {warning}")
    
    if not errors and not warnings:
        print("\n✅ No syntax or structural errors detected")
    
    print("\n" + "=" * 70)
    print("METRICS")
    print("=" * 70)
    print(f"- Script tags: {content.count('<script')}")
    print(f"- Try/catch blocks: {try_count}/{catch_count}")
    print(f"- Fetch calls: {fetch_count}")
    print(f"- Chart initializations: {content.count('new Chart(')}")
    print(f"- Event listeners: {content.count('addEventListener')}")
    
    return len(errors) == 0


def check_json_validity():
    """Check if generated JSON files are valid"""
    
    saved_json_dir = Path('saved_json')
    json_files = list(saved_json_dir.glob('*.json')) + list(saved_json_dir.glob('*/*.json')) + list(saved_json_dir.glob('*/*/*.json'))
    
    print("\n" + "=" * 70)
    print("JSON FILE VALIDITY CHECK")
    print("=" * 70)
    
    valid = 0
    invalid = 0
    errors_found = []
    
    for json_file in json_files[:10]:  # Check first 10 files
        try:
            data = json.loads(json_file.read_text())
            valid += 1
            
            # Validate structure
            required_fields = ['posts', 'post_count', 'source_file', 'parsed_at']
            missing = [f for f in required_fields if f not in data]
            
            if missing:
                errors_found.append(f"{json_file.name}: Missing {missing}")
        except json.JSONDecodeError as e:
            invalid += 1
            errors_found.append(f"{json_file.name}: {str(e)}")
    
    print(f"\nChecked {len(json_files[:10])} JSON files:")
    print(f"  ✅ Valid: {valid}")
    print(f"  ❌ Invalid: {invalid}")
    
    if errors_found:
        print(f"\n⚠️  Issues found:")
        for error in errors_found[:5]:
            print(f"   - {error}")
    else:
        print(f"\n✅ All checked JSON files are valid")


def analyze_dashboard_functions():
    """Analyze dashboard functions for common issues"""
    
    dashboard_file = Path('dashboard.html')
    content = dashboard_file.read_text()
    
    print("\n" + "=" * 70)
    print("FUNCTION ANALYSIS")
    print("=" * 70)
    
    functions = [
        'loadData',
        'processData',
        'updateStats',
        'displayUnits',
        'displayJobs',
        'displayJobTracking',
        'setupFilters',
        'updateTimeline'
    ]
    
    for func in functions:
        pattern = f'function {func}\\s*\\('
        if re.search(pattern, content):
            print(f"✅ {func}() - defined")
            
            # Check if it's called
            if f'{func}()' in content or f'{func}(filtered)' in content or f'{func}(data)' in content:
                print(f"   → Called in code")
            else:
                print(f"   ⚠️  Not called anywhere")
        else:
            print(f"❌ {func}() - NOT defined")


def main():
    """Run all tests"""
    
    print("\n╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "DASHBOARD ERROR DETECTION TEST SUITE" + " " * 17 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Run tests
    print("\n[1/3] Validating JavaScript syntax...")
    js_valid = validate_js_syntax()
    
    print("\n[2/3] Analyzing function definitions...")
    analyze_dashboard_functions()
    
    print("\n[3/3] Checking JSON file validity...")
    check_json_validity()
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    if js_valid:
        print("✅ All checks passed - dashboard should load without errors")
    else:
        print("⚠️  Some issues found - check dashboard for errors")
    
    print("\nTo see runtime errors:")
    print("  1. Open http://localhost:8000 in browser")
    print("  2. Press F12 to open Developer Tools")
    print("  3. Check Console tab for error messages")
    print("  4. Check Network tab for failed requests")
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
