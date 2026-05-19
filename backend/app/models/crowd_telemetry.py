from sqlalchemy import (
    Column,
    Integer,
    Float,
    ForeignKey,
    DateTime
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class CrowdTelemetry(Base):
    __tablename__ = "crowd_telemetry"

    telemetry_id = Column(Integer, primary_key=True, index=True)

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

    person_count = Column(Integer, default=0, nullable=False)

    crowd_density_score = Column(Float, default=0.0, nullable=False)

    average_movement_speed = Column(Float, nullable=True)

    anomaly_probability = Column(Float, nullable=True)

    camera = relationship("Camera", back_populates="telemetries")