# Tests

This directory contains test configuration for the Torque integration.

## Current State

The tests require proper Home Assistant test infrastructure to run effectively. The current tests are placeholder implementations that outline what should be tested.

## Setup

The tests require proper PYTHONPATH configuration to import custom_components and Home Assistant test utilities. This is handled automatically in the CI workflow.

## Running Tests Locally

To run tests locally, you would need Home Assistant's test dependencies installed:

```bash
# Install Home Assistant test dependencies first
pip install homeassistant pytest pytest-homeassistant-custom-component

# Then run tests
PYTHONPATH=. pytest tests/ -v
```

## Test Infrastructure

- `conftest.py` - Test configuration and fixtures
- `test_sensor.py` - Placeholder tests for sensor functionality
- Test files should follow the pattern `test_*.py`

## Adding Tests

When adding tests for the integration, you can use the fixtures provided in `conftest.py` such as:

- `mock_hass` - Mock Home Assistant instance
- `mock_config_entry` - Mock configuration entry

You can import constants and modules from the custom component using:

```python
from custom_components.torque.const import DOMAIN, DEFAULT_NAME
```

## Recommended Test Coverage

- Config flow setup and validation
- Options flow functionality
- Sensor creation and state updates
- Icon selection logic
- Unique ID generation
- Unit conversion logic
- Data parsing and validation
- Error handling scenarios
