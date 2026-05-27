import cv2
import numpy as np
import base64
import time
import os
import torch
import sqlite3
import queue
import threading
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from ultralytics import YOLO

# =========================================================
# CONFIG
# =========================================================

os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Отключаем CUDA, если инференс идет на CPU
DEVICE = 0 if torch.cuda.is_available() else "cpu"

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "traffic.db"
WEIGHTS_PATH = BASE_DIR / "models" / "weight" / "best2.pt"

# Идеальная высота для вашей камеры (чуть выше пешеходного перехода)
LINE_Y = 220  

FRAME_SKIP = 3   # Экономия CPU (обрабатываем каждый 3-й кадр)
FPS_LIMIT = 10   # Ограничение FPS для устранения лагов

# =========================================================
# THREAD-SAFE GLOBAL STATE
# =========================================================

_model = None
track_history = defaultdict(list)
counted_ids = set()
car_counter = 0
last_saved_count = 0

frame_queue = queue.Queue(maxsize=2)  # Защита от переполнения памяти
worker_running = False
state_lock = threading.Lock()

# =========================================================
# UTILITIES
# =========================================================

def load_model():
    print(f"[YOLO] Загрузка модели: {WEIGHTS_PATH}")
    return YOLO(str(WEIGHTS_PATH))

def get_model():
    global _model
    if _model is None:
        _model = load_model()
    return _model

