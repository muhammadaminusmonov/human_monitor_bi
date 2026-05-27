from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import cv2
import yt_dlp

from app.core.dependencies import get_db
from app.models.camera import Camera
from app.models.enums import CameraStatus

router = APIRouter(prefix="/cameras", tags=["Cameras"])

UPLOAD_DIR = "uploads"
Path(UPLOAD_DIR).mkdir(exist_ok=True)


def resolve_video_source(video_source: str) -> str:
    """Резолвим YouTube → прямой URL. RTSP/HTTP/файл — без изменений."""
    if not video_source:
        return video_source
    if "youtube.com" in video_source or "youtu.be" in video_source:
        try:
            ydl_opts = {"format": "best[ext=mp4]/best", "quiet": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_source, download=False)
                return info["url"]
        except Exception as e:
            raise RuntimeError(f"Не удалось получить URL с YouTube: {e}")
    return video_source


def generate_camera_stream(video_source: str):
    """Генератор MJPEG стрима."""
    try:
        real_source = resolve_video_source(video_source)
    except RuntimeError as e:
        # Возвращаем пустой стрим с ошибкой
        yield b''
        return

    cap = cv2.VideoCapture(real_source, cv2.CAP_FFMPEG)  # ✅ используем реальный источник
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        print(f"❌ Не удалось открыть: {real_source}")
        cap.release()
        return

    try:
        while True:
            success, frame = cap.read()
            if not success:
                break

            _, buffer = cv2.imencode(".jpg", frame)
            frame_bytes = buffer.tobytes()

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' +
                frame_bytes +
                b'\r\n'
            )
    finally:
        cap.release()


@router.post("/")
def create_camera(
    camera_name: str = Form(...),
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
        location_id=location_id,
        status=status,
        video_url=video_url,
        video_file=saved_video
    )

    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


@router.get("/")
def get_cameras(db: Session = Depends(get_db)):
    return db.query(Camera).all()


@router.get("/stream/{camera_id}")
def stream_camera(camera_id: int, db: Session = Depends(get_db)):
    camera = db.query(Camera).filter(Camera.camera_id == camera_id).first()

    if not camera:
        return {"error": "Camera not found"}

    video_source = camera.video_file if camera.video_file else camera.video_url

    if not video_source:
        return {"error": "No video source"}

    return StreamingResponse(
        generate_camera_stream(video_source),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )