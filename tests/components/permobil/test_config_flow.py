"""Test the MyPermobil config flow."""

from unittest.mock import MagicMock, patch

import pytest

from homeassistant import config_entries
from homeassistant.components.permobil import config_flow
from homeassistant.components.permobil.const import DOMAIN
from homeassistant.const import CONF_CODE, CONF_EMAIL, CONF_REGION, CONF_TOKEN, CONF_TTL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .const import (
    EMPTY,
    INVALID_CODE,
    INVALID_EMAIL,
    INVALID_REGION,
    MOCK_CODE,
    MOCK_DATE,
    MOCK_EMAIL,
    MOCK_REGION,
    MOCK_REGIONS,
    MOCK_TOKEN,
    MOCK_TOKEN_RESPONSE,
)

pytestmark = pytest.mark.usefixtures("mock_setup_entry")


async def test_flow_init(hass: HomeAssistant) -> None:
    """Test config flow init."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == FlowResultType.FORM  # type: ignore
    assert result["errors"] == {}  # type: ignore


async def test_form_empty_email(hass: HomeAssistant) -> None:
    """Test we handle empty email."""
    _result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "user"}
    )
    result = await hass.config_entries.flow.async_configure(
        _result["flow_id"],
        user_input={CONF_EMAIL: EMPTY},
    )

    assert result["type"] == FlowResultType.FORM  # type: ignore
    assert result["errors"].get("reason") == "empty_email"  # type: ignore


async def test_form_empty_code(hass: HomeAssistant) -> None:
    """Test we handle empty code."""
    _result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "email_code"}
    )
    result = await hass.config_entries.flow.async_configure(
        _result["flow_id"],
        user_input={CONF_CODE: EMPTY},
    )
    assert result["type"] == FlowResultType.FORM  # type: ignore
    assert result["errors"].get("reason") == "empty_code"  # type: ignore


async def test_form_invalid_email(hass: HomeAssistant) -> None:
    """Test we handle invalid email."""
    _result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "user"}
    )
    result = await hass.config_entries.flow.async_configure(
        _result["flow_id"],
        user_input={CONF_EMAIL: INVALID_EMAIL},
    )
    assert result["type"] == FlowResultType.FORM  # type: ignore
    assert result["errors"].get("reason") == "invalid_email"  # type: ignore


async def test_form_invalid_region_no_match(hass: HomeAssistant) -> None:
    """Test we handle invalid region."""
    result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN,
        context={"source": "region"},
        data={CONF_REGION: INVALID_REGION},
    )
    assert result["type"] == FlowResultType.FORM  # type: ignore
    assert result["errors"].get("reason") == "invalid_region"  # type: ignore


async def test_form_invalid_region_api(hass: HomeAssistant) -> None:
    """Test we handle invalid region."""
    with patch(
        "homeassistant.components.permobil.config_flow.MyPermobil.request_application_code",
        side_effect=config_flow.MyPermobilAPIException,
    ), patch(
        "homeassistant.components.permobil.config_flow.PermobilConfigFlow.region_names",
        MOCK_REGIONS,
    ):
        result = await hass.config_entries.flow.async_init(
            config_flow.DOMAIN,
            context={"source": "region"},
            data={CONF_REGION: MOCK_REGION},
        )
    assert result["type"] == FlowResultType.FORM  # type: ignore
    assert result["errors"].get("reason") == "api_error"  # type: ignore


async def test_form_invalid_code(hass: HomeAssistant) -> None:
    """Test we handle invalid code."""
    result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN,
        context={"source": "email_code"},
        data={CONF_CODE: INVALID_CODE},
    )
    assert result["type"] == FlowResultType.FORM  # type: ignore
    assert result["errors"].get("reason") == "invalid_code"  # type: ignore


async def test_form_valid_email(hass: HomeAssistant) -> None:
    """Test we handle a valid email."""
    with patch(
        "homeassistant.components.permobil.config_flow.MyPermobil.request_region_names",
        return_value=MOCK_REGIONS,
    ) as mock:
        result = await hass.config_entries.flow.async_init(
            config_flow.DOMAIN,
            context={"source": "user"},
            data={CONF_EMAIL: MOCK_EMAIL},
        )
    expected_email = MOCK_EMAIL.replace(" ", "")
    assert result["type"] == FlowResultType.FORM  # type: ignore
    assert result["step_id"] == "region"  # type: ignore
    assert result["errors"] == {}  # type: ignore
    assert len(mock.mock_calls) == 1
    assert config_flow.PermobilConfigFlow.data.get(CONF_EMAIL) == expected_email


async def test_form_valid_region(hass: HomeAssistant) -> None:
    """Test we handle a valid region."""
    with patch(
        "homeassistant.components.permobil.config_flow.MyPermobil.request_application_code",
        return_value=None,
    ), patch(
        "homeassistant.components.permobil.config_flow.PermobilConfigFlow.region_names",
        MOCK_REGIONS,
    ):
        result = await hass.config_entries.flow.async_init(
            config_flow.DOMAIN,
            context={"source": "region"},
            data={CONF_REGION: MOCK_REGION},
        )

    expected_region = MOCK_REGIONS.get(MOCK_REGION)
    assert result["type"] == FlowResultType.FORM  # type: ignore
    assert result["step_id"] == "email_code"  # type: ignore
    assert result["errors"] == {}  # type: ignore
    assert config_flow.PermobilConfigFlow.data.get(CONF_REGION) == expected_region


async def test_form_valid_code(hass: HomeAssistant) -> None:
    """Test we handle a valid email."""
    with patch(
        "homeassistant.components.permobil.config_flow.MyPermobil.request_application_token",
        return_value=MOCK_TOKEN_RESPONSE,
    ), patch(
        "homeassistant.components.permobil.config_flow.MyPermobil.request_item",
        return_value="km",
    ), patch(
        "homeassistant.components.permobil.config_flow.MyPermobil.request_product_id",
        return_value="1234567890AB" * 2,
    ), patch(
        "homeassistant.components.permobil.config_flow.MyPermobil.self_authenticate",
        return_value=None,
    ):
        result = await hass.config_entries.flow.async_init(
            config_flow.DOMAIN,
            context={"source": "email_code"},
            data={CONF_CODE: MOCK_CODE},
        )
    expected_code = MOCK_CODE.replace(" ", "")
    assert result["type"] == FlowResultType.CREATE_ENTRY  # type: ignore
    assert result["data"].get(CONF_CODE) == expected_code  # type: ignore
    assert result["data"].get(CONF_TOKEN) == MOCK_TOKEN  # type: ignore
    assert result["data"].get(CONF_TTL) == MOCK_DATE  # type: ignore
    assert not result.get("errors")


async def test_form_connection_error_region_names(hass: HomeAssistant) -> None:
    """Test we handle a connection error."""
    with patch(
        "homeassistant.components.permobil.config_flow.MyPermobil.request_region_names",
        side_effect=config_flow.MyPermobilConnectionException,
    ):
        result = await hass.config_entries.flow.async_init(
            config_flow.DOMAIN,
            context={"source": "user"},
            data={CONF_EMAIL: MOCK_EMAIL},
        )

    assert result["type"] == FlowResultType.FORM  # type: ignore
    assert result["step_id"] == "region"  # type: ignore
    assert result["errors"].get("reason") == "connection_error"  # type: ignore


async def test_form_connection_error_region_app_code(hass: HomeAssistant) -> None:
    """Test we handle a connection error."""
    with patch(
        "homeassistant.components.permobil.config_flow.PermobilConfigFlow.region_names",
        MOCK_REGIONS,
    ), patch(
        "homeassistant.components.permobil.config_flow.MyPermobil.request_application_code",
        side_effect=config_flow.MyPermobilConnectionException,
    ):
        result = await hass.config_entries.flow.async_init(
            config_flow.DOMAIN,
            context={"source": "region"},
            data={CONF_REGION: MOCK_REGION},
        )

    assert result["type"] == FlowResultType.FORM  # type: ignore
    assert result["step_id"] == "region"  # type: ignore
    assert result["errors"].get("reason") == "connection_error"  # type: ignore


async def test_form_connection_error_token(hass: HomeAssistant) -> None:
    """Test we handle a connection error."""
    with patch(
        "homeassistant.components.permobil.config_flow.MyPermobil.request_application_token",
        side_effect=config_flow.MyPermobilConnectionException,
    ):
        result = await hass.config_entries.flow.async_init(
            config_flow.DOMAIN,
            context={"source": "email_code"},
            data={CONF_CODE: MOCK_CODE},
        )

    assert result["type"] == FlowResultType.FORM  # type: ignore
    assert result["step_id"] == "email_code"  # type: ignore
    assert result["errors"].get("reason") == "connection_error"  # type: ignore


async def test_validate_input() -> None:
    """Test validate input."""
    p_api = MagicMock()
    data = {
        "email": "test@example.com",
        "code": "123456",
        "token": "abcdef",
    }

    await config_flow.validate_input(p_api, data)

    assert p_api.set_email.called_once_with("test@example.com")
    assert p_api.set_code.called_once_with("123456")
    assert p_api.set_token.called_once_with("abcdef")


async def test_validate_input_missing_values() -> None:
    """Test validate input."""
    p_api = MagicMock()
    data = {
        "email": "test@example.com",
    }

    await config_flow.validate_input(p_api, data)

    assert p_api.set_email.called_once_with("test@example.com")
    assert not p_api.set_code.called
    assert not p_api.set_token.called
