"""The MyPermobil integration."""
from __future__ import annotations

import logging

from mypermobil import (
    ENDPOINT_VA_USAGE_RECORDS,
    RECORDS_DISTANCE_UNIT,
    MyPermobil,
    MyPermobilException,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_CODE,
    CONF_EMAIL,
    CONF_REGION,
    CONF_TOKEN,
    CONF_TTL,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import API, APPLICATION, DOMAIN, KM, MILES, UNIT

_LOGGER = logging.getLogger(__name__)


PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MyPermobil from a config entry."""
    default: dict = {
        API: {},
        UNIT: {},
    }
    hass.data.setdefault(DOMAIN, default)
    hass.data[DOMAIN][entry.entry_id] = entry.data
    config = hass.data[DOMAIN][entry.entry_id]

    # create the API object from the config and save it in hass
    session = hass.helpers.aiohttp_client.async_get_clientsession()
    p_api = MyPermobil(
        application=APPLICATION,
        session=session,
        email=config.get(CONF_EMAIL),
        region=config.get(CONF_REGION),
        code=config.get(CONF_CODE),
        token=config.get(CONF_TOKEN),
        expiration_date=config.get(CONF_TTL),
    )
    try:
        p_api.self_authenticate()
    except MyPermobilException as err:
        _LOGGER.error("Permobil: %s", err)
        raise ConfigEntryNotReady(f"Permobil Config error for {p_api.email}") from err
    hass.data[DOMAIN][API][entry.entry_id] = p_api

    p_api_unit: str = KM
    try:
        # find out what unit of distance the user has set
        p_api_unit = str(
            await p_api.request_item(
                RECORDS_DISTANCE_UNIT, endpoint=ENDPOINT_VA_USAGE_RECORDS
            )
        )
        if p_api_unit not in [KM, MILES]:
            _LOGGER.error("Unknown unit of distance: %s, defaulting to km", p_api_unit)
            p_api_unit = KM
    except MyPermobilException as err:
        _LOGGER.error("Permobil: %s", err)
        raise ConfigEntryNotReady(f"Permobil API error for {p_api.email}") from err
    hass.data[DOMAIN][UNIT][entry.entry_id] = p_api_unit

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        hass.data[DOMAIN][API].pop(entry.entry_id)
        hass.data[DOMAIN][UNIT].pop(entry.entry_id)

    return unload_ok
