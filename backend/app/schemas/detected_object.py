from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    
class DetectedObjectCreate(BaseModel):
    camera_id: int
    object_type: str
    confidence_score: float

class DetectedObjectResponse(BaseSchema):
    detected_object_id: int
    camera_id: int
    timestamp: datetime
    object_type: str
    confidence_score: float