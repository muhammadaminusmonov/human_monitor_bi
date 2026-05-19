from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class City(Base):
    __tablename__ = "cities"

    city_id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False, unique=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    streets = relationship(
        "Street",
        back_populates="city",
        cascade="all, delete-orphan"
    )