import asyncio
import traceback
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor

from app.core.dependencies import get_db
from app.models.camera import Camera
from app.websocket.manager import manager
from app.services.yolo.detector import stream_frames

router = APIRouter()

_executor = ThreadPoolExecutor(max_workers=2)


@router.websocket("/ws/stream/{camera_id}")
async def camera_stream(
    camera_id: int,
    websocket: WebSocket,
    db: Session = Depends(get_db),
):

    camera = db.query(Camera).filter(
        Camera.camera_id == camera_id
    ).first()

    await websocket.accept()

    if not camera:
        await websocket.send_json({
            "error": f"Camera {camera_id} not found"
        })
        await websocket.close()
        return

    video_source = camera.video_url or camera.video_file

    if not video_source:
        await websocket.send_json({
            "error": "No video source configured"
        })
        await websocket.close()
        return

    print(f"[WS] Camera {camera_id} connected")
    print(f"[WS] Source: {video_source}")

    loop = asyncio.get_running_loop()

    frame_queue = asyncio.Queue(maxsize=1)

    stop_event = asyncio.Event()

    # =====================================================
    # PRODUCER THREAD
    # =====================================================

    def producer():

        try:

            for frame_data in stream_frames(
                video_source,
                conf_threshold=0.15,
            ):

                if stop_event.is_set():
                    break

                # DROP OLD FRAMES
                if frame_queue.full():
                    try:
                        frame_queue.get_nowait()
                    except:
                        pass

                asyncio.run_coroutine_threadsafe(
                    frame_queue.put(frame_data),
                    loop
                )

        except Exception:

            print("\n========== STREAM ERROR ==========")
            traceback.print_exc()
            print("==================================\n")

            asyncio.run_coroutine_threadsafe(
                frame_queue.put({
                    "error": traceback.format_exc()
                }),
                loop
            )

        finally:

            asyncio.run_coroutine_threadsafe(
                frame_queue.put(None),
                loop
            )

    _executor.submit(producer)

    # =====================================================
    # CONSUMER
    # =====================================================

    try:

        while True:

            frame_data = await asyncio.wait_for(
                frame_queue.get(),
                timeout=30
            )

            if frame_data is None:
                print("[WS] Stream ended")
                break

            if "error" in frame_data:

                print(frame_data["error"])

                await websocket.send_json({
                    "error": frame_data["error"]
                })

                break

            payload = {
                "frame": frame_data["frame_b64"],
                "car_count": frame_data["car_count"],
                "fps": frame_data["fps"],
                "detections": frame_data["detections"],
            }

            await websocket.send_json(payload)

            print(
                f"[WS] sent frame | vehicles={frame_data['car_count']}"
            )

    except WebSocketDisconnect:

        print(f"[WS] disconnected camera {camera_id}")

    except Exception:

        print("\n========== WS ERROR ==========")
        traceback.print_exc()
        print("================================\n")

    finally:

        stop_event.set()

        manager.disconnect(camera_id, websocket)

        try:
            await websocket.close()
        except:
            pass

        print(f"[WS] closed camera {camera_id}")