# models/enums.py
import enum


class CameraStatus(enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    MAINTENANCE = "Maintenance"


class AlertSeverity(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class AlertStatus(enum.Enum):
    ACTIVE = "Active"
    INVESTIGATING = "Investigating"
    RESOLVED = "Resolved"


class DetectionType(enum.Enum):
    PERSON = "person"
    CAR = "car"
    BICYCLE = "bicycle"
    BACKPACK = "backpack"
    MOTORBIKE = "motorbike"
    UNKNOWN = "unknown"