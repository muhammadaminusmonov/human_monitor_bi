from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AlertCreate(BaseModel):
    camera_id: int
    anomaly_type: str
    severity: str

class AlertUpdateStatus(BaseModel):
    status: str  

class AlertResponse(BaseSchema):
    alert_id: int
    camera_id: int
    timestamp: datetime
    anomaly_type: str
    severity: str
    status: str
