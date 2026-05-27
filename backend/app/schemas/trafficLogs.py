from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class TrafficLogBase(BaseModel):
    camera_id: int
    cars_count: int
 
 
class TrafficLogCreate(TrafficLogBase):
    timestamp: Optional[datetime] = None
 
 
class TrafficLogUpdate(BaseModel):
    cars_count: Optional[int] = None
    timestamp: Optional[datetime] = None
 
 
class TrafficLogRead(TrafficLogBase):
    model_config = ConfigDict(from_attributes=True)
 
    logs_id: int
    timestamp: datetime
 