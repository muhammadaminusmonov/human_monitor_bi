from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.models.chatbot import ChatbotLog
from app.core.dependencies import get_db

# ── Pydantic schemas ──────────────────────────────────────
from pydantic import BaseModel, Field


class ChatbotLogCreate(BaseModel):
    session_id: str = Field(..., max_length=100)
    user_id: Optional[int] = None
    query_text: str = Field(..., max_length=2000)
    response_text: str = Field(..., max_length=5000)
    response_time_ms: Optional[int] = None
    ai_model_used: Optional[str] = Field(None, max_length=100)
    timestamp: Optional[datetime] = None


class ChatbotLogUpdate(BaseModel):
    query_text: Optional[str] = Field(None, max_length=2000)
    response_text: Optional[str] = Field(None, max_length=5000)
    response_time_ms: Optional[int] = None
    ai_model_used: Optional[str] = Field(None, max_length=100)


class ChatbotLogRead(BaseModel):
    chatbot_id: int
    session_id: str
    user_id: Optional[int]
    query_text: str
    response_text: str
    response_time_ms: Optional[int]
    ai_model_used: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


# ── Router ────────────────────────────────────────────────
router = APIRouter(prefix="/chatbot-logs", tags=["Chatbot Logs"])


@router.get("/", response_model=List[ChatbotLogRead])
def list_logs(
    skip: int = 0,
    limit: int = 100,
    session_id: Optional[str] = None,
    user_id: Optional[int] = None,
    ai_model_used: Optional[str] = None,
    from_time: Optional[datetime] = None,
    to_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """List chatbot logs with optional filters."""
    q = db.query(ChatbotLog)
    if session_id:
        q = q.filter(ChatbotLog.session_id == session_id)
    if user_id:
        q = q.filter(ChatbotLog.user_id == user_id)
    if ai_model_used:
        q = q.filter(ChatbotLog.ai_model_used == ai_model_used)
    if from_time:
        q = q.filter(ChatbotLog.timestamp >= from_time)
    if to_time:
        q = q.filter(ChatbotLog.timestamp <= to_time)
    return q.order_by(ChatbotLog.timestamp.desc()).offset(skip).limit(limit).all()


@router.get("/stats/summary", response_model=dict)
def stats_summary(
    from_time: Optional[datetime] = None,
    to_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """
    Aggregate stats:
      - total_queries
      - avg_response_time_ms
      - unique_sessions
      - unique_users
      - queries per ai_model_used
    """
    q = db.query(ChatbotLog)
    if from_time:
        q = q.filter(ChatbotLog.timestamp >= from_time)
    if to_time:
        q = q.filter(ChatbotLog.timestamp <= to_time)

    total        = q.count()
    avg_rt       = q.with_entities(func.avg(ChatbotLog.response_time_ms)).scalar()
    unique_sess  = q.with_entities(func.count(func.distinct(ChatbotLog.session_id))).scalar()
    unique_users = q.with_entities(func.count(func.distinct(ChatbotLog.user_id))).scalar()

    model_rows = (
        q.with_entities(
            ChatbotLog.ai_model_used,
            func.count(ChatbotLog.chatbot_id).label("count"),
        )
        .group_by(ChatbotLog.ai_model_used)
        .all()
    )

    return {
        "total_queries": total,
        "avg_response_time_ms": round(avg_rt, 1) if avg_rt else None,
        "unique_sessions": unique_sess,
        "unique_users": unique_users,
        "queries_by_model": [
            {"ai_model_used": r.ai_model_used or "unknown", "count": r.count}
            for r in model_rows
        ],
    }


@router.get("/stats/by-session", response_model=dict)
def stats_by_session(
    from_time: Optional[datetime] = None,
    to_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """Query count grouped by session_id."""
    q = db.query(
        ChatbotLog.session_id,
        func.count(ChatbotLog.chatbot_id).label("count"),
    )
    if from_time:
        q = q.filter(ChatbotLog.timestamp >= from_time)
    if to_time:
        q = q.filter(ChatbotLog.timestamp <= to_time)
    rows = q.group_by(ChatbotLog.session_id).order_by(func.count(ChatbotLog.chatbot_id).desc()).limit(50).all()
    return {"data": [{"session_id": r.session_id, "count": r.count} for r in rows]}


@router.get("/{chatbot_id}", response_model=ChatbotLogRead)
def get_log(chatbot_id: int, db: Session = Depends(get_db)):
    log = db.query(ChatbotLog).filter(ChatbotLog.chatbot_id == chatbot_id).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot log not found")
    return log


@router.post("/", response_model=ChatbotLogRead, status_code=status.HTTP_201_CREATED)
def create_log(payload: ChatbotLogCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    if not data.get("timestamp"):
        data["timestamp"] = datetime.utcnow()
    log = ChatbotLog(**data)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.patch("/{chatbot_id}", response_model=ChatbotLogRead)
def update_log(chatbot_id: int, payload: ChatbotLogUpdate, db: Session = Depends(get_db)):
    log = db.query(ChatbotLog).filter(ChatbotLog.chatbot_id == chatbot_id).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot log not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{chatbot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log(chatbot_id: int, db: Session = Depends(get_db)):
    log = db.query(ChatbotLog).filter(ChatbotLog.chatbot_id == chatbot_id).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot log not found")
    db.delete(log)
    db.commit()