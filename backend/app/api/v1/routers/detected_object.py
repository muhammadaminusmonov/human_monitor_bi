from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.detected_object import DetectedObject
from app.models.enums import DetectionType

router = APIRouter(prefix="/detected-objects", tags=["Detected Objects"])


@router.post("/")
def create_detected_object(
    camera_id: int,
    object_type: DetectionType,
    confidence_score: float,
    db: Session = Depends(get_db)
):
    detected_object = DetectedObject(
        camera_id=camera_id,
        object_type=object_type,
        confidence_score=confidence_score
    )

    db.add(detected_object)
    db.commit()
    db.refresh(detected_object)

    return detected_object