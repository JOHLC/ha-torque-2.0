# Tests

This directory contains comprehensive tests for the Torque integration.

## Running Tests

To run all tests:
```bash
pytest tests/
```

To run tests with coverage:
```bash
pytest tests/ --cov=custom_components.torque --cov-report=html
```

## Test Structure

- `conftest.py` - Test fixtures and configuration
- `test_config_flow.py` - Tests for configuration flow
- `test_sensor.py` - Tests for sensor functionality
- `test_init.py` - Tests for integration setup/teardown

## Requirements

The tests require the following packages:
- pytest
- pytest-homeassistant-custom-component
- pytest-cov (for coverage reporting)
