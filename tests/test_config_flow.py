"""Test the Torque config flow."""
from __future__ import annotations

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.torque.const import CONF_EMAIL, CONF_NAME, DEFAULT_NAME, DOMAIN


async def test_flow_user_init(hass: HomeAssistant) -> None:
    """Test the initial user flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_flow_user_success(hass: HomeAssistant) -> None:
    """Test successful user flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_EMAIL: "test@example.com",
            CONF_NAME: "My Car",
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "My Car"
    assert result["data"] == {
        CONF_EMAIL: "test@example.com",
        CONF_NAME: "My Car",
    }


async def test_flow_user_default_name(hass: HomeAssistant) -> None:
    """Test user flow with default vehicle name."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_EMAIL: "test@example.com",
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == DEFAULT_NAME
    assert result["data"] == {
        CONF_EMAIL: "test@example.com",
        CONF_NAME: DEFAULT_NAME,
    }


async def test_flow_user_invalid_email(hass: HomeAssistant) -> None:
    """Test user flow with invalid email."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_EMAIL: "invalid-email",
            CONF_NAME: "My Car",
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_EMAIL: "invalid_email"}


async def test_flow_user_duplicate_email(hass: HomeAssistant) -> None:
    """Test user flow with duplicate email (already configured)."""
    # First entry
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_EMAIL: "test@example.com",
            CONF_NAME: "First Car",
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY

    # Try to add same email again
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_EMAIL: "test@example.com",
            CONF_NAME: "Second Car",
        },
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_options_flow(hass: HomeAssistant, mock_config_entry) -> None:
    """Test options flow."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "hide_pids": "41,42",
            "rename_map": "41:Engine Load,42:Coolant Temp",
            "unit_system": "imperial",
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        "hide_pids": "41,42",
        "rename_map": "41:Engine Load,42:Coolant Temp",
        "unit_system": "imperial",
    }


async def test_options_flow_defaults(hass: HomeAssistant, mock_config_entry) -> None:
    """Test options flow with default values."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    # Configure with empty input to test defaults
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {}
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
