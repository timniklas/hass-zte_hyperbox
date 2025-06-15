from dataclasses import dataclass
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import API, APIAuthError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class HyperboxAPIData:
    """Class to hold api data."""

    networkStatistics: dict[str, any]
    networkInfo: dict[str, any]
    smsMessages: list[any]


class HyperboxCoordinator(DataUpdateCoordinator):
    """My coordinator."""

    data: HyperboxAPIData

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize coordinator."""

        # Set variables from values entered in config flow setup
        self._hostname = config_entry.data[CONF_HOST]
        self._password = config_entry.data[CONF_PASSWORD]

        # Initialise DataUpdateCoordinator
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            # Method to call on every update interval.
            update_method=self.async_update_data,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=60),
        )

        # Initialise your api here
        self.api = API(hass, hostname=self._hostname)

    async def async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            await self.api.login(password=self._password)
            networkStatistics = await self.api.getWANStatistics()
            networkInfo = await self.api.getNetworkInfo()
            smsMessages = await self.api.getSMSMessages()
            return HyperboxAPIData(
                networkStatistics=networkStatistics,
                networkInfo=networkInfo,
                smsMessages=smsMessages
            )
        except Exception as err:
            _LOGGER.error(err)
            # This will show entities as unavailable by raising UpdateFailed exception
            raise UpdateFailed(f"Error communicating with API: {err}") from err
