from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow

from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD
)

from .const import DOMAIN
from .api import API

class HyperboxConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, formdata):
        if formdata is not None:
            hostname = formdata[CONF_HOST]
            password = formdata[CONF_PASSWORD]

            try:
                api = API(self.hass, hostname=hostname)
                await api.login(password=password)
                await self.async_set_unique_id(deviceid, raise_on_progress=False)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=f"ZTE Hyperbox {hostname}", data={
                    CONF_HOST: hostname,
                    CONF_PASSWORD: password,
                })
            except APIAuthError as err:
                return self.async_abort(reason="authentication")
            except APIConnectionError as err:
                return self.async_abort(reason="connenction")
        
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PASSWORD): str
            })
        )
