"""Test the MyPermobil config flow."""
from unittest.mock import patch

from mypermobil import MyPermobilAPIException, MyPermobilConnectionException
import pytest

from homeassistant.components.permobil import async_setup_entry, async_unload_entry
from homeassistant.components.permobil.const import DOMAIN, KM, MILES
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DATA, DATA2, INVALID_DATA

from tests.common import MockConfigEntry

pytestmark = pytest.mark.usefixtures("mock_setup_entry")


async def test_async_setup_entry_and_unload(hass: HomeAssistant) -> None:
    """Test the async_setup_entry and async_unload_entry functions."""
    # Create a mock config entry
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=DATA,
    )
    config_entry.add_to_hass(hass)

    # Call the async_setup_entry function
    with patch(
        "homeassistant.components.permobil.MyPermobil.request_item",
        return_value=MILES,
    ):
        assert await async_setup_entry(hass, config_entry)

    # Assert that the integration data is set correctly in the hass.data dictionary
    assert config_entry.entry_id in hass.data[DOMAIN]
    assert hass.data[DOMAIN][config_entry.entry_id] == config_entry.data

    # Assert that the MyPermobil API object is created and stored in hass.data
    assert DOMAIN in hass.data
    assert "api" in hass.data[DOMAIN]
    assert (
        hass.data[DOMAIN]["api"][config_entry.entry_id].email
        == config_entry.data["email"]
    )

    # Assert that the unit of distance is set correctly in hass.data
    assert "unit" in hass.data[DOMAIN]
    assert hass.data[DOMAIN]["unit"][config_entry.entry_id] == MILES

    # Unload the config entry
    assert await async_unload_entry(hass, config_entry)

    # Assert that the integration data is removed from the hass.data dictionary
    assert config_entry.entry_id not in hass.data[DOMAIN]


async def test_async_setup_entry_fail_authenticate(hass: HomeAssistant) -> None:
    """Test for when the config entry contains invalid data."""
    # Create a mock config entry
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=INVALID_DATA,
    )
    config_entry.add_to_hass(hass)

    # Call the async_setup_entry function
    with patch(
        "homeassistant.components.permobil.MyPermobil.request_item",
        return_value=KM,
    ), pytest.raises(ConfigEntryNotReady):
        assert await async_setup_entry(hass, config_entry)


async def test_async_setup_entry_invalid_unit(hass: HomeAssistant) -> None:
    """Test for when the api returns an invalid unit of distance."""
    # Create a mock config entry
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=DATA,
    )
    config_entry.add_to_hass(hass)

    # Call the async_setup_entry function
    with patch(
        "homeassistant.components.permobil.MyPermobil.request_item",
        return_value="invalid_unit",
    ):
        assert await async_setup_entry(hass, config_entry)

    # Assert that the integration data is set correctly in the hass.data dictionary
    assert config_entry.entry_id in hass.data[DOMAIN]
    assert hass.data[DOMAIN][config_entry.entry_id] == config_entry.data

    # Assert that the MyPermobil API object is created and stored in hass.data
    assert DOMAIN in hass.data
    assert "api" in hass.data[DOMAIN]
    assert (
        hass.data[DOMAIN]["api"][config_entry.entry_id].email
        == config_entry.data["email"]
    )

    # Assert that the unit of distance defaulted to KM
    assert "unit" in hass.data[DOMAIN]
    assert hass.data[DOMAIN]["unit"][config_entry.entry_id] == KM

    # Unload the config entry
    assert await async_unload_entry(hass, config_entry)

    # Assert that the integration data is removed from the hass.data dictionary
    assert config_entry.entry_id not in hass.data[DOMAIN]


async def test_async_setup_entry_fail_unit1(hass: HomeAssistant) -> None:
    """Test for when the api does not answer because of invalid cridential."""
    # Create a mock config entry
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=DATA,
    )
    config_entry.add_to_hass(hass)

    # Call the async_setup_entry function
    with patch(
        "homeassistant.components.permobil.MyPermobil.request_item",
        side_effect=MyPermobilAPIException,
    ), pytest.raises(ConfigEntryNotReady):
        assert await async_setup_entry(hass, config_entry)


async def test_async_setup_entry_fail_unit2(hass: HomeAssistant) -> None:
    """Test for when the api does not answer because it is down."""
    # Create a mock config entry
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=DATA,
    )
    config_entry.add_to_hass(hass)

    # Call the async_setup_entry function
    with patch(
        "homeassistant.components.permobil.MyPermobil.request_item",
        side_effect=MyPermobilConnectionException,
    ), pytest.raises(ConfigEntryNotReady):
        assert await async_setup_entry(hass, config_entry)


async def test_async_setup_multiple_configs(hass: HomeAssistant) -> None:
    """Test adding multiple config entries."""
    config_entry1 = MockConfigEntry(
        domain=DOMAIN,
        data=DATA,
    )
    config_entry2 = MockConfigEntry(
        domain=DOMAIN,
        data=DATA2,
    )
    config_entry1.add_to_hass(hass)
    config_entry2.add_to_hass(hass)

    # Call the async_setup_entry function
    with patch(
        "homeassistant.components.permobil.MyPermobil.request_item",
        return_value=MILES,
    ):
        assert await async_setup_entry(hass, config_entry1)

    with patch(
        "homeassistant.components.permobil.MyPermobil.request_item",
        return_value=KM,
    ):
        assert await async_setup_entry(hass, config_entry2)

    # Assert that the integration data is set correctly in the hass.data dictionary
    assert config_entry1.entry_id in hass.data[DOMAIN]
    assert config_entry2.entry_id in hass.data[DOMAIN]
    assert hass.data[DOMAIN][config_entry1.entry_id] == config_entry1.data
    assert hass.data[DOMAIN][config_entry2.entry_id] == config_entry2.data

    # Assert that the MyPermobil API object is created and stored in hass.data
    assert DOMAIN in hass.data
    assert "api" in hass.data[DOMAIN]
    assert (
        hass.data[DOMAIN]["api"][config_entry1.entry_id].email
        == config_entry1.data["email"]
    )
    assert (
        hass.data[DOMAIN]["api"][config_entry2.entry_id].email
        == config_entry2.data["email"]
    )

    # Assert that the unit of distance is set correctly in hass.data
    assert "unit" in hass.data[DOMAIN]
    assert hass.data[DOMAIN]["unit"][config_entry1.entry_id] == MILES
    assert "unit" in hass.data[DOMAIN]
    assert hass.data[DOMAIN]["unit"][config_entry2.entry_id] == KM

    # Unload the config entry
    # Assert that the integration data is removed from the hass.data dictionary
    assert await async_unload_entry(hass, config_entry1)
    assert config_entry1.entry_id not in hass.data[DOMAIN]
    assert await async_unload_entry(hass, config_entry2)
    assert config_entry2.entry_id not in hass.data[DOMAIN]
