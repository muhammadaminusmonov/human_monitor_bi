

import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.camera import Camera
from app.models.detected_object import DetectedObject
from app.models.crowd_telemetry import CrowdTelemetry
from app.models.anomalies_and_alert import AnomaliesAndAlert
from app.models.enums import AlertSeverity
from app.websocket.manager import manager
from app.services.yolo.detector import stream_frames

router = APIRouter()

CROWD_THRESHOLD = 10


@router.websocket("/ws/stream/{camera_id}")
async def camera_stream(
    camera_id: int,
    websocket: WebSocket,
    db: Session = Depends(get_db),
):
    """
    WebSocket стрим кадров с детекцией людей.
    
    Клиент получает JSON:
    {
        "frame": "<base64 JPEG>",
        "person_count": 3,
        "fps": 14.2,
        "detections": [{"object_type": "person", "confidence_score": 0.92, "bbox": [x1,y1,x2,y2]}]
    }
    """
    # Получаем камеру из БД
    camera = db.query(Camera).filter(Camera.camera_id == camera_id).first()
    if camera is None:
        await websocket.accept()
        await websocket.send_json({"error": f"Камера {camera_id} не найдена"})
        await websocket.close()
        return

    # Определяем источник видео
    video_source = camera.video_url or camera.video_file
    if not video_source:
        await websocket.accept()
        await websocket.send_json({"error": "У камеры нет источника видео (url или файл)"})
        await websocket.close()
        return

    await manager.connect(camera_id, websocket)

    try:

        loop = asyncio.get_event_loop()

        def run_stream():
            for frame_data in stream_frames(video_source, conf_threshold=0.4, max_fps=15):
                
                _save_to_db(db, camera_id, frame_data)
                asyncio.run_coroutine_threadsafe(
                    manager.broadcast(camera_id, {
                        "frame": frame_data["frame_b64"],
                        "person_count": frame_data["person_count"],
                        "fps": frame_data["fps"],
                        "detections": frame_data["detections"],
                    }),
                    loop,
                ).result(timeout=2)

        frame_count = [0]
        original_stream = stream_frames.__wrapped__ if hasattr(stream_frames, '__wrapped__') else None

        async def async_stream():
            """Асинхронный wrapper над синхронным генератором."""
            save_every = 30  # сохранять в БД каждые N кадров
            for frame_data in stream_frames(video_source, conf_threshold=0.4, max_fps=15):
                frame_count[0] += 1

                # Отправляем кадр клиенту
                await websocket.send_json({
                    "frame": frame_data["frame_b64"],
                    "person_count": frame_data["person_count"],
                    "fps": frame_data["fps"],
                    "detections": frame_data["detections"],
                })

                # Сохраняем данные в БД периодически
                if frame_count[0] % save_every == 0:
                    await loop.run_in_executor(None, _save_to_db, db, camera_id, frame_data)

                # Небольшая пауза чтобы не захламлять event loop
                await asyncio.sleep(0)

        await async_stream()

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"error": str(e)})
        except Exception:
            pass
    finally:
        manager.disconnect(camera_id, websocket)


def _save_to_db(db: Session, camera_id: int, frame_data: dict):
    """Сохраняет результаты детекции и телеметрию в PostgreSQL."""
    try:
        person_count = frame_data["person_count"]

        # Сохраняем каждый детектированный объект
        for det in frame_data["detections"]:
            obj = DetectedObject(
                camera_id=camera_id,
                object_type=det["object_type"],
                confidence_score=det["confidence_score"],
            )
            db.add(obj)

        # Телеметрия толпы
        telemetry = CrowdTelemetry(
            camera_id=camera_id,
            person_count=person_count,
            crowd_density_score=min(person_count / 20.0, 1.0),  # нормализуем 0..1
        )
        db.add(telemetry)

        # Алерт если слишком много людей
        if person_count >= CROWD_THRESHOLD:
            alert = AnomaliesAndAlert(
                camera_id=camera_id,
                anomaly_type="crowd_overflow",
                severity=AlertSeverity.HIGH if person_count >= 20 else AlertSeverity.MEDIUM,
            )
            db.add(alert)

        db.commit()

    except Exception as e:
        db.rollback()
        print(f"[DB] Ошибка сохранения: {e}")