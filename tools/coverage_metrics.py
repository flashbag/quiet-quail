#!/usr/bin/env python3
"""
Generate and analyze test coverage metrics for the scripts/ directory.

Usage:
    python3 tools/coverage_metrics.py              # Show coverage summary
    python3 tools/coverage_metrics.py --detailed   # Detailed per-file metrics
    python3 tools/coverage_metrics.py --html       # Generate HTML report
    python3 tools/coverage_metrics.py --save       # Save metrics to file
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

try:
    import coverage
    HAS_COVERAGE = True
except ImportError:
    HAS_COVERAGE = False
    print("Error: coverage module not installed")
    print("Install with: pip install coverage")
    sys.exit(1)


def run_coverage_analysis():
    """Run coverage analysis and return results."""
    # Create coverage instance for scripts directory
    cov = coverage.Coverage(source=['scripts'])
    cov.start()
    
    # Run tests
    import unittest
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=0)
    runner.run(suite)
    
    cov.stop()
    cov.save()
    
    return cov


def get_coverage_stats(cov):
    """Extract coverage statistics from coverage object."""
    # Get total coverage percentage
    total_coverage = cov.report(skip_covered=False, skip_empty=True, precision=2)
    
    # Get per-file stats
    file_stats = {}
    for filename in cov.get_data().measured_files():
        try:
            analysis = cov._analyze(filename)
            statements = len(analysis.statements)
            missing = len(analysis.missing)
            executed = statements - missing
            
            if statements > 0:
                percentage = (executed / statements) * 100
                file_stats[filename] = {
                    'statements': statements,
                    'executed': executed,
                    'missing': missing,
                    'coverage': round(percentage, 2)
                }
        except Exception as e:
            pass
    
    return {
        'total': total_coverage,
        'files': file_stats,
        'timestamp': datetime.now().isoformat()
    }


def print_summary(stats):
    """Print coverage summary."""
    print("\n" + "=" * 70)
    print("COVERAGE METRICS")
    print("=" * 70)
    print(f"Overall Coverage: {stats['total']:.1f}%")
    print(f"Timestamp: {stats['timestamp']}")
    print()


def print_detailed(stats):
    """Print detailed per-file coverage."""
    print("\nPer-File Coverage:")
    print("-" * 70)
    print(f"{'File':<40} {'Coverage':<12} {'Statements':<12}")
    print("-" * 70)
    
    for filename in sorted(stats['files'].keys()):
        file_info = stats['files'][filename]
        short_name = filename.replace('scripts/', '').replace('.py', '')
        coverage_pct = file_info['coverage']
        statements = file_info['statements']
        
        # Color code by coverage percentage
        if coverage_pct >= 90:
            status = "✓"
        elif coverage_pct >= 70:
            status = "~"
        else:
            status = "✗"
        
        print(f"{short_name:<40} {coverage_pct:>6.1f}% {coverage_pct:>4}{status:<6} {statements:>8} stmts")
    
    print("-" * 70)


def generate_html_report(cov):
    """Generate HTML coverage report."""
    html_dir = 'htmlcov'
    cov.html_report(directory=html_dir)
    print(f"\n✓ HTML coverage report generated in {html_dir}/")
    print(f"  Open {html_dir}/index.html in browser to view")


def save_metrics(stats, filename='coverage_metrics.json'):
    """Save coverage metrics to file."""
    metrics_file = Path(filename)
    with open(metrics_file, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"\n✓ Coverage metrics saved to {filename}")


def main():
    """Main entry point."""
    detailed = '--detailed' in sys.argv
    html = '--html' in sys.argv
    save = '--save' in sys.argv
    
    print("Running coverage analysis...")
    cov = run_coverage_analysis()
    
    print("Calculating metrics...")
    stats = get_coverage_stats(cov)
    
    # Print summary
    print_summary(stats)
    
    if detailed:
        print_detailed(stats)
    
    # Generate reports
    if html:
        generate_html_report(cov)
    
    if save:
        save_metrics(stats)
    
    # Print coverage badge
    coverage_pct = stats['total']
    if coverage_pct >= 80:
        badge = "🟢"
    elif coverage_pct >= 60:
        badge = "🟡"
    else:
        badge = "🔴"
    
    print(f"\nCoverage Badge: {badge} {coverage_pct:.1f}%")
    
    # Summary
    file_count = len(stats['files'])
    total_statements = sum(f['statements'] for f in stats['files'].values())
    total_executed = sum(f['executed'] for f in stats['files'].values())
    
    print(f"\nSummary:")
    print(f"  Files analyzed: {file_count}")
    print(f"  Total statements: {total_statements}")
    print(f"  Statements executed: {total_executed}")
    print(f"  Statements missed: {total_statements - total_executed}")


if __name__ == '__main__':
    main()
