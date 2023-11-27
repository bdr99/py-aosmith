import aiohttp
import base64
import json
import urllib.parse

from .exceptions import (
    AOSmithInvalidCredentialsException,
    AOSmithInvalidParametersException,
    AOSmithUnknownException
)

API_BASE_URL = "https://r2.wh8.co"

DEVICES_GRAPHQL_QUERY = """
query devices($forceUpdate: Boolean, $junctionIds: [String]) {
    devices(forceUpdate: $forceUpdate, junctionIds: $junctionIds) {
        brand
        model
        deviceType
        dsn
        junctionId
        name
        serial
        install {
            location
        }
        data {
            __typename
            temperatureSetpoint
            temperatureSetpointPending
            temperatureSetpointPrevious
            temperatureSetpointMaximum
            modes {
                mode
                controls
            }
            isOnline
            ... on NextGenHeatPump {
                firmwareVersion
                hotWaterStatus
                mode
                modePending
                vacationModeRemainingDays
                electricModeRemainingDays
            }
        }
    }
}
"""

MAX_RETRIES = 2

def build_passcode(email, password):
    data = {'email': email, 'password': password}
    json_string = json.dumps(data)
    url_encoded = urllib.parse.quote(json_string)
    base64_encoded = base64.b64encode(url_encoded.encode()).decode('utf-8')
    return base64_encoded

class AOSmithAPIClient:
    token: str = None

    def __init__(self, email: str, password: str, session: aiohttp.ClientSession = None):
        self.email = email
        self.password = password

        if session is None:
            self.session = aiohttp.ClientSession()
        else:
            self.session = session

    async def __send_graphql_query(self, query: str, variables: dict, login_required: bool, retry_count: int = 0):
        if retry_count > MAX_RETRIES:
            raise AOSmithUnknownException("Request failed - max retries exceeded")

        headers = {}

        if login_required:
            if self.token is None:
                await self.__login()
                if self.token is None:
                    raise AOSmithUnknownException("Login failed")

            headers["Authorization"] = f"Bearer {self.token}"

        response = await self.session.request(
            method="POST",
            url=API_BASE_URL + "/graphql",
            headers=headers,
            json={
                "query": query,
                "variables": variables
            }
        )

        if response.status == 401:
            # Access token may be expired - try to log in again
            print(401)
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

    async def __login(self):
        passcode = build_passcode(self.email, self.password)

        response = await self.__send_graphql_query(
            "query login($passcode: String) { login(passcode: $passcode) { user { tokens { accessToken idToken refreshToken } } } }",
            {
                "passcode": passcode
            },
            False
        )

        self.token = response.get("data", {}).get("login", {}).get("user", {}).get("tokens", {}).get("accessToken")

    async def is_everything_okay(self):
        response = await self.__send_graphql_query("{ status { isEverythingOkay } }", {}, False)

        return response.get("data", {}).get("status", {}).get("isEverythingOkay")

    async def get_devices(self):
        response = await self.__send_graphql_query(DEVICES_GRAPHQL_QUERY, { "forceUpdate": True }, True)

        devices = response.get("data", {}).get("devices", None)
        if devices is None:
            raise AOSmithUnknownException("Failed to retrieve devices")

        next_gen_heat_pump_devices = list(filter(lambda device: device.get("data", {}).get("__typename") == "NextGenHeatPump", devices))

        return next_gen_heat_pump_devices

    async def __get_device_by_junction_id(self, junction_id: str):
        devices = await self.get_devices()

        device = next(filter(lambda device: device.get("junctionId") == junction_id, devices), None)
        if device is None:
            raise AOSmithUnknownException("Device not found")

        return device

    async def update_setpoint(self, junction_id: str, setpoint: int):
        if setpoint < 95:
            raise AOSmithInvalidParametersException("Setpoint is below the minimum")

        device = await self.__get_device_by_junction_id(junction_id)

        setpoint_maximum = device.get("data", {}).get("temperatureSetpointMaximum")
        if setpoint_maximum is None:
            raise AOSmithUnknownException("Failed to determine maximum setpoint")

        if setpoint > setpoint_maximum:
            raise AOSmithInvalidParametersException("Setpoint is above the maximum")

        response = await self.__send_graphql_query(
            "mutation updateSetpoint($junctionId: String!, $value: Int!) { updateSetpoint(junctionId: $junctionId, value: $value) }",
            {
                "junctionId": junction_id,
                "value": setpoint
            },
            True
        )

        if response.get("data", {}).get("updateSetpoint") != True:
            raise AOSmithUnknownException("Failed to update setpoint")

    async def __get_energy_use_data_by_dsn(self, dsn: str, device_type: str):
        response = await self.__send_graphql_query(
            "query getEnergyUseData($dsn: String!, $deviceType: DeviceType!) { getEnergyUseData(dsn: $dsn, deviceType: $deviceType) { average graphData { date kwh } lifetimeKwh startDate } }",
            {
                "dsn": dsn,
                "deviceType": device_type
            },
            True
        )

        return response.get("data", {}).get("getEnergyUseData")

    async def get_energy_use_data(self, junction_id: str):
        device = await self.__get_device_by_junction_id(junction_id)
        return await self.get_energy_use_data(device.get("dsn"), device.get("deviceType"))

    async def update_mode(self, junction_id: str, mode: str, days: int | None = None):
        device = await self.__get_device_by_junction_id(junction_id)

        device_modes = device.get("data", {}).get("modes", [])
        desired_mode = next(filter(lambda device_mode: device_mode.get("mode") == mode, device_modes), None)
        if desired_mode is None:
            raise AOSmithInvalidParametersException("Invalid mode for this device")

        days_required = desired_mode.get("controls") == "SELECT_DAYS"
        if days_required:
            if days is None:
                days = 100
            elif days <= 0 or days > 100:
                raise AOSmithInvalidParametersException("Invalid days selection")
        elif days is not None:
            raise AOSmithInvalidParametersException("Days not supported for this operation mode")

        response = await self.__send_graphql_query(
            "mutation updateMode($junctionId: String!, $mode: ModeInput!) { updateMode(junctionId: $junctionId, mode: $mode) }",
            {
                "junctionId": junction_id,
                "mode": { "mode": mode, "days": days } if days_required else { "mode": mode }
            },
            True
        )

        if response.get("data", {}).get("updateMode") != True:
            raise AOSmithUnknownException("Failed to update mode")

    async def close(self):
        await self.session.close()
