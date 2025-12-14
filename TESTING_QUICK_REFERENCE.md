# Quick Testing Commands

## Run Tests Locally

```bash
# Run all tests
python3 run_tests.py

# Verbose output
python3 run_tests.py --verbose

# With coverage report
python3 run_tests.py --coverage

# With HTML coverage report
python3 run_tests.py --html
# Opens in: htmlcov/index.html
```

## Coverage Metrics

```bash
# Show coverage summary
python3 tools/coverage_metrics.py

# Show detailed per-file coverage
python3 tools/coverage_metrics.py --detailed

# Generate HTML report and save metrics
python3 tools/coverage_metrics.py --html --save
```

## Watch Mode (Auto-run on File Changes)

```bash
# Watch and auto-run tests when files change
python3 tools/watch_tests.py

# Verbose output
python3 tools/watch_tests.py --verbose
```

## Run Specific Tests

```bash
# Test specific file
python3 -m unittest tests.test_download_job_pages

# Test specific class
python3 -m unittest tests.test_download_job_pages.TestJobPagePath

# Test specific method
python3 -m unittest tests.test_download_job_pages.TestJobPagePath.test_path_generation
```

## Install Pre-Commit Hook

```bash
# Install git hook (runs tests before each commit)
python3 scripts/install_hooks.py

# Bypass hook if needed (not recommended)
git commit --no-verify
```

## Test Coverage

Tests cover:
- ✓ 42 unit tests across download_job_pages.py and parse_html_to_json.py
- ✓ Path generation, file operations, content extraction
- ✓ Edge cases and error handling
- ✓ Integration workflows

## CI/CD

Tests automatically run on:
- GitHub Actions (Python 3.9, 3.10, 3.11, 3.12)
- Pre-commit hooks (local commits)
- Watch mode (development)

## Test Results

All 42 tests passing ✓
