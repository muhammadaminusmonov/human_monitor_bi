from pydantic import BaseModel, ConfigDict
from datetime import datetime

class CrowdTelemetryBase(BaseModel):
    camera_id: int
    person_count: int
    crowd_density_score: float

class CrowdTelemetryCreate(CrowdTelemetryBase):
    pass

class CrowdTelemetryResponse(CrowdTelemetryBase):
    telemetry_id: int
    timestamp: datetime

    # В Pydantic v2 это заменяет старый class Config: orm_mode = True
    model_config = ConfigDict(from_attributes=True)