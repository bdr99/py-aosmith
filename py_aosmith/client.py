from typing import Any

import aiohttp
import asyncio
import base64
import json
import logging
import urllib.parse

from .exceptions import (
    AOSmithInvalidCredentialsException,
    AOSmithInvalidParametersException,
    AOSmithUnknownException
)
from .models import (
    Device,
    DeviceBasicInfo,
    DeviceStatus,
    DeviceType,
    EnergyUseData,
    EnergyUseHistoryEntry,
    HotWaterStatus,
    SupportedOperationModeInfo,
    OperationMode
)
from .queries import (
    ALL_DEVICE_DATA_GRAPHQL_QUERY,
    DEVICES_BASIC_INFO_GRAPHQL_QUERY,
    DEVICES_GRAPHQL_QUERY,
    ENERGY_USE_DATA_GRAPHQL_QUERY
)

API_BASE_URL = "https://r1.wh8.co"

MAX_RETRIES = 2

TIMEOUT = aiohttp.ClientTimeout(total=20)

def build_passcode(email: str, password: str) -> str:
    data = {'email': email, 'password': password}
    json_string = json.dumps(data)
    url_encoded = urllib.parse.quote(json_string)
    base64_encoded = base64.b64encode(url_encoded.encode()).decode('utf-8')
    return base64_encoded

def device_is_compatible(device_dict: dict[str, Any]) -> bool:
    device_type = device_dict.get("data", {}).get("__typename")
    if device_type is None:
        return False

    return device_type in ["NextGenHeatPump", "RE3Connected"]

def map_mode_str_to_operation_mode_type(mode_str: str) -> OperationMode:
    if mode_str == "HYBRID":
        return OperationMode.HYBRID
    elif mode_str == "HEAT_PUMP":
        return OperationMode.HEAT_PUMP
    elif mode_str == "ELECTRIC":
        return OperationMode.ELECTRIC
    elif mode_str == "VACATION":
        return OperationMode.VACATION
    elif mode_str == "STANDARD":
        return OperationMode.ELECTRIC
    else:
        raise AOSmithUnknownException("Unknown mode")

def map_mode_dict_to_operation_mode(mode_dict: dict[str, Any]) -> SupportedOperationModeInfo:
    mode_str = mode_dict.get("mode")
    if mode_str is None:
        raise AOSmithUnknownException("Failed to determine mode")

    controls_str = mode_dict.get("controls")
    if controls_str == "SELECT_DAYS":
        has_day_selection = True
    elif controls_str is None:
        has_day_selection = False
    else:
        raise AOSmithUnknownException("Unknown controls")

    return SupportedOperationModeInfo(
        mode=map_mode_str_to_operation_mode_type(mode_str),
        original_name=mode_str,
        has_day_selection=has_day_selection
    )

def map_hot_water_status_str_to_hot_water_status(hot_water_status_str: str) -> HotWaterStatus:
    if hot_water_status_str == "LOW":
        return HotWaterStatus.LOW
    elif hot_water_status_str == "MEDIUM":
        return HotWaterStatus.MEDIUM
    elif hot_water_status_str == "HIGH":
        return HotWaterStatus.HIGH
    else:
        raise AOSmithUnknownException("Unknown hot water status")

