"""
YOLO Human Detector
Загружает модель best.pt и детектирует людей из видео/потока.
"""

import cv2
import numpy as np
import base64
import time
import os
from pathlib import Path
from typing import Generator, Tuple, List, Dict, Any

# Путь к весам модели
WEIGHTS_PATH = Path(__file__).parent.parent.parent / "models" / "weight" / "best.pt"


def load_model():
    """Загружает YOLO модель. best.pt если есть, иначе yolov8n.pt (скачается автоматически)."""
    try:
        from ultralytics import YOLO

        if WEIGHTS_PATH.exists():
            print(f"[YOLO] Загружаем модель: {WEIGHTS_PATH}")
            model = YOLO(str(WEIGHTS_PATH))
        else:
            print("[YOLO] best.pt не найден — загружаем стандартную yolov8n.pt")
            model = YOLO("yolov8n.pt")

        print("[YOLO] Модель загружена успешно")
        return model

    except ImportError:
        raise RuntimeError("ultralytics не установлен. Запустите: pip install ultralytics")


# Глобальный экземпляр модели (singleton)
_model = None


def get_model():
    global _model
    if _model is None:
        _model = load_model()
    return _model


def detect_humans(frame: np.ndarray, conf_threshold: float = 0.4) -> Tuple[np.ndarray, List[Dict]]:
    """
    Детектирует людей на кадре.

    Возвращает:
        annotated_frame - кадр с нарисованными боксами
        detections - список словарей с данными о каждом объекте
    """
    model = get_model()

    results = model(frame, conf=conf_threshold, verbose=False)[0]

    detections = []
    annotated_frame = frame.copy()

    for box in results.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        class_name = model.names[cls_id]

        if class_name != "person":
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 100), 2)
        label = f"Person {conf:.0%}"
        (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        cv2.rectangle(annotated_frame, (x1, y1 - lh - 8), (x1 + lw, y1), (0, 255, 100), -1)
        cv2.putText(annotated_frame, label, (x1, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1)

        detections.append({
            "object_type": "person",
            "confidence_score": round(conf, 3),
            "bbox": [x1, y1, x2, y2],
        })

    count = len(detections)
    label_count = f"People: {count}"
    cv2.rectangle(annotated_frame, (8, 8), (160, 38), (0, 0, 0), -1)
    cv2.putText(annotated_frame, label_count, (12, 29),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 100), 2)

    return annotated_frame, detections


def frame_to_base64(frame: np.ndarray, quality: int = 75) -> str:
    """Конвертирует кадр OpenCV в base64 JPEG строку для передачи по WebSocket."""
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, buffer = cv2.imencode(".jpg", frame, encode_param)
    return base64.b64encode(buffer).decode("utf-8")


# =========================================================
# ✅ НОВАЯ ФУНКЦИЯ — резолвинг источника видео
# =========================================================

def resolve_video_source(source: str) -> str:
    """
    Преобразует источник видео в прямой URL для OpenCV.

    - YouTube / youtu.be  → прямой CDN URL через yt-dlp
    - RTSP / HTTP / файл  → без изменений
    """
    if not isinstance(source, str):
        return source  # int (webcam index) — возвращаем как есть

    is_youtube = (
        "youtube.com/watch" in source
        or "youtu.be/" in source
        or "youtube.com/shorts" in source
    )

    if is_youtube:
        try:
            import yt_dlp  # pip install yt-dlp
        except ImportError:
            raise RuntimeError(
                "yt-dlp не установлен. Запустите: pip install yt-dlp"
            )

        ydl_opts = {
            # Предпочитаем mp4 с прямым URL без склейки дашей
            "format": "best[ext=mp4]/best[protocol=https]/best",
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(source, download=False)
                direct_url = info.get("url")
                if not direct_url:
                    # Иногда url лежит внутри formats
                    formats = info.get("formats", [])
                    if formats:
                        direct_url = formats[-1]["url"]
                if not direct_url:
                    raise RuntimeError("yt-dlp не вернул URL")
                print(f"[yt-dlp] Резолвнули YouTube → {direct_url[:80]}...")
                return direct_url
        except Exception as e:
            raise RuntimeError(f"Не удалось получить URL с YouTube: {e}")

    return source


# =========================================================
# ✅ ИСПРАВЛЕННАЯ open_video_source
# =========================================================

def open_video_source(source: str | int) -> cv2.VideoCapture:
    """
    Открывает видео из файла, URL-потока, YouTube или веб-камеры.
    YouTube-ссылки автоматически резолвятся через yt-dlp.
    """
    real_source = resolve_video_source(source)

    # Для сетевых потоков используем CAP_FFMPEG явно
    if isinstance(real_source, str) and (
        real_source.startswith("rtsp://")
        or real_source.startswith("http://")
        or real_source.startswith("https://")
    ):
        cap = cv2.VideoCapture(real_source, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    else:
        cap = cv2.VideoCapture(real_source)

    if not cap.isOpened():
        raise RuntimeError(f"Не удалось открыть источник видео: {source}")

    return cap


def stream_frames(
    source: str | int,
    conf_threshold: float = 0.4,
    max_fps: int = 15,
) -> Generator[Dict[str, Any], None, None]:
    """
    Генератор кадров с детекцией.
    Используется в WebSocket endpoint.

    Yields словари:
        {
            "frame_b64": str,
            "person_count": int,
            "detections": List[Dict],
            "fps": float,
        }
    """
    cap = open_video_source(source)  # ✅ теперь резолвит YouTube автоматически
    frame_interval = 1.0 / max_fps
    prev_time = 0.0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                # Видеофайл закончился — перемотка
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
                if not ret:
                    break

            now = time.time()
            elapsed = now - prev_time
            if elapsed < frame_interval:
                time.sleep(frame_interval - elapsed)
                continue
            prev_time = time.time()

            annotated, detections = detect_humans(frame, conf_threshold)

            fps = 1.0 / max(elapsed, 1e-6)

            yield {
                "frame_b64": frame_to_base64(annotated),
                "person_count": len(detections),
                "detections": detections,
                "fps": round(fps, 1),
            }
    finally:
        cap.release()