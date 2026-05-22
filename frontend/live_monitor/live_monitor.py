"""
Страница мониторинга камер — живой стрим + детекция людей через YOLO.
Добавить в sidebar как: pages/live_monitor.py
или вызвать напрямую из streamlit_app.py
"""

import streamlit as st
import requests
import websocket
import json
import base64
import threading
import time
import queue
from io import BytesIO
from PIL import Image
import numpy as np

API_URL = "http://localhost:8000"
WS_URL  = "ws://localhost:8000"


# ──────────────────────────────────────────────
# Вспомогательные функции
# ──────────────────────────────────────────────

def get_cameras():
    try:
        r = requests.get(f"{API_URL}/cameras/", timeout=5)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []


def base64_to_pil(b64: str) -> Image.Image:
    img_bytes = base64.b64decode(b64)
    return Image.open(BytesIO(img_bytes))


# ──────────────────────────────────────────────
# WebSocket поток (в отдельном потоке)
# ──────────────────────────────────────────────

class CameraStream:
    """Читает WebSocket в фоне и складывает последний кадр в очередь."""

    def __init__(self, camera_id: int):
        self.camera_id = camera_id
        self.q: queue.Queue = queue.Queue(maxsize=2)
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        url = f"{WS_URL}/ws/stream/{self.camera_id}"
        try:
            ws = websocket.create_connection(url, timeout=10)
            while not self._stop.is_set():
                raw = ws.recv()
                data = json.loads(raw)
                # Если очередь полна — сбрасываем старый кадр
                if self.q.full():
                    try:
                        self.q.get_nowait()
                    except queue.Empty:
                        pass
                self.q.put(data)
            ws.close()
        except Exception as e:
            self.q.put({"error": str(e)})

    def get_frame(self, timeout: float = 1.0):
        try:
            return self.q.get(timeout=timeout)
        except queue.Empty:
            return None

    def stop(self):
        self._stop.set()


# ──────────────────────────────────────────────
# UI
# ──────────────────────────────────────────────

def render_live_monitor():
    st.markdown("""
    <h2 style='background:linear-gradient(90deg,#00E5FF,#4ADE80);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               font-size:32px;font-weight:800;'>
        🎥 Live Camera Monitor
    </h2>
    """, unsafe_allow_html=True)

    cameras = get_cameras()

    if not cameras:
        st.warning("Камеры не найдены. Сначала добавьте камеру через форму ниже.")
        _render_add_camera_form()
        return

    # ── Выбор камеры ──
    cam_options = {f"[{c['camera_id']}] {c['camera_name']}": c for c in cameras}
    selected_name = st.selectbox("Выберите камеру", list(cam_options.keys()))
    selected_cam = cam_options[selected_name]

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f"**Источник:** `{selected_cam.get('video_url') or selected_cam.get('video_file') or 'не задан'}`")

        # Placeholder для кадра
        frame_placeholder = st.empty()
        info_placeholder  = st.empty()

        # Кнопка старт/стоп
        if "stream_running" not in st.session_state:
            st.session_state.stream_running = False
        if "stream_obj" not in st.session_state:
            st.session_state.stream_obj = None

        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("▶ Запустить", type="primary", use_container_width=True):
                if st.session_state.stream_obj:
                    st.session_state.stream_obj.stop()
                st.session_state.stream_obj = CameraStream(selected_cam["camera_id"])
                st.session_state.stream_running = True

        with btn_col2:
            if st.button("⏹ Остановить", use_container_width=True):
                if st.session_state.stream_obj:
                    st.session_state.stream_obj.stop()
                    st.session_state.stream_obj = None
                st.session_state.stream_running = False
                frame_placeholder.empty()

        # Живой стрим
        if st.session_state.stream_running and st.session_state.stream_obj:
            stream: CameraStream = st.session_state.stream_obj

            # Читаем ~30 кадров в одном run Streamlit
            for _ in range(30):
                data = stream.get_frame(timeout=1.5)
                if data is None:
                    continue

                if "error" in data:
                    st.error(f"Ошибка стрима: {data['error']}")
                    st.session_state.stream_running = False
                    break

                # Показываем кадр
                img = base64_to_pil(data["frame"])
                frame_placeholder.image(img, use_column_width=True, caption="YOLO Detection")

                # Статистика
                count   = data.get("person_count", 0)
                fps     = data.get("fps", 0)
                color   = "#4ADE80" if count < 10 else ("#F59E0B" if count < 20 else "#EF4444")
                info_placeholder.markdown(f"""
                <div style='background:rgba(17,25,40,0.8);border-radius:12px;padding:14px;
                            border:1px solid rgba(255,255,255,0.08);margin-top:8px;'>
                    <span style='color:#9CA3AF;font-size:14px;'>Людей на кадре</span><br>
                    <span style='color:{color};font-size:42px;font-weight:800;'>{count}</span>
                    &nbsp;&nbsp;
                    <span style='color:#9CA3AF;font-size:13px;'>FPS: {fps}</span>
                </div>
                """, unsafe_allow_html=True)

                time.sleep(0.05)

            # Перезапуск Streamlit для следующей порции кадров
            st.rerun()

    with col2:
        st.markdown("#### 📋 Инфо о камере")
        st.json({
            "ID": selected_cam.get("camera_id"),
            "Статус": selected_cam.get("status"),
            "Улица": selected_cam.get("street_id"),
            "Локация": selected_cam.get("location_id"),
        })

    st.divider()
    _render_add_camera_form()