def map_device_dict_to_device(device_dict: dict[str, Any]) -> Device:
    device_type_str = device_dict.get("data", {}).get("__typename")
    if device_type_str is None:
        raise AOSmithUnknownException("Failed to determine device type")

    if device_type_str == "NextGenHeatPump":
        device_type = DeviceType.NEXT_GEN_HEAT_PUMP
    elif device_type_str == "RE3Connected":
        device_type = DeviceType.RE3_CONNECTED
    else:
        raise AOSmithUnknownException("Unknown device type")

    required_keys = ["brand", "model", "dsn", "junctionId", "name", "serial", "install", "data"]
    if not all(key in device_dict for key in required_keys):
        raise AOSmithUnknownException("Missing required keys")

    required_data_keys = ["temperatureSetpoint", "temperatureSetpointPending", "temperatureSetpointPrevious", "temperatureSetpointMaximum", "modes", "isOnline", "firmwareVersion", "hotWaterStatus", "mode", "modePending"]
    if not all(key in device_dict["data"] for key in required_data_keys):
        raise AOSmithUnknownException("Missing required data keys")

    return Device(
        brand=device_dict["brand"],
        model=device_dict["model"],
        device_type=device_type,
        dsn=device_dict["dsn"],
        junction_id=device_dict["junctionId"],
        name=device_dict["name"],
        serial=device_dict["serial"],
        install_location=device_dict["install"]["location"],
        supported_modes=list(map(map_mode_dict_to_operation_mode, device_dict["data"]["modes"])),
        status=DeviceStatus(
            firmware_version=device_dict["data"]["firmwareVersion"],
            is_online=device_dict["data"]["isOnline"],
            current_mode=map_mode_str_to_operation_mode_type(device_dict["data"]["mode"]),
            mode_change_pending=device_dict["data"]["modePending"],
            temperature_setpoint=device_dict["data"]["temperatureSetpoint"],
            temperature_setpoint_pending=device_dict["data"]["temperatureSetpointPending"],
            temperature_setpoint_previous=device_dict["data"]["temperatureSetpointPrevious"],
            temperature_setpoint_maximum=device_dict["data"]["temperatureSetpointMaximum"],
            hot_water_status=map_hot_water_status_str_to_hot_water_status(device_dict["data"]["hotWaterStatus"])
        )
    )

def map_device_basic_info_dict_to_device_basic_info(device_basic_info_dict: dict[str, Any]) -> DeviceBasicInfo:
    required_keys = ["brand", "model", "deviceType", "dsn", "junctionId", "name", "serial"]
    if not all(key in device_basic_info_dict for key in required_keys):
        raise AOSmithUnknownException("Missing required keys")

    return DeviceBasicInfo(
        brand=device_basic_info_dict["brand"],
        model=device_basic_info_dict["model"],
        device_type=device_basic_info_dict["deviceType"],
        dsn=device_basic_info_dict["dsn"],
        junction_id=device_basic_info_dict["junctionId"],
        name=device_basic_info_dict["name"],
        serial=device_basic_info_dict["serial"]
    )

def map_energy_use_history_entry_dict_to_energy_use_history_entry(energy_use_history_entry_dict: dict[str, Any]) -> EnergyUseHistoryEntry:
    required_keys = ["date", "kwh"]
    if not all(key in energy_use_history_entry_dict for key in required_keys):
        raise AOSmithUnknownException("Missing required keys")

    return EnergyUseHistoryEntry(
        date=energy_use_history_entry_dict["date"],
        energy_use_kwh=energy_use_history_entry_dict["kwh"]
    )

def map_energy_use_data_dict_to_energy_use_data(energy_use_data_dict: dict[str, Any]) -> EnergyUseData:
    required_keys = ["graphData", "lifetimeKwh"]
    if not all(key in energy_use_data_dict for key in required_keys):
        raise AOSmithUnknownException("Missing required keys")

    return EnergyUseData(
        lifetime_kwh=energy_use_data_dict["lifetimeKwh"],
        history=list(map(map_energy_use_history_entry_dict_to_energy_use_history_entry, energy_use_data_dict["graphData"]))
    )

