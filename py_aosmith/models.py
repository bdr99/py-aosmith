from dataclasses import dataclass
from enum import Enum

class DeviceType(Enum):
    RE3_CONNECTED = "re3_connected"
    NEXT_GEN_HEAT_PUMP = "next_gen_heat_pump"

class HotWaterStatus(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class OperationMode(Enum):
    HYBRID = "hybrid"
    HEAT_PUMP = "heat_pump"
    ELECTRIC = "electric"
    VACATION = "vacation"

@dataclass(frozen=True)
class SupportedOperationModeInfo:
    mode: OperationMode
    original_name: str
    has_day_selection: bool

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
    hot_water_status: HotWaterStatus

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