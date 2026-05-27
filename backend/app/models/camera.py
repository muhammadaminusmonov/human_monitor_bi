from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Enum,
    Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base
from app.models.enums import CameraStatus



class Camera(Base):
    __tablename__ = "cameras"

    camera_id = Column(Integer, primary_key=True, index=True)
    location_id = Column(
        Integer,
        ForeignKey("locations.location_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    camera_name = Column(String(150), nullable=False, unique=True)
    ip_address = Column(String(100), nullable=True)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    model_info = Column(String(250), nullable=True)

    firmware_version = Column(String(100), nullable=True)

    status = Column(
        Enum(CameraStatus),
        default=CameraStatus.ACTIVE,
        nullable=False
    )


    video_url = Column(String(500), nullable=True)

    video_file = Column(String(500), nullable=True)

    ai_model_version = Column(String(100), nullable=True)

    installed_at = Column(DateTime(timezone=True), server_default=func.now())

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    location = relationship("Location", back_populates="cameras")
    traffic_logs = relationship("TrafficLog", back_populates="camera")