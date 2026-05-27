from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime

from app.models.trafficLogs import TrafficLog
from app.schemas.trafficLogs import TrafficLogCreate, TrafficLogRead, TrafficLogUpdate
from app.core.dependencies import get_db

router = APIRouter(prefix="/traffic-logs", tags=["Traffic Logs"])


@router.get("/", response_model=List[TrafficLogRead])
def list_logs(
    skip: int = 0,
    limit: int = 100,
    camera_id: int = None,
    from_time: datetime = None,
    to_time: datetime = None,
    db: Session = Depends(get_db),
):
    q = db.query(TrafficLog)
    if camera_id:
        q = q.filter(TrafficLog.camera_id == camera_id)
    if from_time:
        q = q.filter(TrafficLog.timestamp >= from_time)
    if to_time:
        q = q.filter(TrafficLog.timestamp <= to_time)
    return q.order_by(TrafficLog.timestamp.desc()).offset(skip).limit(limit).all()


@router.get("/stats/total-cars", response_model=dict)
def total_cars_by_camera(
    camera_id: int = None,
    from_time: datetime = None,
    to_time: datetime = None,
    db: Session = Depends(get_db),
):
    """Aggregate cars_count grouped by camera."""
    q = db.query(TrafficLog.camera_id, func.sum(TrafficLog.cars_count).label("total"))
    if camera_id:
        q = q.filter(TrafficLog.camera_id == camera_id)
    if from_time:
        q = q.filter(TrafficLog.timestamp >= from_time)
    if to_time:
        q = q.filter(TrafficLog.timestamp <= to_time)
    rows = q.group_by(TrafficLog.camera_id).all()
    return {"data": [{"camera_id": r.camera_id, "total_cars": r.total} for r in rows]}


@router.get("/{logs_id}", response_model=TrafficLogRead)
def get_log(logs_id: int, db: Session = Depends(get_db)):
    log = db.query(TrafficLog).filter(TrafficLog.logs_id == logs_id).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Traffic log not found")
    return log


@router.post("/", response_model=TrafficLogRead, status_code=status.HTTP_201_CREATED)
def create_log(payload: TrafficLogCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    if not data.get("timestamp"):
        data["timestamp"] = datetime.utcnow()
    log = TrafficLog(**data)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.patch("/{logs_id}", response_model=TrafficLogRead)
def update_log(logs_id: int, payload: TrafficLogUpdate, db: Session = Depends(get_db)):
    log = db.query(TrafficLog).filter(TrafficLog.logs_id == logs_id).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Traffic log not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{logs_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log(logs_id: int, db: Session = Depends(get_db)):
    log = db.query(TrafficLog).filter(TrafficLog.logs_id == logs_id).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Traffic log not found")
    db.delete(log)
    db.commit()