def _render_add_camera_form():
    """Форма добавления новой камеры."""
    with st.expander("➕ Добавить новую камеру", expanded=False):
        st.markdown("Введите данные камеры. Источником может быть **URL потока** или **загруженный видеофайл**.")

        with st.form("add_camera_form"):
            cam_name   = st.text_input("Название камеры", placeholder="Cam-01 / Entrance")
            street_id  = st.number_input("ID улицы",   min_value=1, value=1)
            loc_id     = st.number_input("ID локации", min_value=1, value=1)

            source_type = st.radio("Источник видео", ["URL потока / видео", "Загрузить файл MP4"], horizontal=True)

            video_url  = None
            video_file = None

            if source_type == "URL потока / видео":
                video_url = st.text_input(
                    "URL",
                    placeholder="rtsp://... или https://example.com/video.mp4"
                )
                st.caption("Поддерживаются: RTSP, HTTP MP4, YouTube (через yt-dlp), веб-камера (0)")
            else:
                video_file = st.file_uploader("Видеофайл MP4", type=["mp4", "avi", "mov"])

            submitted = st.form_submit_button("💾 Сохранить камеру", type="primary")

            if submitted:
                if not cam_name:
                    st.error("Введите название камеры")
                elif source_type == "URL потока / видео" and not video_url:
                    st.error("Введите URL видео")
                elif source_type == "Загрузить файл MP4" and video_file is None:
                    st.error("Выберите видеофайл")
                else:
                    _submit_camera(cam_name, street_id, loc_id, video_url, video_file)


def _submit_camera(name, street_id, loc_id, video_url, video_file):
    """Отправляет POST /cameras/ в FastAPI."""
    try:
        data = {
            "camera_name": name,
            "street_id":   str(street_id),
            "location_id": str(loc_id),
            "status":      "active",
        }
        files = {}

        if video_url:
            data["video_url"] = video_url

        if video_file:
            files["video_file"] = (video_file.name, video_file.getvalue(), "video/mp4")

        r = requests.post(f"{API_URL}/cameras/", data=data, files=files if files else None, timeout=30)

        if r.status_code in (200, 201):
            st.success(f"✅ Камера '{name}' успешно добавлена! ID: {r.json().get('camera_id')}")
            st.rerun()
        else:
            st.error(f"Ошибка API: {r.status_code} — {r.text}")

    except Exception as e:
        st.error(f"Ошибка подключения к бэкенду: {e}")


# ──────────────────────────────────────────────
# Запуск как самостоятельная страница
# ──────────────────────────────────────────────
if __name__ == "__main__" or True:
    render_live_monitor()