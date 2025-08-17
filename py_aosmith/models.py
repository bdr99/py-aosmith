from dataclasses import dataclass
from enum import Enum

class DeviceType(Enum):
    NEXT_GEN_HEAT_PUMP = "next_gen_heat_pump"
    RE3_CONNECTED = "re3_connected"
    RE3_PREMIUM = "re3_premium"

class OperationMode(Enum):
    ELECTRIC = "electric"
    GUEST = "guest"
    HEAT_PUMP = "heat_pump"
    HYBRID = "hybrid"
    VACATION = "vacation"

@dataclass(frozen=True)
class SupportedOperationModeInfo:
    mode: OperationMode
    original_name: str
    has_day_selection: bool
    supports_hot_water_plus: bool

@dataclass(frozen=True)
class DeviceStatus:
    firmware_version: str
    is_online: bool
    current_mode: OperationMode
    mode_change_pending: bool
    temperature_setpoint: int
    temperature_setpoint_pending: bool
    temperature_setpoint_previous: int
    temperature_setpoint_maximum: int
    hot_water_status: int | None
    hot_water_plus_level: int | None

@dataclass(frozen=True)
class Device:
    brand: str
    model: str
    device_type: DeviceType
    dsn: str
    junction_id: str
    name: str
    serial: str
    install_location: str
    supported_modes: list[SupportedOperationModeInfo]
    supports_hot_water_plus: bool
    status: DeviceStatus

@dataclass(frozen=True)
class DeviceBasicInfo:
    brand: str
    model: str
    device_type: str
    dsn: str
    junction_id: str
    name: str
    serial: str

@dataclass(frozen=True)
class EnergyUseHistoryEntry:
    date: str
    energy_use_kwh: float

@dataclass(frozen=True)
class EnergyUseData:
    lifetime_kwh: float
    history: list[EnergyUseHistoryEntry]