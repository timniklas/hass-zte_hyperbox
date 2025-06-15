from enum import StrEnum
import logging
from random import choice, randrange

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from aiohttp import ClientError, ClientResponseError, ClientSession, BasicAuth
from homeassistant.core import HomeAssistant

import json
import hashlib
from datetime import datetime, timedelta, timezone
from pygsm7 import encodeMessage, decodeMessage

_LOGGER = logging.getLogger(__name__)

class API:
    def __init__(self, hass: HomeAssistant, hostname: str) -> None:
        """Initialise."""
        self._url = "http://" + hostname + "/"
        self._session = async_get_clientsession(hass)
        self._req_id = 0
        self._ubus_rpc_session = "00000000000000000000000000000000"
        self.connected: bool = False

    async def sendRequest(self, endpoint, method, params = {}):
        payload = [
            {
                "jsonrpc": "2.0",
                "id": self._req_id,
                "method": "call",
                "params": [
                    self._ubus_rpc_session,
                    endpoint,
                    method,
                    params
                ]
            }
        ]
        response = await self._session.post(self._url + "ubus/", data=json.dumps(payload), headers={
            'content-type': 'application/json',
            "Referer": self._url
        })
        self._req_id += 1
        response_json = (await response.json())[0]
        if "error" in response_json:
            raise APIAuthError(response_json['error']['message'])
        result = response_json['result']
        if result[0] == 0:
            return response_json['result'][1]
        raise APIConnectionError("invalid jsonrpc response status: " + str(result[0]))

    async def _getLoginSalt(self):
        return (await self.sendRequest("zwrt_web", "web_login_info"))['zte_web_sault']

    def _hash(self, str):
        hashed = hashlib.sha256(str.encode()).hexdigest()
        return hashed

    async def login(self, password):
        salt = await self._getLoginSalt()
        hashPassword = self._hash(password).upper()
        ztePass = self._hash(hashPassword + salt).upper()
        response = await self.sendRequest("zwrt_web", "web_login",{
            "password": ztePass
        })
        if response['result'] != 0:
            raise APIAuthError(response['msg'])
        self._ubus_rpc_session = response['ubus_rpc_session']
        self.connected = True

    async def getWANStatistics(self):
        return await self.sendRequest("zwrt_data", "get_wwandst", {
            "source_module": "web",
            "cid": 1,
            "type": 4
        })
    
    async def getNetworkInfo(self):
        return await self.sendRequest("zte_nwinfo_api", "nwinfo_get_netinfo")

    def _format_date(self, str):
        parts = str.split(",")
        tz = timezone(timedelta(hours=int(parts[6][1:])))
        return datetime(int(parts[0]) + 2000, int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5]), tzinfo=tz)
    
    def _current_date_string(self):
        now = datetime.now().astimezone()
        custom_format = now.strftime('%y;%m;%d;%H;%M;%S')
        tz_offset = int(now.utcoffset().total_seconds() / 3600)
        return f"{custom_format};{tz_offset:+d}"

    async def getSMSMessages(self):
        response = await self.sendRequest("zwrt_wms", "zte_libwms_get_sms_data", {
            "page": 0,
            "data_per_page": 500,
            "mem_store": 1,
            "tags": 10,
            "order_by": "order by id desc"
        })
        for message in response['messages']:
            message['content'] = decodeMessage(message['content'])
            message['date'] = self._format_date(message['date']).timestamp()
        return response['messages']
    
    async def sendSMSMessage(self, address, message):
        await self.sendRequest("zwrt_wms", "zte_libwms_send_sms", {
            "number": address,
            "sms_time": self._current_date_string(),
            "message_body": encodeMessage(message),
            "id": "-1",
            "encode_type": "GSM7_default"
        })
    
    async def reboot(self):
        await self.sendRequest("zwrt_mc.device.manager", "device_reboot", {
            "moduleName":"web"
        })

class APIAuthError(Exception):
    """Exception class for auth error."""


class APIConnectionError(Exception):
    """Exception class for connection error."""