def open_video_source(source):
    if isinstance(source, str) and ("youtube.com" in source or "youtu.be" in source):
        import yt_dlp
        print("[YT-DLP] Запрос экономичного потока с YouTube (720p)...")
        ydl_opts = {"quiet": True, "format": "best[height<=720]/worst"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(source, download=False)
            source = info["url"]

    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "timeout;3000000" 
    cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap

def save_traffic_log(camera_id: int, cars_count: int):
    """Прямая безопасная запись логов в вашу базу данных PostgreSQL."""
    import psycopg2
    try:
        # 1. Получаем текущее время в формате, который ожидает колонка 'timestamp without time zone'
        current_datetime = datetime.now()
        current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"[POSTGRES TRY] Попытка записи. Время: {current_datetime_str}, Машин: {cars_count}")

        # 2. Подключаемся напрямую к вашей БД PostgreSQL
        # Используем те же параметры, что указаны в DATABASE_URL
        conn = psycopg2.connect(
            dbname="smart_city_db",
            user="postgres",
            password="root",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()

        # 3. Записываем данные. Имена таблиц в PostgreSQL чувствительны к регистру, 
        # поэтому пишем 'traffic_logs' строго строчными буквами, как в вашей схеме.
        cur.execute("""
            INSERT INTO traffic_logs (camera_id, timestamp, cars_count)
            VALUES (%s, %s, %s)
        """, (camera_id, current_datetime, cars_count))

        # 4. Фиксируем транзакцию
        conn.commit()
        cur.close()
        conn.close()
        print(f"[POSTGRES SUCCESS] Лог успешно сохранен в PostgreSQL! Камера: {camera_id}")

    except Exception as e:
        print("[POSTGRES ERROR] Ошибка записи в базу данных PostgreSQL:", e)

    except Exception as e:
        print("[DB ERROR] Ошибка записи типа данных TIMESTAMP:", e)

def frame_to_base64(frame, quality=70):
    _, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    return base64.b64encode(buffer).decode("utf-8")

def crossed(prev_y, curr_y, line_y):
    # Двунаправленный подсчет (сверху-вниз и снизу-вверх)
    return (prev_y < line_y and curr_y >= line_y) or (prev_y > line_y and curr_y <= line_y)

# =========================================================
# CORE COMPUTER VISION ENGINE
# =========================================================

def detect_objects(frame, camera_id=1, conf_threshold=0.15):
    global car_counter

    model = get_model()
    results = model.track(
        source=frame, persist=True, conf=conf_threshold,
        imgsz=480, device=DEVICE, verbose=False, tracker="bytetrack.yaml"
    )[0]

    annotated = frame.copy()
    detections = []
    
    height, width, _ = frame.shape
    cv2.line(annotated, (0, LINE_Y), (width, LINE_Y), (255, 255, 0), 3)

    if results.boxes is None or len(results.boxes) == 0:
        cv2.putText(annotated, f"Total Vehicles Crossed: {car_counter}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return annotated, detections, 0

    for box in results.boxes:
        if box.id is None:
            continue

        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        class_name = model.names[cls_id]

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        track_id = int(box.id[0])

        with state_lock:
            track_history[track_id].append((cx, cy))
            if len(track_history[track_id]) > 2:
                track_history[track_id].pop(0)

            if len(track_history[track_id]) == 2:
                prev = track_history[track_id][0]
                curr = track_history[track_id][1]

                if track_id not in counted_ids:
                    if crossed(prev[1], curr[1], LINE_Y):
                        car_counter += 1
                        counted_ids.add(track_id)
                        
                        # ТРИГГЕР СОБЫТИЯ: Записываем в PostgreSQL строго в момент пересечения!
                        save_traffic_log(camera_id, 1) 

        # Отрисовка UI
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 200, 255), 2)
        cv2.circle(annotated, (cx, cy), 4, (0, 0, 255), -1)
        cv2.putText(annotated, f"ID: {track_id}", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1)

        detections.append({
            "id": track_id, "class": class_name, "confidence": round(conf, 3),
            "bbox": [x1, y1, x2, y2], "category": "vehicle"
        })

    cv2.putText(annotated, f"Total Vehicles Crossed: {car_counter}", (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    return annotated, detections, len(results.boxes)


# =========================================================
# ИСПРАВЛЕННЫЙ ВОРКЕР (Очищен от багов со счетчиком)
# =========================================================

def _video_processing_worker(source, camera_id, conf_threshold):
    global worker_running
    print("[THREAD-WORKER] Фоновый движок успешно запущен.")
    
    while worker_running:
        cap = None
        try:
            cap = open_video_source(source)
            frame_id = 0
            
            while worker_running:
                ret, frame = cap.read()
                if not ret:
                    print("[THREAD-WORKER] Сбой чтения фрейма. Переподключение...")
                    break

                frame_id += 1
                if frame_id % FRAME_SKIP != 0:
                    continue

                # Передаем camera_id внутрь детектора
                annotated, detections, vehicle_count = detect_objects(frame, camera_id, conf_threshold)

                packet = {
                    "frame_b64": frame_to_base64(annotated),
                    "car_count": car_counter,
                    "detections": detections,
                    "current_frame_vehicles": vehicle_count,
                    "fps": FPS_LIMIT
                }

                if frame_queue.full():
                    try:
                        frame_queue.get_nowait()
                    except queue.Empty:
                        pass
                        
                frame_queue.put(packet)
                time.sleep(1 / FPS_LIMIT)
                
        except Exception as e:
            print(f"[THREAD-WORKER ERROR]: {e}")
            time.sleep(3)
        finally:
            if cap:
                cap.release()
                
    print("[THREAD-WORKER] Фоновый движок полностью остановлен.")


# =========================================================
# БЕЗОПАСНЫЙ СИНГЛТОН-ИНТЕРФЕЙС СТРИМА (stream_frames)
# =========================================================

def stream_frames(source, camera_id=1, conf_threshold=None):
    global worker_running
    if conf_threshold is None:
        conf_threshold = CONF_THRESHOLD

    # ПРОВЕРКА: Если поток уже запущен, НЕ создаем дубликат!
    # Просто очищаем старую очередь и подлючаемся к существующему конвейеру данных.
    if not worker_running:
        while not frame_queue.empty():
            try:
                frame_queue.get_nowait()
            except queue.Empty:
                break

        worker_running = True
        worker_thread = threading.Thread(
            target=_video_processing_worker,
            args=(source, camera_id, conf_threshold),
            daemon=True
        )
        worker_thread.start()
    else:
        print("[STREAM] Подключение к уже запущенному фоновому потоку обработки.")

    try:
        while worker_running:
            try:
                packet = frame_queue.get(timeout=0.2)
                yield packet
            except queue.Empty:
                continue
    finally:
        # ВНИМАНИЕ: Убираем здесь worker_running = False!
        # Поток должен продолжать жить в фоне, даже если один из пользователей закрыл вкладку браузера.
        # Таким образом, детекция и запись в БД не прервутся ни на секунду.
        pass