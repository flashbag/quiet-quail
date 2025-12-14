# Testing Documentation

This document describes the testing infrastructure for the Quiet-Quail project.

## Quick Start

### Run All Tests
```bash
python3 run_tests.py              # Run all tests
python3 run_tests.py --verbose    # Verbose output
python3 run_tests.py --coverage   # With coverage report
```

### Run Specific Tests
```bash
python3 -m pytest tests/test_download_job_pages.py -v
python3 -m pytest tests/test_parse_html_to_json.py::TestExtractPostId -v
```

### Watch Mode - Auto-run Tests on Changes
```bash
python3 tools/watch_tests.py              # Watch and run tests
python3 tools/watch_tests.py --verbose    # Verbose output
```

## Test Structure

```
tests/
├── __init__.py                          # Package marker
├── test_download_job_pages.py           # Tests for download_job_pages.py
└── test_parse_html_to_json.py          # Tests for parse_html_to_json.py
```

## Covered Functions

### download_job_pages.py
- `get_job_page_path()` - Path generation for job files
- `extract_main_content()` - HTML content extraction
- `is_already_downloaded()` - Download status checking
- `is_job_closed()` - Closed job detection
- `log_cron_stats()` - Statistics logging

### parse_html_to_json.py
- `extract_post_id()` - Post ID extraction
- `parse_post_div()` - Job posting parsing
- (Integration tests for file parsing)

## Automatic Testing Triggers

### 1. Pre-Commit Hook
Runs tests before each commit to prevent breaking code from being committed.

**Installation:**
```bash
python3 scripts/install_hooks.py
```

**Behavior:**
- If any `scripts/*.py` file is staged for commit, tests will run
- Commit is blocked if tests fail
- Use `git commit --no-verify` to bypass (not recommended)

### 2. GitHub Actions CI
Automatically runs tests on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Changes to `scripts/`, `tests/`, or `requirements.txt`

**Matrix:** Tests run on Python 3.9, 3.10, 3.11, 3.12

**View Results:** https://github.com/flashbag/quiet-quail/actions

### 3. Watch Mode (Development)
Continuously monitors files and runs tests on changes.

```bash
python3 tools/watch_tests.py
```

This is useful during development to get immediate feedback.

## Test Categories

### Unit Tests
- Test individual functions in isolation
- Use temporary directories for file operations
- Test edge cases and error handling

### Integration Tests
- Test multiple components working together
- Simulate realistic workflows
- Verify data flows correctly between functions

## Test Examples

### Testing a Function
```python
class TestGetJobPagePath(unittest.TestCase):
    def test_path_generation(self):
        """Test correct path generation for job IDs."""
        path = get_job_page_path(123456)
        expected = Path('data/job-pages/123/456/job_123456.html')
        self.assertEqual(path, expected)
```

### Testing File Operations
```python
def setUp(self):
    """Create temporary directory for tests."""
    self.temp_dir = tempfile.TemporaryDirectory()
    self.original_cwd = os.getcwd()
    os.chdir(self.temp_dir.name)

def tearDown(self):
    """Clean up temporary directory."""
    os.chdir(self.original_cwd)
    self.temp_dir.cleanup()
```

## Continuous Integration Workflow

```
Developer makes changes to scripts/
        ↓
Pre-commit hook runs tests
        ↓
    Tests pass? → Commit allowed
        │
    Tests fail? → Commit blocked (fix and retry)
        ↓
Code pushed to GitHub
        ↓
GitHub Actions runs full test suite (Python 3.9-3.12)
        ↓
    All pass? → Green check on PR
        │
    Any fail? → Red X on PR (must fix)
```

## Coverage

Current test coverage includes:
- Core utility functions (path generation, content extraction)
- File operations (download checking, metadata logging)
- Error handling and edge cases
- Integration flows

To see detailed coverage:
```bash
python3 run_tests.py --coverage
```

## Adding New Tests

When adding new functions to `scripts/`:

1. Create/update corresponding test file in `tests/`
2. Write tests for:
   - Normal/happy path
   - Edge cases
   - Error conditions
3. Run tests locally: `python3 run_tests.py`
4. Watch mode for development: `python3 tools/watch_tests.py`

Example structure:
```python
class TestNewFunction(unittest.TestCase):
    def test_happy_path(self):
        """Normal operation."""
        result = new_function(valid_input)
        self.assertEqual(result, expected)
    
    def test_edge_case(self):
        """Handle edge cases."""
        result = new_function(edge_case_input)
        self.assertIsNotNone(result)
    
    def test_error_handling(self):
        """Gracefully handle errors."""
        result = new_function(invalid_input)
        self.assertFalse(result)
```

## Troubleshooting

### Tests fail with import errors
```bash
# Make sure you're in the project root
cd /path/to/quiet-quail

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov
```

### Watch script doesn't work
```bash
# Install watchdog
pip install watchdog
```

### Pre-commit hook doesn't run
```bash
# Reinstall hooks
python3 scripts/install_hooks.py

# Check hook file exists and is executable
ls -la .git/hooks/pre-commit
```

## Best Practices

1. **Write tests for new features** - Add tests alongside new code
2. **Keep tests fast** - Use temporary directories, mock network calls
3. **Test edge cases** - Don't just test the happy path
4. **Run tests before pushing** - Ensure local tests pass
5. **Fix failing CI immediately** - Don't let failures accumulate
6. **Use meaningful test names** - Test names should describe what they test

## References

- [unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
