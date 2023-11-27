# py-aosmith

This is an API Client for A. O. Smith iCOMM-enabled water heaters. If you can control your
water heater using the A. O. Smith mobile app ([iOS](https://apps.apple.com/us/app/a-o-smith/id456489822)/[Android](https://play.google.com/store/apps/details?id=com.aosmith.warrantycheck)), then it should be compatible with this library.

# Known Compatible Models

- [HPTS-50](https://www.hotwater.com/products/HPTS-50-SG200.html)
- [HPTS-66](https://www.hotwater.com/products/HPTS-66-SG200.html)
- [HPTS-80](https://www.hotwater.com/products/HPTS-80-SG200.html)

If your water heater is not working with this library, but it can be controlled using the A. O. Smith mobile app, please [open an issue](https://github.com/bdr99/py-aosmith/issues/new) so that support can be added.

Similarly, if your water heater is working with this library, but is not listed here, please [open an issue](https://github.com/bdr99/py-aosmith/issues/new) so it can be added to the list.

# Installation

To install the latest release from [PyPI](https://pypi.org/project/py-aosmith/), run `pip3 install py-aosmith`.

# Quick Start

You will need a compatible water heater which is already connected to Wi-Fi and linked to your A. O. Smith account.

This example initializes the API client and gets a list of water heaters linked to the account. Then, for each water heater, it updates the setpoint to 120 degrees.

```python
from py_aosmith import AOSmithAPIClient

# Initialize API client
client = AOSmithAPIClient("myemail@example.com", "mypassword")

# Get list of water heaters linked to the account
devices = await client.get_devices()

# Loop through the registered water heaters
for device in devices:
    # Update the setpoint to 120 degrees
    await client.update_setpoint(device.get("junctionId"), 120);
```

# API Documentation

## Initialize API Client

```typescript
AOSmithAPIClient(email, password)
```

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `email`   | The email address for your A. O. Smith account |
| `password` | The password for your A. O. Smith account |

### Return value

Returns an instance of `AOSmithAPIClient` which can be used to invoke the below methods.

## Get List of Devices

```typescript
await client.get_devices()
```

Gets a list of water heaters linked with the A. O. Smith account. May only include devices which are known to be compatible with this library.

If your water heater can be controlled in the A. O. Smith mobile app, but is not included in the return value of this method, please [open an issue](https://github.com/bdr99/py-aosmith/issues/new) so that support can be added.

### Parameters

None

### Return value

```jsonc
[
    {
        "brand": "aosmith",
        "model": "HPTS-50 200 202172000",
        "deviceType": "NEXT_GEN_HEAT_PUMP",
        "dsn": "xxxxxxxxxxxxxxx",
        "junctionId": "xxxxxxxxxxxxxxxxxx", // Unique ID needed to call the other API methods
        "name": "Water Heater", // Custom nickname assigned in the mobile app
        "serial": "xxxxxxxxxxxxx",
        "install": {
            "location": "Basement" // Install location set in the mobile app
        },
        "data": {
            "__typename": "NextGenHeatPump",
            "temperatureSetpoint": 130, // Current setpoint (target water temperature)
            "temperatureSetpointPending": false,
            "temperatureSetpointPrevious": 130,
            "temperatureSetpointMaximum": 130, // Max possible setpoint - to increase this, manually adjust the setpoint using the buttons on the water heater
            "modes": [ // Available operation modes
                {
                    "mode": "HYBRID",
                    "controls": null
                },
                {
                    "mode": "HEAT_PUMP",
                    "controls": null
                },
                {
                    "mode": "ELECTRIC",
                    "controls": "SELECT_DAYS"
                },
                {
                    "mode": "VACATION",
                    "controls": "SELECT_DAYS"
                }
            ],
            "isOnline": true,
            "firmwareVersion": "2.14",
            "hotWaterStatus": "LOW", // Current hot water availability ("LOW", "MEDIUM", or "HIGH")
            "mode": "HEAT_PUMP", // Current operation mode
            "modePending": false,
            "vacationModeRemainingDays": 0,
            "electricModeRemainingDays": 0
        }
    }
]
```

## Update setpoint

```typescript
await client.update_setpoint(junction_id, setpoint)
```

Updates the setpoint (target water temperature) of the water heater.

When using this method, the setpoint cannot be adjusted above the `temperatureSetpointMaximum` from the return value of `get_devices()`. To increase this maximum, manually adjust the setpoint using the buttons on the water heater.

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `junction_id` | Unique ID of the water heater, obtained from `get_devices()` |
| `setpoint` | New target temperature to set |

### Return value

None

## Update mode

```typescript
await client.updateMode(junction_id, mode, days)
```

Sets the operation mode of the water heater. To determine the list of modes supported by your water heater, check `data.modes[]` in the return value of `get_devices()`.

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `junction_id` | Unique ID of the water heater, obtained from `get_devices()` |
| `mode` | New operation mode to set |
| `days` | Optional. Number of days after which the device will automatically exit this mode. Only works for modes where `data.modes[].controls` from `get_devices()` is `"SELECT_DAYS"`.

### Return value

None

## Get energy use data

```typescript
await client.get_energy_use_data(junction_id)
```

Gets energy use history data from the water heater.

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `junction_id` | Unique ID of the water heater, obtained from `get_devices()` |

### Return value

```jsonc
{
    "average": 2.7552000000000003,
    "graphData": [
        {
            "date": "2023-10-30T04:00:00.000Z",
            "kwh": 2.01
        },
        {
            "date": "2023-10-31T04:00:00.000Z",
            "kwh": 1.542
        },
        {
            "date": "2023-11-01T04:00:00.000Z",
            "kwh": 1.908
        },
        /* ... */
    ],
    "lifetimeKwh": 132.825,
    "startDate": "Oct 30"
}
```

# Disclaimer

This project is not affiliated with or endorsed by A. O. Smith. This is not an official API, and it may stop working at any time without warning.