"""The MyPermobil integration."""
from __future__ import annotations

import logging

from mypermobil import MyPermobil, MyPermobilClientException, MyPermobilException

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_CODE,
    CONF_EMAIL,
    CONF_ID,
    CONF_REGION,
    CONF_TOKEN,
    CONF_TTL,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import APPLICATION, DOMAIN
from .coordinator import MyPermobilCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MyPermobil from a config entry."""

    # create the API object from the config and save it in hass
    session = hass.helpers.aiohttp_client.async_get_clientsession()
    p_api = MyPermobil(
        application=APPLICATION,
        session=session,
        email=entry.data.get(CONF_EMAIL),
        region=entry.data.get(CONF_REGION),
        code=entry.data.get(CONF_CODE),
        token=entry.data.get(CONF_TOKEN),
        expiration_date=entry.data.get(CONF_TTL),
        product_id=entry.data.get(CONF_ID),
    )
    try:
        p_api.self_authenticate()
    except MyPermobilClientException as err:
        _LOGGER.error("Permobil: %s", err)
        raise ConfigEntryNotReady(f"Permobil Config error for {p_api.email}") from err

    # create the coordinator with the API object
    coordinator = MyPermobilCoordinator(hass, p_api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry to an entry that has a product."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:
        new = config_entry.data.copy()
        try:
            session = hass.helpers.aiohttp_client.async_get_clientsession(hass)
            p_api = MyPermobil(
                APPLICATION,
                session,
                email=new[CONF_EMAIL],
                region=new[CONF_REGION],
                code=new[CONF_CODE],
                token=new[CONF_TOKEN],
                expiration_date=new[CONF_TTL],
            )
            p_api.self_authenticate()
            new[CONF_ID] = await p_api.request_product_id()
        except MyPermobilException as err:
            _LOGGER.error("Permobil: %s", err)
            raise ConfigEntryNotReady(
                f"Permobil Config error for {p_api.email} in migration from version 1"
            ) from err

        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new)

    _LOGGER.info("Migration to version %s successful", config_entry.version)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
