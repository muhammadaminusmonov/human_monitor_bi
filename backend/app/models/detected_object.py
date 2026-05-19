from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base
from app.models.enums import DetectionType


class DetectedObject(Base):
    __tablename__ = "detected_objects"

    detected_object_id = Column(Integer, primary_key=True, index=True)

    camera_id = Column(
        Integer,
        ForeignKey("cameras.camera_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    object_type = Column(
        Enum(DetectionType),
        nullable=False,
        index=True
    )

    confidence_score = Column(Float, nullable=False)

    bbox_x = Column(Float, nullable=True)
    bbox_y = Column(Float, nullable=True)
    bbox_width = Column(Float, nullable=True)
    bbox_height = Column(Float, nullable=True)

    tracking_id = Column(String(100), nullable=True, index=True)

    frame_number = Column(Integer, nullable=True)

    image_path = Column(String(500), nullable=True)
    video_path = Column(String(500), nullable=True)

    camera = relationship("Camera", back_populates="detected_objects")