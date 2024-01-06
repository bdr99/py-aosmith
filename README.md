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
from py_aosmith.models import OperationMode

# Initialize API client
client = AOSmithAPIClient("myemail@example.com", "mypassword")

# Get list of water heaters linked to the account
devices = await client.get_devices()

# Loop through the registered water heaters
for device in devices:
    # Update the setpoint to 120 degrees
    await client.update_setpoint(device.junction_id, 120);

    # Set the operation mode to heat pump
    await client.update_mode(device.junction_id, OperationMode.HEAT_PUMP)
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

```python
[
    Device(
        brand='aosmith',
        model='HPTS-50 200 202172000',
        device_type=DeviceType.NEXT_GEN_HEAT_PUMP,
        dsn='xxxxxxxxxxxxxxx',
        junction_id='xxxxxxxxxxxxxxxxxx', # Unique ID needed to call the other API methods
        name='Water Heater', # Custom nickname assigned to your water heater in the mobile app
        serial='xxxxxxxxxxxxx',
        install_location='Basement', # Install location set in the mobile app
        supported_modes=[ # Available operation modes for your water heater
            SupportedOperationModeInfo(
                mode=OperationMode.HYBRID, # Enum value of the mode (use this when calling update_mode)
                original_name='HYBRID',    # Original name of the mode as returned by the API
                has_day_selection=False    # Whether the mode supports day selection
            ),
            SupportedOperationModeInfo(
                mode=OperationMode.HEAT_PUMP,
                original_name='HEAT_PUMP',
                has_day_selection=False
            ),
            SupportedOperationModeInfo(
                mode=OperationMode.ELECTRIC,
                original_name='ELECTRIC',
                has_day_selection=True
            ),
            SupportedOperationModeInfo(
                mode=OperationMode.VACATION,
                original_name='VACATION',
                has_day_selection=True
            )
        ],
        status=DeviceStatus(
            firmware_version='2.14', # Current installed firmware version
            is_online=True, # Whether the water heater is currently connected to the internet
            current_mode=OperationMode.HEAT_PUMP, # Current operation mode
            mode_change_pending=False, # Whether a mode change is currently in progress
            temperature_setpoint=145, # Current setpoint (target water temperature)
            temperature_setpoint_pending=False, # Whether a setpoint change is currently in progress
            temperature_setpoint_previous=145, # Previous setpoint
            temperature_setpoint_maximum=145, # Maximum setpoint (to increase this, manually adjust the setpoint using the buttons on the water heater)
            hot_water_status=HotWaterStatus.HIGH # Current hot water availability (low, medium, high)
        )
    )
]
```

## Update setpoint

```typescript
await client.update_setpoint(junction_id, setpoint)
```

Updates the setpoint (target water temperature) of the water heater.

When using this method, the setpoint cannot be adjusted above the `temperature_setpoint_maximum` from the return value of `get_devices()`. To increase the maximum, manually adjust the setpoint using the buttons on the water heater.

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `junction_id` | Unique ID of the water heater, obtained from `get_devices()` |
| `setpoint` | New target temperature to set |

### Return value

None

## Update mode

```typescript
await client.update_mode(junction_id, mode, days)
```

Sets the operation mode of the water heater. To determine the list of modes supported by your water heater, check `supported_modes` in the `Device` object returned by `get_devices()`.

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `junction_id` | Unique ID of the water heater, obtained from `get_devices()` |
| `mode` | New operation mode to set. Must be a member of the `OperationMode` enum and must be a supported mode from `supported_modes`. |
| `days` | Optional. Number of days after which the device will automatically exit this mode. Only works for modes where `has_day_selection` from `supported_modes` is `True`. |

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

```python
EnergyUseData(
    lifetime_kwh=234.309,
    history=[
        EnergyUseHistoryEntry(
            date='2023-12-09T04:00:00.000Z',
            energy_use_kwh=2.19
        ),
        EnergyUseHistoryEntry(
            date='2023-12-10T04:00:00.000Z',
            energy_use_kwh=3.786
        ),
        EnergyUseHistoryEntry(
            date='2023-12-11T04:00:00.000Z',
            energy_use_kwh=5.292
        ),
        # ...
    ]
)
```

# Disclaimer

This project is not affiliated with or endorsed by A. O. Smith. This is not an official API, and it may stop working at any time without warning.