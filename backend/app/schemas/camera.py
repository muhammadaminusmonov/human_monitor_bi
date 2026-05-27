from pydantic import BaseModel, ConfigDict
from typing import Optional
import datetime
class CameraBase(BaseModel):
    street_id: int
    location_id: int
    status: Optional[str] = "Active"
    model_info: Optional[str] = None

class CameraCreate(CameraBase):
    pass

class CameraResponse(CameraBase):
    camera_id: int

    model_config = ConfigDict(from_attributes=True)

    

