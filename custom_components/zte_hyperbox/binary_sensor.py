import logging

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import (
    EntityCategory,
    UnitOfInformation,
    SIGNAL_STRENGTH_DECIBELS,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    STATE_ON,
    STATE_OFF
)
from datetime import datetime

from .const import DOMAIN
from .coordinator import HyperboxCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Sensors."""
    # This gets the data update coordinator from hass.data as specified in your __init__.py
    coordinator: HyperboxCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ].coordinator
    # Enumerate all the sensors in your data value from your DataUpdateCoordinator and add an instance of your sensor class
    # to a list for each one.
    # This maybe different in your specific case, depending on how your data is structured
    sensors = [
        HyperboxBinarySensor(coordinator, endpoint_key="network_info", data_key="nitz_sync_flag", positive_values=[1]), #Synchronisation aktiv
        HyperboxBinarySensor(coordinator, endpoint_key="network_info", data_key="simcard_roam", positive_values=["Internal", "International"]), #Roaming-Status der SIM
        HyperboxBinarySensor(coordinator, endpoint_key="network_info", data_key="lteca_state", positive_values=[1], visible=False), #CA Status
    ]

    # Create the sensors.
    async_add_entities(sensors)

class HyperboxBinarySensor(CoordinatorEntity):
    
    _attr_should_poll = False
    _attr_has_entity_name = True
    
    def __init__(self, coordinator: HyperboxCoordinator, endpoint_key: str, data_key: str, positive_values: list[any], icon: str = None, visible: bool = True, category: str = None) -> None:
        super().__init__(coordinator)
        self.device_info = coordinator.device_info
        self.translation_key = endpoint_key + "_" + data_key
        self.entity_registry_enabled_default = visible
        self._attr_unique_id = f"{coordinator.hostname}-{endpoint_key}-{data_key}"
        self._endpoint_key = endpoint_key
        self._data_key = data_key
        self._positive_values = positive_values
        if icon is not None:
            self._attr_icon = icon
        if category is not None:
            self._attr_entity_category = category

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()
    
    @property
    def is_on(self) -> bool:
        """Return the state of the sensor."""
        return getattr(self.coordinator.data, self._endpoint_key)[self._data_key] in self._positive_values
    
    @property
    def state(self):
        return STATE_ON if self.is_on else STATE_OFF