class AOSmithAPIClient:
    token: str = None

    def __init__(self, email: str, password: str, session: aiohttp.ClientSession = None):
        self.email = email
        self.password = password

        if session is None:
            self.session = aiohttp.ClientSession()
        else:
            self.session = session

        self.logger = logging.getLogger(__name__)

    async def __send_graphql_query(
        self,
        query: str,
        variables: dict[str, Any],
        login_required: bool,
        retry_count: int = 0
    ) -> dict[str, Any]:
        if retry_count > MAX_RETRIES:
            raise AOSmithUnknownException("Request failed - max retries exceeded")

        query_log = query.replace('\n', ' ')
        self.logger.debug(f"Sending query, variables: {variables}, login_required: {login_required}, retry_count: {retry_count}, query: {query_log}")

        headers = {}

        if login_required:
            if self.token is None:
                await self.__login()
                if self.token is None:
                    raise AOSmithUnknownException("Login failed")
                self.logger.debug("Successfully logged in")

            headers["Authorization"] = f"Bearer {self.token}"

        try:
            response = await self.session.request(
                method="POST",
                url=API_BASE_URL + "/graphql",
                headers=headers,
                json={
                    "query": query,
                    "variables": variables
                },
                timeout=TIMEOUT
            )
            self.logger.debug(f"Received response, status code: {response.status}")
            self.logger.debug(f"Response body: {await response.text()}")
        except asyncio.TimeoutError:
            raise AOSmithUnknownException("Request timed out")
        except Exception as err:
            self.logger.exception("Request failed", exc_info=err)
            raise AOSmithUnknownException("Request failed")

        if response.status == 401:
            self.logger.debug("Access token may be expired - trying to log in again")
            await self.__login()
            return await self.__send_graphql_query(query, variables, login_required, retry_count=retry_count + 1)
        elif response.status != 200:
            raise AOSmithUnknownException(f"Received status code {response.status}")

        response_json = await response.json()

        if "errors" in response_json:
            errors = response_json.get("errors")
            if any(error.get("extensions", {}).get("code") == "INVALID_CREDENTIALS" for error in errors):
                raise AOSmithInvalidCredentialsException("Invalid email address or password")
            else:
                messages = ", ".join([error.get("message", "") for error in errors])
                raise AOSmithUnknownException("Error: " + messages)

        return response_json

    async def __login(self) -> None:
        passcode = build_passcode(self.email, self.password)

        response = await self.__send_graphql_query(
            "query login($passcode: String) { login(passcode: $passcode) { user { tokens { accessToken idToken refreshToken } } } }",
            {
                "passcode": passcode
            },
            False
        )

        self.token = response.get("data", {}).get("login", {}).get("user", {}).get("tokens", {}).get("accessToken")

    async def is_everything_okay(self) -> bool:
        response = await self.__send_graphql_query("{ status { isEverythingOkay } }", {}, False)

        return response["data"]["status"]["isEverythingOkay"]

    async def get_devices(self) -> list[Device]:
        response = await self.__send_graphql_query(DEVICES_GRAPHQL_QUERY, { "forceUpdate": True }, True)

        device_dicts: list[dict[str, Any]] | None = response.get("data", {}).get("devices")
        if device_dicts is None:
            raise AOSmithUnknownException("Failed to retrieve devices")

        compatible_device_dicts = list(filter(device_is_compatible, device_dicts))

        return list(map(map_device_dict_to_device, compatible_device_dicts))

    async def __get_device_by_junction_id(self, junction_id: str) -> Device:
        devices = await self.get_devices()

        device = next(filter(lambda device: device.junction_id == junction_id, devices), None)
        if device is None:
            raise AOSmithUnknownException("Device not found")

        return device

    async def __get_device_basic_info_by_junction_id(self, junction_id: str) -> DeviceBasicInfo:
        response = await self.__send_graphql_query(DEVICES_BASIC_INFO_GRAPHQL_QUERY, { "forceUpdate": True }, True)

        device_basic_info_dicts = response.get("data", {}).get("devices", None)
        if device_basic_info_dicts is None:
            raise AOSmithUnknownException("Failed to retrieve devices")

        device_basic_infos = list(map(map_device_basic_info_dict_to_device_basic_info, device_basic_info_dicts))

        device_basic_info = next(filter(lambda device_basic_info: device_basic_info.junction_id == junction_id, device_basic_infos), None)
        if device_basic_info is None:
            raise AOSmithUnknownException("Device not found")

        return device_basic_info

    async def update_setpoint(self, junction_id: str, setpoint: int):
        if setpoint < 95:
            raise AOSmithInvalidParametersException("Setpoint is below the minimum")

        device = await self.__get_device_by_junction_id(junction_id)

        if setpoint > device.status.temperature_setpoint_maximum:
            raise AOSmithInvalidParametersException("Setpoint is above the maximum")

        response = await self.__send_graphql_query(
            "mutation updateSetpoint($junctionId: String!, $value: Int!) { updateSetpoint(junctionId: $junctionId, value: $value) }",
            {
                "junctionId": junction_id,
                "value": setpoint
            },
            True
        )

        if response.get("data", {}).get("updateSetpoint") is not True:
            raise AOSmithUnknownException("Failed to update setpoint")

    async def __get_energy_use_data_by_dsn(self, dsn: str, device_type: str) -> EnergyUseData:
        response = await self.__send_graphql_query(
            ENERGY_USE_DATA_GRAPHQL_QUERY,
            {
                "dsn": dsn,
                "deviceType": device_type
            },
            True
        )

        energy_use_data_dict = response.get("data", {}).get("getEnergyUseData")
        if energy_use_data_dict is None:
            raise AOSmithUnknownException("Failed to retrieve energy use data")

        return map_energy_use_data_dict_to_energy_use_data(energy_use_data_dict)

    async def get_energy_use_data(self, junction_id: str) -> EnergyUseData:
        device_basic_info = await self.__get_device_basic_info_by_junction_id(junction_id)
        return await self.__get_energy_use_data_by_dsn(device_basic_info.dsn, device_basic_info.device_type)

    async def update_mode(self, junction_id: str, mode: OperationMode, days: int | None = None) -> None:
        device = await self.__get_device_by_junction_id(junction_id)

        # check if mode is supported
        desired_mode = next(filter(lambda device_mode: device_mode.mode == mode, device.supported_modes), None)
        if desired_mode is None:
            raise AOSmithInvalidParametersException("Mode not supported by this device")

        if desired_mode.has_day_selection:
            if days is None:
                days = 100
            elif days <= 0 or days > 100:
                raise AOSmithInvalidParametersException("Invalid days selection")
        elif days is not None:
            raise AOSmithInvalidParametersException("Days not supported for this operation mode")

        mode_payload = { "mode": desired_mode.original_name }
        if desired_mode.has_day_selection:
            mode_payload["days"] = days

        response = await self.__send_graphql_query(
            "mutation updateMode($junctionId: String!, $mode: ModeInput!) { updateMode(junctionId: $junctionId, mode: $mode) }",
            {
                "junctionId": junction_id,
                "mode": mode_payload
            },
            True
        )

        if response.get("data", {}).get("updateMode") is not True:
            raise AOSmithUnknownException("Failed to update mode")

    async def get_all_device_info(self) -> dict[str, Any]:
        all_device_data_response = await self.__send_graphql_query(ALL_DEVICE_DATA_GRAPHQL_QUERY, { "forceUpdate": True }, True)
        all_device_data = all_device_data_response.get("data", {}).get("devices", [])

        energy_use_data_by_junction_id = {}
        for device in all_device_data:
            try:
                response = await self.__send_graphql_query(
                    ENERGY_USE_DATA_GRAPHQL_QUERY,
                    {
                        "dsn": device["dsn"],
                        "deviceType": device["deviceType"]
                    },
                    True
                )

                energy_use_data_by_junction_id[device["junctionId"]] = response.get("data", {}).get("getEnergyUseData")
            except Exception as err:
                self.logger.exception("Failed to get energy use data", exc_info=err)

        return {
            "devices": all_device_data,
            "energy_use_data": energy_use_data_by_junction_id
        }

    async def close(self):
        await self.session.close()
