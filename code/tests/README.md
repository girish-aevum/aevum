# Aevum Health Platform - Centralized Test Suite

This directory contains all tests for the Aevum Health Platform, organized in a centralized structure for better maintainability and comprehensive coverage.

## Directory Structure

The tests are organized by both app functionality and test type for maximum clarity and maintainability.

## Running Tests

### Using the Centralized Test Runner

```bash
# Run all tests
python tests/test_runner.py

# Run tests for specific app
python tests/test_runner.py --app auth

# Run specific test types
python tests/test_runner.py --type api

# Run with coverage reporting
python tests/test_runner.py --coverage
```

### Using Django's Test Command

```bash
# Run all tests
python manage.py test tests

# Run specific app tests
python manage.py test tests.authentication

# Run specific test types
python manage.py test tests.api
```

## Test Categories

### 1. App-Specific Tests
Located in `tests/{app_name}/`, these test the core functionality of individual apps.

### 2. API Tests (`tests/api/`)
Comprehensive API endpoint testing including authentication, validation, and response formats.

### 3. Integration Tests (`tests/integration/`)
Cross-app functionality and complex workflows that span multiple applications.

### 4. Performance Tests (`tests/performance/`)
Performance benchmarks, load testing, and resource usage monitoring.

## Coverage Reporting

Generate coverage reports to ensure comprehensive testing:

```bash
python tests/test_runner.py --coverage
```

## Best Practices

- Write tests first (TDD approach)
- Test both success and failure cases
- Use realistic test data
- Mock external dependencies
- Maintain high test coverage (>90%)

## Adding New Tests

1. Create test file in appropriate directory
2. Write failing tests first
3. Implement feature to make tests pass
4. Add integration tests if feature spans multiple apps 