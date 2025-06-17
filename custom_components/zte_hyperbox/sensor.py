import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import EntityCategory, UnitOfInformation, SIGNAL_STRENGTH_DECIBELS, SIGNAL_STRENGTH_DECIBELS_MILLIWATT, UnitOfTime
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
        #📶 Netzwerkauswahl & -typ
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="network_type"), #Aktueller Verbindungstyp
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="domain_stat"), #Netzdomäne
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="net_select"), #Netzpräferenz
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="net_select_mode"), #Modus der Netzauswahl
        #📡 Signalstärke & Qualität
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="signalbar", state_class=SensorStateClass.MEASUREMENT), #Signalbalken-Anzeige
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="lte_rsrp", unit=SIGNAL_STRENGTH_DECIBELS_MILLIWATT, state_class=SensorStateClass.MEASUREMENT, category=EntityCategory.DIAGNOSTIC), #LTE Signalstärke
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="lte_rsrq", unit=SIGNAL_STRENGTH_DECIBELS, state_class=SensorStateClass.MEASUREMENT, category=EntityCategory.DIAGNOSTIC), #LTE Empfangsqualität
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="lte_rssi", unit=SIGNAL_STRENGTH_DECIBELS_MILLIWATT, state_class=SensorStateClass.MEASUREMENT, category=EntityCategory.DIAGNOSTIC), #LTE RSSI
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="lte_snr", unit=SIGNAL_STRENGTH_DECIBELS, state_class=SensorStateClass.MEASUREMENT, category=EntityCategory.DIAGNOSTIC), #LTE SNR
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="nr5g_rsrp", unit=SIGNAL_STRENGTH_DECIBELS_MILLIWATT, state_class=SensorStateClass.MEASUREMENT, category=EntityCategory.DIAGNOSTIC), #5G RSRP
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="nr5g_rsrq", unit=SIGNAL_STRENGTH_DECIBELS, state_class=SensorStateClass.MEASUREMENT, category=EntityCategory.DIAGNOSTIC), #5G RSRQ
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="nr5g_snr", unit=SIGNAL_STRENGTH_DECIBELS, state_class=SensorStateClass.MEASUREMENT, category=EntityCategory.DIAGNOSTIC), #5G SNR
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="nr5g_rssi", unit=SIGNAL_STRENGTH_DECIBELS_MILLIWATT, state_class=SensorStateClass.MEASUREMENT, category=EntityCategory.DIAGNOSTIC), #5G RSSI
        #🌍 Roaming & Netzbetreiber
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="rmcc"), #Roaming Mobile Country Code (Land)
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="rmnc"), #Roaming Mobile Network Code (Provider)
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="network_provider"), #Netzname kurz
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="network_provider_fullname"), #Netzname lang
        #📶 Zellinformationen
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="cell_id"), #LTE Cell ID
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="lte_pci"), #LTE Physical Cell ID
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="wan_active_band"), #Aktives LTE-Band
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="wan_active_channel"), #Aktiver LTE-Kanal
        #📡 5G-spezifisch
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="nr5g_cell_id"), #5G Cell ID
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="nr5g_pci"), #5G Physical Cell ID
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="nr5g_action_channel"), #5G Betriebsfrequenz (ARFCN)
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="nr5g_action_band"), #5G Band
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="nr5g_bandwidth", visible=False), #5G Bandbreite
        #📶 Carrier Aggregation (CA)
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="ltecasig", visible=False), #LTE CA Signalinfo (RSRP/SNR pro Band)
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="lteca", visible=False), #LTE CA Konfiguration
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="nrca", visible=False), #5G Carrier Aggregation Info
        #🔒 Netzsperren
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="lock_lte_cell", visible=False), #LTE-Zellsperre
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="lock_nr_cell", visible=False), #5G-Zellsperre
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="lte_band_lock", visible=False), #LTE-Band-Sperrmaske (hex)
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="gw_band_lock", visible=False), #GSM/WCDMA Bandlock
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="nr5g_sa_band_lock", visible=False), #5G SA Band Lock Liste
        #🕒 NITZ & Zeitsynchronisation
        HyperboxSensor(coordinator, endpoint_key="network_info", data_key="nitz_timezone"), #Zeitzone laut NITZ
        #📡 Verbindung & Datenverkehr (aktuelle Sitzung)
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="cid"), #Connection ID (Zelle / WWAN-Slot)
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="real_time", conversion_rate=3600, unit=UnitOfTime.HOURS, precision=2), #Aktuelle Betriebszeit
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="real_tx_bytes", conversion_rate=1073741824, unit=UnitOfInformation.GIGABYTES, precision=2), #Gesendete Bytes seit Neustart
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="real_rx_bytes", conversion_rate=1073741824, unit=UnitOfInformation.GIGABYTES, precision=2), #Empfangene Bytes seit Neustart
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="real_tx_packets", state_class=SensorStateClass.TOTAL_INCREASING), #Gesendete Pakete (aktuell)
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="real_rx_packets", state_class=SensorStateClass.TOTAL_INCREASING), #Empfangene Pakete (aktuell)
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="real_tx_drop_packets", state_class=SensorStateClass.TOTAL_INCREASING), #Verlorene (nicht gesendete) Pakete
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="real_rx_drop_packets", state_class=SensorStateClass.TOTAL_INCREASING), #Empfangsverluste (Pakete verworfen)
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="real_tx_error_packets", state_class=SensorStateClass.TOTAL_INCREASING), #Sende-Fehlerpakete
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="real_rx_error_packets", state_class=SensorStateClass.TOTAL_INCREASING), #Empfangs-Fehlerpakete
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="real_tx_speed", conversion_rate=1000000/8, unit=UnitOfInformation.MEGABITS, state_class=SensorStateClass.MEASUREMENT, precision=2), #Aktuelle Uploadrate
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="real_rx_speed", conversion_rate=1000000/8, unit=UnitOfInformation.MEGABITS, state_class=SensorStateClass.MEASUREMENT, precision=2), #Aktuelle Downloadrate
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="real_max_tx_speed", conversion_rate=1000000/8, unit=UnitOfInformation.MEGABITS, precision=2), #Maximale Uploadrate seit Neustart
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="real_max_rx_speed", conversion_rate=1000000/8, unit=UnitOfInformation.MEGABITS, precision=2), #Maximale Downloadrate seit Neustart
        #📅 Monatsdaten
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="month_tx_bytes", conversion_rate=1073741824, unit=UnitOfInformation.GIGABYTES, precision=2), #Upload gesamt im Monat
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="month_rx_bytes", conversion_rate=1073741824, unit=UnitOfInformation.GIGABYTES, precision=2), #Download gesamt im Monat
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="month_tx_packets", state_class=SensorStateClass.TOTAL_INCREASING), #Upload-Pakete im Monat
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="month_rx_packets", state_class=SensorStateClass.TOTAL_INCREASING), #Download-Pakete im Monat
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="month_tx_drop_packets", state_class=SensorStateClass.TOTAL_INCREASING), #Upload-Verluste im Monat
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="month_rx_drop_packets", state_class=SensorStateClass.TOTAL_INCREASING), #Download-Verluste im Monat
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="month_tx_error_packets", state_class=SensorStateClass.TOTAL_INCREASING), #Upload-Fehler im Monat
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="month_rx_error_packets", state_class=SensorStateClass.TOTAL_INCREASING), #Download-Fehler im Monat
        #🧮 Gesamtdaten (Gerätelebensdauer)
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="total_tx_bytes", conversion_rate=1073741824, unit=UnitOfInformation.GIGABYTES, precision=2), #Upload gesamt
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="total_rx_bytes", conversion_rate=1073741824, unit=UnitOfInformation.GIGABYTES, precision=2), #Download gesamt
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="total_tx_packets", state_class=SensorStateClass.TOTAL_INCREASING), #Upload-Pakete gesamt
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="total_rx_packets", state_class=SensorStateClass.TOTAL_INCREASING), #Download-Pakete gesamt
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="total_tx_drop_packets", state_class=SensorStateClass.TOTAL_INCREASING), #Upload-Verluste gesamt
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="total_rx_drop_packets", state_class=SensorStateClass.TOTAL_INCREASING), #Download-Verluste gesamt
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="total_tx_error_packets", state_class=SensorStateClass.TOTAL_INCREASING), #Upload-Fehler gesamt
        HyperboxSensor(coordinator, endpoint_key="network_statistics", data_key="total_rx_error_packets", state_class=SensorStateClass.TOTAL_INCREASING), #Download-Fehler gesamt
    ]

    # Create the sensors.
    async_add_entities(sensors)

class HyperboxSensor(CoordinatorEntity):
    
    _attr_should_poll = False
    _attr_has_entity_name = True
    
    def __init__(self, coordinator: HyperboxCoordinator, endpoint_key: str, data_key: str, unit: str = None, conversion_rate: int = None, icon: str = None, visible: bool = True, category: str = None, state_class: str = None, precision: int = None) -> None:
        super().__init__(coordinator)
        self.device_info = coordinator.device_info
        self.translation_key = endpoint_key + "_" + data_key
        self.entity_registry_enabled_default = visible
        self._attr_unique_id = f"{coordinator.hostname}-{endpoint_key}-{data_key}"
        self._endpoint_key = endpoint_key
        self._data_key = data_key
        self._state_class = state_class
        self._conversion_rate = conversion_rate
        if precision is not None:
            self.suggested_display_precision = precision
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
        attr = {}
        if self._state_class is not None:
            attr['state_class'] = self._state_class
        return attr

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
