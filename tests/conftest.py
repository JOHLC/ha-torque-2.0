"""Test configuration for Torque integration tests."""
import asyncio
import pytest
from unittest.mock import Mock

# Import constants from the custom component
from custom_components.torque.const import DOMAIN, DEFAULT_NAME

@pytest.fixture
def mock_hass():
    """Return a mock HomeAssistant instance."""
    return Mock()

@pytest.fixture
def mock_config_entry():
    """Return a mock config entry."""
    return Mock(
        domain=DOMAIN,
        title="Test Torque",
        data={"name": DEFAULT_NAME},
        options={}
    )

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()