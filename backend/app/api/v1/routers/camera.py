from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile
)

from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

from pathlib import Path

import shutil
import cv2

from app.core.dependencies import get_db

from app.models.camera import Camera
from app.models.enums import CameraStatus

from app.services.yolo_service import process_frame



router = APIRouter(
    prefix="/cameras",
    tags=["Cameras"]
)


UPLOAD_DIR = "uploads"

Path(UPLOAD_DIR).mkdir(exist_ok=True)



def generate_camera_stream(video_source):

    cap = cv2.VideoCapture(video_source)

    while True:

        success, frame = cap.read()

        if not success:
            break

        processed_frame, detections = process_frame(frame)

   
        _, buffer = cv2.imencode(".jpg", processed_frame)

        frame_bytes = buffer.tobytes()

        # MJPEG STREAM
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            frame_bytes +
            b'\r\n'
        )

    cap.release()




@router.post("/")
def create_camera(

    camera_name: str = Form(...),

    street_id: int = Form(...),

    location_id: int = Form(...),

    status: CameraStatus = Form(CameraStatus.ACTIVE),

    video_url: str = Form(None),

    video_file: UploadFile = File(None),

    db: Session = Depends(get_db)

):

    saved_video = None

    if video_file:

        file_path = f"{UPLOAD_DIR}/{video_file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)

        saved_video = file_path

    camera = Camera(
        camera_name=camera_name,
        street_id=street_id,
        location_id=location_id,
        status=status,
        video_url=video_url,
        video_file=saved_video
    )

    db.add(camera)

    db.commit()

    db.refresh(camera)

    return camera


# =========================================================
# GET ALL CAMERAS
# =========================================================

@router.get("/")
def get_cameras(
    db: Session = Depends(get_db)
):

    return db.query(Camera).all()


# =========================================================
# LIVE STREAM
# =========================================================

@router.get("/stream/{camera_id}")
def stream_camera(
    camera_id: int,
    db: Session = Depends(get_db)
):

    # FIND CAMERA
    camera = db.query(Camera).filter(
        Camera.camera_id == camera_id
    ).first()

    if not camera:
        return {"error": "Camera not found"}

    # PRIORITY:
    # uploaded video > stream url

    video_source = (
        camera.video_file
        if camera.video_file
        else camera.video_url
    )

    if not video_source:
        return {"error": "No video source"}

    return StreamingResponse(
        generate_camera_stream(video_source),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )