"""Platform for binary sensor integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Any

from mypermobil import BATTERY_CHARGING

from homeassistant import config_entries
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MyPermobilCoordinator


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the binary sensor platform."""


_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=50)


@dataclass
class PermobilRequiredKeysMixin:
    """Mixin for required keys."""

    value_fn: Callable[[Any], Any]


@dataclass
class PermobilBinarySensorEntityDescription(
    BinarySensorEntityDescription, PermobilRequiredKeysMixin
):
    """Describes Permobil binary sensor entity."""


SENSOR_DESCRIPTIONS: tuple[PermobilBinarySensorEntityDescription, ...] = (
    PermobilBinarySensorEntityDescription(
        # binary sensor that indicates if the battery is charging
        value_fn=lambda data: data.nested_get(data.battery, BATTERY_CHARGING),
        key=BATTERY_CHARGING,
        translation_key="battery_charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create sensors from a config entry created in the integrations UI."""

    # load the coordinator from the config
    coordinator: MyPermobilCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    # create a sensor for each sensor description

    async_add_entities(
        PermobilBinarySensor(coordinator=coordinator, description=description)
        for description in SENSOR_DESCRIPTIONS
    )


class PermobilBinarySensor(
    CoordinatorEntity[MyPermobilCoordinator], BinarySensorEntity
):
    """Representation of a Pi-hole binary sensor."""

    entity_description: PermobilBinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MyPermobilCoordinator,
        description: PermobilBinarySensorEntityDescription,
    ) -> None:
        """Initialize a Pi-hole sensor."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.p_api.email}_{self.entity_description.key}"
        )

    @property
    def is_on(self) -> bool:
        """Return if the battery is charging."""

        return self.entity_description.value_fn(self.coordinator.data)
