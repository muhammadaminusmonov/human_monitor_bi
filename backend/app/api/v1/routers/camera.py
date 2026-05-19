from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.camera import Camera
from app.models.enums import CameraStatus

router = APIRouter(prefix="/cameras", tags=["Cameras"])


@router.post("/")
def create_camera(
    camera_name: str,
    street_id: int,
    location_id: int,
    status: CameraStatus = CameraStatus.ACTIVE,
    db: Session = Depends(get_db)
):
    camera = Camera(
        camera_name=camera_name,
        street_id=street_id,
        location_id=location_id,
        status=status
    )

    db.add(camera)
    db.commit()
    db.refresh(camera)

    return camera

@router.get("/")
def get_cameras(db: Session = Depends(get_db)):
    return db.query(Camera).all()