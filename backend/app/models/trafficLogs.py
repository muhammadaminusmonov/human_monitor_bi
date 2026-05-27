from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Enum,
    Float,

)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.models.base import Base
from app.models.enums import CameraStatus


class TrafficLog(Base):
    __tablename__ = "traffic_logs"
 
    logs_id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.camera_id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    cars_count = Column(Integer, nullable=False, default=0)
 
    camera = relationship("Camera", back_populates="traffic_logs")