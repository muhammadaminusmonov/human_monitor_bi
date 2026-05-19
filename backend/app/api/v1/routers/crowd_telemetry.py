from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.crowd_telemetry import CrowdTelemetry

router = APIRouter(prefix="/crowd-telemetry", tags=["Crowd Telemetry"])


@router.post("/")
def create_telemetry(
    camera_id: int,
    person_count: int,
    crowd_density_score: float,
    db: Session = Depends(get_db)
):
    telemetry = CrowdTelemetry(
        camera_id=camera_id,
        person_count=person_count,
        crowd_density_score=crowd_density_score
    )

    db.add(telemetry)
    db.commit()
    db.refresh(telemetry)

    return telemetry


@router.get("/")
def get_telemetry(db: Session = Depends(get_db)):
    return db.query(CrowdTelemetry).all()