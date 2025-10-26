# Quick Test Reference

## Files Structure

```
tests/
├── __init__.py                 # Test module marker
├── conftest.py                 # Shared fixtures and configuration
├── test_auth_db.py             # Auth system tests (22 tests)
├── test_inference.py           # Inference engine tests (7 tests)
├── test_model_loader.py        # Model loading tests (10 tests)
├── test_smoothing.py           # Smoothing algorithm tests (17 tests)
├── test_video_io.py            # Video I/O tests (14 tests)
└── test_videoCapture.py        # Webcam capture tests (14 tests)
```

## Quick Commands

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Module Tests
```bash
pytest tests/test_auth_db.py -v              # Auth tests
pytest tests/test_smoothing.py -v            # Smoothing tests
pytest tests/test_video_io.py -v             # Video I/O tests
```

### Run Specific Test Class
```bash
pytest tests/test_auth_db.py::TestCreateUser -v
pytest tests/test_smoothing.py::TestEMA -v
```

### Run Specific Test
```bash
pytest tests/test_auth_db.py::TestCreateUser::test_create_user_success -v
```

### Quiet Output (Summary Only)
```bash
pytest tests/ -q
```

### Show Print Statements
```bash
pytest tests/ -s
```

### Stop on First Failure
```bash
pytest tests/ -x
```

### Run Tests and Show Coverage
```bash
pytest tests/ --cov=auth --cov=ml --cov-report=term-missing
```

### Generate HTML Coverage Report
```bash
pytest tests/ --cov --cov-report=html
# Open htmlcov/index.html in browser
```

### Parallel Testing (Faster)
```bash
pytest tests/ -n auto
# (requires pytest-xdist: pip install pytest-xdist)
```

---

## Test Results Summary

✅ **84/90 tests passing (93.3%)**

### Passing Tests by Module
- ✅ auth/db.py: 21/22 (95%)
- ✅ ml/model_loader.py: 9/10 (90%)
- ✅ ml/inference.py: 5/7 (71%)
- ✅ ml/smoothing.py: 17/17 (100%)
- ✅ ml/video_io.py: 11/14 (79%)
- ✅ videoCapture.py: 12/14 (86%)

---

## Test Fixtures Available

From `conftest.py`:

```python
# Use in any test
def test_something(sample_frame):
    """sample_frame: Random BGR numpy array (480x640x3)"""
    pass

def test_batch(sample_frames):
    """sample_frames: List of 5 random frames"""
    pass

def test_video(sample_video_path):
    """sample_video_path: Path to temporary MP4 video file"""
    pass

def test_db(temp_db):
    """temp_db: Temporary database path for testing"""
    pass
```

---

## Common Assertions

```python
# List/Dict checks
assert isinstance(result, list)
assert isinstance(result, dict)
assert len(result) == expected_length

# Numeric checks
assert result > 0
np.testing.assert_array_almost_equal(array1, array2)

# Boolean checks
assert result is not None
assert result is True
assert 'key' in result

# Exception checks
with pytest.raises(ValueError):
    some_function_that_raises()

# Mock checks
mock_func.assert_called()
mock_func.assert_called_once()
mock_func.assert_called_with(arg1, arg2)
```

---

## Adding New Tests

1. Create test file: `tests/test_module_name.py`
2. Import module to test
3. Create test class: `class TestClassName:`
4. Write test methods: `def test_something(self):`
5. Run: `pytest tests/test_module_name.py -v`

Example:
```python
from module_to_test import some_function

class TestSomeFunction:
    def test_basic_case(self):
        result = some_function(input_data)
        assert result == expected_output
    
    def test_error_case(self):
        with pytest.raises(ValueError):
            some_function(invalid_input)
```

---

## Debugging Failed Tests

```bash
# Verbose with traceback
pytest tests/test_file.py::TestClass::test_name -vv --tb=long

# Drop into debugger on failure
pytest tests/ --pdb

# Print debugging info
pytest tests/ -s  # Shows print() statements
```

---

## CI/CD Integration

Add to `.github/workflows/tests.yml`:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt pytest
      - run: pytest tests/ -v
```

---

**Happy Testing!** 🧪✨
