from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base



class ChatbotLog(Base):
    __tablename__ = "chatbot_logs"

    chatbot_id = Column(Integer, primary_key=True, index=True)

    session_id = Column(String(100), nullable=False, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    query_text = Column(String(2000), nullable=False)

    response_text = Column(String(5000), nullable=False)

    response_time_ms = Column(Integer, nullable=True)

    ai_model_used = Column(String(100), nullable=True)

    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    user = relationship("User", back_populates="chatbot_sessions")