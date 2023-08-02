"""Platform for sensor integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Any

from mypermobil import (
    BATTERY_AMPERE_HOURS_LEFT,
    BATTERY_CHARGE_TIME_LEFT,
    BATTERY_DISTANCE_LEFT,
    BATTERY_INDOOR_DRIVE_TIME,
    BATTERY_MAX_AMPERE_HOURS,
    BATTERY_MAX_DISTANCE_LEFT,
    BATTERY_STATE_OF_CHARGE,
    BATTERY_STATE_OF_HEALTH,
    RECORDS_DISTANCE,
    RECORDS_DISTANCE_UNIT,
    RECORDS_SEATING,
    USAGE_ADJUSTMENTS,
    USAGE_DISTANCE,
)

from homeassistant import config_entries
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfLength,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import BATTERY_ASSUMED_VOLTAGE, DOMAIN, KM, LATITUDE, LONGITUDE, MILES_TO_KM
from .coordinator import MyPermobilCoordinator


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""


_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=50)


@dataclass
class PermobilRequiredKeysMixin:
    """Mixin for required keys."""

    value_fn: Callable[[Any], Any]


@dataclass
class PermobilSensorEntityDescription(
    SensorEntityDescription, PermobilRequiredKeysMixin
):
    """Describes Permobil sensor entity."""


def records_dist_fn(data: Any) -> float:
    """Find and calculate the record distance.

    This function gets the record distance from the data and converts it to kilometers if needed.
    """
    distance = data.records[RECORDS_DISTANCE[0]]
    distance_unit = data.records[RECORDS_DISTANCE_UNIT[0]]
    if distance_unit != KM:
        distance = distance * MILES_TO_KM
    return distance


SENSOR_DESCRIPTIONS: tuple[PermobilSensorEntityDescription, ...] = (
    PermobilSensorEntityDescription(
        # Current battery as a percentage
        value_fn=lambda data: data.nested_get(data.battery, BATTERY_STATE_OF_CHARGE),
        key=BATTERY_STATE_OF_CHARGE,
        translation_key="state_of_charge",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PermobilSensorEntityDescription(
        # Current battery health as a percentage of original capacity
        value_fn=lambda data: data.nested_get(data.battery, BATTERY_STATE_OF_HEALTH),
        key=BATTERY_STATE_OF_HEALTH,
        translation_key="state_of_health",
        icon="mdi:battery-heart-variant",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PermobilSensorEntityDescription(
        # Time until fully charged (displays 0 if not charging)
        value_fn=lambda data: data.nested_get(data.battery, BATTERY_CHARGE_TIME_LEFT),
        key=BATTERY_CHARGE_TIME_LEFT,
        translation_key="charge_time_left",
        icon="mdi:battery-clock",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PermobilSensorEntityDescription(
        # Distance possible on current change (km)
        value_fn=lambda data: data.nested_get(data.battery, BATTERY_DISTANCE_LEFT),
        key=BATTERY_DISTANCE_LEFT,
        translation_key="distance_left",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PermobilSensorEntityDescription(
        # Drive time possible on current charge
        value_fn=lambda data: data.nested_get(data.battery, BATTERY_INDOOR_DRIVE_TIME),
        key=BATTERY_INDOOR_DRIVE_TIME,
        translation_key="indoor_drive_time",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PermobilSensorEntityDescription(
        # Watt hours the battery can store given battery health
        value_fn=lambda data: data.nested_get(data.battery, BATTERY_MAX_AMPERE_HOURS)
        * BATTERY_ASSUMED_VOLTAGE,
        key=BATTERY_MAX_AMPERE_HOURS,
        translation_key="max_watt_hours",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PermobilSensorEntityDescription(
        # Current amount of watt hours in battery
        value_fn=lambda data: data.nested_get(data.battery, BATTERY_AMPERE_HOURS_LEFT)
        * BATTERY_ASSUMED_VOLTAGE,
        key=BATTERY_AMPERE_HOURS_LEFT,
        translation_key="watt_hours_left",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PermobilSensorEntityDescription(
        # Distance that can be traveled with full charge given battery health (km)
        value_fn=lambda data: data.nested_get(data.battery, BATTERY_MAX_DISTANCE_LEFT),
        key=BATTERY_MAX_DISTANCE_LEFT,
        translation_key="max_distance_left",
        icon="mdi:map-marker-distance",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PermobilSensorEntityDescription(
        # Distance traveled today monotonically increasing, resets every 24h (km)
        value_fn=lambda data: data.nested_get(data.daily_usage, USAGE_DISTANCE),
        key=USAGE_DISTANCE,
        translation_key="usage_distance",
        icon="mdi:map-marker-distance",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PermobilSensorEntityDescription(
        # Number of adjustments monotonically increasing, resets every 24h
        value_fn=lambda data: data.nested_get(data.daily_usage, USAGE_ADJUSTMENTS),
        key=USAGE_ADJUSTMENTS,
        translation_key="usage_adjustments",
        icon="mdi:seat-recline-extra",
        native_unit_of_measurement="adjustments",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PermobilSensorEntityDescription(
        # Largest number of adjustemnts in a single 24h period, monotonically increasing, never resets
        value_fn=lambda data: data.nested_get(data.records, RECORDS_SEATING),
        key=RECORDS_SEATING,
        translation_key="record_adjustments",
        icon="mdi:seat-recline-extra",
        native_unit_of_measurement="adjustments",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PermobilSensorEntityDescription(
        # Record of largest distance travelled in a day, monotonically increasing, never resets
        value_fn=records_dist_fn,
        key=RECORDS_DISTANCE,
        translation_key="record_distance",
        icon="mdi:map-marker-distance",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
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
        PermobilSensor(coordinator=coordinator, description=description)
        for description in SENSOR_DESCRIPTIONS
    )
    async_add_entities([PermobilPositionSensor(coordinator=coordinator)])


class PermobilSensor(CoordinatorEntity[MyPermobilCoordinator], SensorEntity):
    """Representation of a Sensor.

    This implements the common functions of all sensors.
    """

    _attr_has_entity_name = True
    _attr_suggested_display_precision = 0
    entity_description: PermobilSensorEntityDescription

    def __init__(
        self,
        coordinator: MyPermobilCoordinator,
        description: PermobilSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.p_api.email}_{self.entity_description.key}"
        )

    @property
    def native_value(self) -> float | None:
        """Return the value of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)


class PermobilPositionSensor(SensorEntity):
    """Position of wheelchair sensor."""

    _attr_name = "Permobil Position Sensor"
    _attr_icon = "mdi:map-marker-question"
    _show_on_map = False
    _location_data: dict[str, str] = {}

    def __init__(self, coordinator: MyPermobilCoordinator) -> None:
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.p_api.email}_position"

    @property
    def native_value(self) -> str:
        """Get battery and position information."""

        lat = self.coordinator.data.position.get(LATITUDE)
        lng = self.coordinator.data.position.get(LONGITUDE)
        if not lat or not lng:
            self._location_data = {}
            self._show_on_map = False
            self._attr_available = False
            self._attr_icon = "mdi:map-marker-off"
            return "Position Unknown"

        self._location_data = {
            ATTR_LATITUDE: str(lat),
            ATTR_LONGITUDE: str(lng),
        }
        self._show_on_map = False
        self._attr_icon = "mdi:map-marker"
        return "Visible on Map"

    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Return latitude value of the device."""
        return self._location_data
