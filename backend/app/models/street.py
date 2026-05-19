from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Street(Base):
    __tablename__ = "streets"

    street_id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False, index=True)

    city_id = Column(
        Integer,
        ForeignKey("cities.city_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    city = relationship("City", back_populates="streets")

    cameras = relationship(
        "Camera",
        back_populates="street",
        cascade="all, delete-orphan"
    )