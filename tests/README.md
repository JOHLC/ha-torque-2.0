# Tests

This directory contains test configuration for the Torque integration.

## Setup

The tests require proper PYTHONPATH configuration to import custom_components. This is handled automatically in the CI workflow.

## Running Tests Locally

To run tests locally, set the PYTHONPATH to the repository root:

```bash
PYTHONPATH=. pytest tests/ -v
```

## Test Infrastructure

- `conftest.py` - Test configuration and fixtures
- Test files should follow the pattern `test_*.py`

## Adding Tests

When adding tests for the integration, you can use the fixtures provided in `conftest.py` such as:

- `mock_hass` - Mock Home Assistant instance
- `mock_config_entry` - Mock configuration entry

You can import constants and modules from the custom component using:

```python
from custom_components.torque.const import DOMAIN, DEFAULT_NAME
```
