from app.schemas.camera import CameraCreate, CameraResponse
from app.schemas.crowd_telemetry import CrowdTelemetryCreate, CrowdTelemetryResponse
# Добавь сюда остальные схемы по мере их написания (City, Street, ChatBot и т.д.)

__all__ = [
    "CameraCreate",
    "CameraResponse",
    "CrowdTelemetryCreate",
    "CrowdTelemetryResponse",
]