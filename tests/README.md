# Tests Directory

This directory contains unit tests for the BrowserStack Uploader project.

## Test Files

### test_config.py
Tests for the configuration module:
- Environment variable substitution
- Configuration file structure
- File access and validation

### test_utils.py
Tests for utility functions:
- Version validation (semantic versioning)
- Parameter validation
- File formatting and operations

### test_local_storage.py
Tests for local storage and artifact validation:
- Path construction from templates
- File extension validation
- Magic bytes (file signature) validation

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run specific test file
```bash
pytest tests/test_config.py -v
```

### Run specific test class
```bash
pytest tests/test_config.py::TestConfigEnvironmentVariables -v
```

### Run specific test function
```bash
pytest tests/test_config.py::TestConfigEnvironmentVariables::test_env_var_substitution -v
```

### Run with verbose output
```bash
pytest tests/ -v
```

### Run with coverage report
```bash
pytest tests/ --cov=src --cov-report=html
```

## Test Structure

Each test file follows this structure:

```python
class TestFeatureName:
    """Test description"""

    def test_specific_behavior(self):
        """Test specific behavior of feature"""
        # Arrange - set up test data
        # Act - perform operation
        # Assert - verify results
        assert result == expected
```

## Writing New Tests

When adding new tests:

1. **Follow naming convention**: `test_*.py` files and `test_*()` functions
2. **Group related tests**: Use test classes to organize related tests
3. **Use descriptive names**: Test names should describe what they test
4. **Add docstrings**: Explain what each test does
5. **Keep tests simple**: Each test should test one thing
6. **Use arrange-act-assert**: Clear test structure

Example:
```python
def test_valid_input_returns_success(self):
    """Test that valid input returns success"""
    # Arrange
    valid_input = 'test_data'

    # Act
    result = process_input(valid_input)

    # Assert
    assert result is True
```

## Best Practices

- Tests should be independent and not rely on each other
- Use fixtures for common test setup
- Mock external dependencies (API calls, file I/O)
- Test both success and failure cases
- Keep tests focused and readable
- Run tests regularly during development

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```bash
# In Jenkins or GitHub Actions
pytest tests/ --cov=src --junitxml=test-results.xml
```

## Dependencies

Make sure you have pytest installed:
```bash
pip install pytest pytest-cov
```

## Future Test Coverage

As you add features to the project, add corresponding tests:
- API integration tests (BrowserStack, GitHub)
- YAML file manipulation tests
- Git operation tests
- Teams notification tests
- End-to-end workflow tests
