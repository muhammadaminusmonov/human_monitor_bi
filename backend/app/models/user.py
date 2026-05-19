from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(150), nullable=False)

    email = Column(String(255), nullable=True, unique=True, index=True)

    date_of_birth = Column(Date, nullable=True)

    role = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chatbot_sessions = relationship(
        "ChatbotLog",
        back_populates="user"
    )