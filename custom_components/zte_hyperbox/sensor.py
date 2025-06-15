import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import EntityCategory, UnitOfInformation, SIGNAL_STRENGTH_DECIBELS
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
        MessageSensor(coordinator),
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="real_rx_speed", conversion_rate=1000, unit=UnitOfInformation.MEGABITS, state_class=SensorStateClass.MEASUREMENT),
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="real_tx_speed", conversion_rate=1000, unit=UnitOfInformation.MEGABITS, state_class=SensorStateClass.MEASUREMENT),
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="total_rx_bytes", conversion_rate=1000000000, unit=UnitOfInformation.GIGABYTES, state_class=SensorStateClass.TOTAL_INCREASING),
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="total_tx_bytes", conversion_rate=1000000000, unit=UnitOfInformation.GIGABYTES, state_class=SensorStateClass.TOTAL_INCREASING),
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="signalbar", category=EntityCategory.DIAGNOSTIC),
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="nr5g_rsrp", unit=SIGNAL_STRENGTH_DECIBELS, state_class=SensorStateClass.MEASUREMENT, category=EntityCategory.DIAGNOSTIC, visible=False),
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="lte_rsrp", unit=SIGNAL_STRENGTH_DECIBELS, state_class=SensorStateClass.MEASUREMENT, category=EntityCategory.DIAGNOSTIC, visible=False),
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="network_provider_fullname", category=EntityCategory.DIAGNOSTIC),
    ]

    # Create the sensors.
    async_add_entities(sensors)

class HyperboxSensor(CoordinatorEntity):
    
    _attr_should_poll = False
    _attr_has_entity_name = True
    
    def __init__(self, coordinator: HyperboxCoordinator, endpoint_key: str, data_key: str, unit: str = None, conversion_rate: int = None, icon: str = None, visible: bool = True, category: str = None, state_class: str = None) -> None:
        super().__init__(coordinator)
        self.device_info = coordinator.device_info
        self.translation_key = endpoint_key + "_" + data_key
        self.entity_registry_enabled_default = visible
        self._attr_unique_id = f"{coordinator.hostname}-{endpoint_key}-{data_key}"
        self._endpoint_key = endpoint_key
        self._data_key = data_key
        self._state_class = state_class
        self._conversion_rate = conversion_rate
        if unit is not None:
            self._attr_unit_of_measurement = unit
        if icon is not None:
            self._attr_icon = icon
        if category is not None:
            self._attr_entity_category = category

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()
    
    @property
    def state(self):
        value = getattr(self.coordinator.data, self._endpoint_key)[self._data_key]
        if self._conversion_rate is not None:
            value = value / self._conversion_rate
        return value
    
    @property
    def extra_state_attributes(self):
        if self._state_class is not None:
            return {
                "state_class": self._state_class
            }

class MessageSensor(CoordinatorEntity):
    
    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_icon = "mdi:mail"
    
    def __init__(self, coordinator: HyperboxCoordinator) -> None:
        super().__init__(coordinator)
        self.device_info = coordinator.device_info
        self.translation_key = "messages"
        self._attr_unique_id = f"{coordinator.hostname}-{self.translation_key}"

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()
    
    @property
    def state(self):
        return len(self.coordinator.data.sms_messages)
    
    @property
    def extra_state_attributes(self):
        attr = {}
        for index in range(len(self.coordinator.data.sms_messages)):
            message = self.coordinator.data.sms_messages[index]
            attr[f"message{index}_content"] = message['content']
            attr[f"message{index}_date"] = datetime.fromtimestamp(message['date'])
            attr[f"message{index}_number"] = message['number']
        return attr
