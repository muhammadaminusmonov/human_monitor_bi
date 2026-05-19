from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base
from app.models.enums import AlertSeverity, AlertStatus


class AnomaliesAndAlert(Base):
    __tablename__ = "anomalies_and_alerts"

    alert_id = Column(Integer, primary_key=True, index=True)

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

    anomaly_type = Column(String(150), nullable=False, index=True)

    severity = Column(
        Enum(AlertSeverity),
        nullable=False,
        default=AlertSeverity.LOW
    )

    status = Column(
        Enum(AlertStatus),
        nullable=False,
        default=AlertStatus.ACTIVE
    )

    description = Column(String(1000), nullable=True)

    resolved_at = Column(DateTime(timezone=True), nullable=True)

    resolution_notes = Column(String(1000), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    camera = relationship("Camera", back_populates="alerts")