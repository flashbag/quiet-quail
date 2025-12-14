# Test Coverage Metrics

## Coverage Commands

```bash
# Run tests with coverage report
python3 run_tests.py --coverage

# Generate HTML coverage report
python3 run_tests.py --html
# Opens in: htmlcov/index.html

# Show detailed coverage metrics
python3 tools/coverage_metrics.py

# Show detailed per-file metrics
python3 tools/coverage_metrics.py --detailed

# Generate HTML and save metrics
python3 tools/coverage_metrics.py --html --save
```

## Current Coverage Status

### Test Suite Stats
- **Total Tests**: 42 ✓
- **Test Files**: 2
  - `test_download_job_pages.py` - 35 tests
  - `test_parse_html_to_json.py` - 7 tests
- **Success Rate**: 100%

### Functions Under Test

#### download_job_pages.py
- ✅ `log_cron_stats()` - Statistics logging
- ✅ `get_job_page_path()` - Path generation
- ✅ `is_job_closed()` - Closed job detection
- ✅ `extract_main_content()` - Content extraction
- ✅ `is_already_downloaded()` - Download status checking
- ✅ `get_new_jobs_from_json()` - Job discovery
- ✅ `generate_all_job_metadata()` - Metadata generation
- ✅ `download_job_page()` - Job downloading
- ✅ `main()` - Main flow

#### parse_html_to_json.py
- ✅ `extract_post_id()` - ID extraction
- (Integration tests for file parsing)

## Coverage Report Generation

The testing infrastructure automatically generates coverage data:

1. **Terminal Report**
   ```bash
   python3 run_tests.py --coverage
   ```
   Shows statement-level coverage in terminal

2. **HTML Report**
   ```bash
   python3 run_tests.py --html
   ```
   Generates interactive HTML coverage report in `htmlcov/`

3. **JSON Metrics**
   ```bash
   python3 tools/coverage_metrics.py --save
   ```
   Saves to `coverage_metrics.json` for tracking over time

## Coverage Goals

- **Immediate** (Current): 80%+ overall line coverage
- **Near-term**: 90%+ for critical scripts
- **Long-term**: 95%+ comprehensive coverage

## What's Covered

✅ **Edge Cases**
- Empty files, missing files
- Invalid inputs
- Malformed HTML
- Unicode/special characters

✅ **Error Handling**
- Network errors
- File I/O errors
- Parsing failures
- Type errors

✅ **Integration Flows**
- Download detection workflow
- Metadata generation pipeline
- Statistics logging

## What to Test When Adding Features

When adding new functionality:

1. Add unit tests to corresponding `test_*.py` file
2. Test happy path, edge cases, and errors
3. Run `python3 run_tests.py --coverage` to check impact
4. Maintain 80%+ coverage minimum
5. Update this document if coverage changes significantly

## CI/CD Integration

Coverage is tracked automatically in:
- GitHub Actions (Python 3.9-3.12)
- Pre-commit hooks (local development)
- Coverage metrics file (tracking over time)

## Known Limitations

- Some scripts (reorganize_job_pages.py, fetch_lobbyx.py) require external resources (Playwright, network) and have minimal unit test coverage due to integration complexity
- Focus is on testable utility functions in download_job_pages.py and parse_html_to_json.py

## Improving Coverage

To improve coverage:

1. Identify untested code: `python3 run_tests.py --html`
2. Write tests in `tests/test_*.py`
3. Run coverage tool: `python3 tools/coverage_metrics.py --detailed`
4. Commit with improved coverage

## Resources

- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [pytest Documentation](https://docs.pytest.org/)
