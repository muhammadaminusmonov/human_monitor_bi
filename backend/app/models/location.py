from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Location(Base):
    __tablename__ = "locations"

    location_id = Column(Integer, primary_key=True, index=True)

    street_id = Column(
        Integer,
        ForeignKey("streets.street_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    name = Column(
        String(150),
        nullable=False,
        unique=True,
        index=True
    )

    description = Column(String(500), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    street = relationship(
        "Street",
        back_populates="locations"
    )

    cameras = relationship(
        "Camera",
        back_populates="location"
    )