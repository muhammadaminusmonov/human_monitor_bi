import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import websocket
import json
import base64
import threading
import time
import queue
from io import BytesIO
from PIL import Image

API_URL = "http://localhost:8000"
WS_URL  = "ws://localhost:8000"

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ASSBI Smart Surveillance",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

st_autorefresh(interval=5000, key="refresh")

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0B1120;
    color: white;
}

.main-title {
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(90deg, #00E5FF, #4ADE80);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
}

.card {
    background: rgba(17, 25, 40, 0.75);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 22px;
    border-radius: 20px;
    margin-bottom: 18px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
    transition: 0.3s ease;
}

.card:hover {
    transform: translateY(-4px);
    border: 1px solid #00E5FF;
}

.metric-card {
    background: linear-gradient(
        145deg,
        rgba(0,229,255,0.15),
        rgba(74,222,128,0.08)
    );
    padding: 25px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.08);
    text-align: center;
}

.metric-title {
    color: #9CA3AF;
    font-size: 15px;
}

.metric-value {
    font-size: 38px;
    font-weight: 800;
    margin-top: 10px;
}

.status-online {
    color: #4ADE80;
    font-weight: 700;
}

.status-offline {
    color: #EF4444;
    font-weight: 700;
}

.status-maintenance {
    color: #F59E0B;
    font-weight: 700;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid rgba(255,255,255,0.06);
}

.stButton > button {
    background: linear-gradient(90deg,#00E5FF,#06B6D4);
    color: black;
    border: none;
    border-radius: 12px;
    font-weight: 700;
    padding: 12px 20px;
    width: 100%;
}

.stButton > button:hover {
    opacity: 0.9;
}

.stTextInput input {
    border-radius: 12px !important;
}

.stSelectbox div[data-baseweb="select"] {
    border-radius: 12px !important;
}

.chat-user {
    background: #1E293B;
    padding: 16px;
    border-radius: 16px;
    margin-bottom: 12px;
}

.chat-ai {
    background: #082F49;
    padding: 16px;
    border-radius: 16px;
    margin-bottom: 18px;
}

[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.markdown(
    "<div class='main-title'>🧠 ASSBI Smart Surveillance Platform</div>",
    unsafe_allow_html=True
)

st.caption(
    "AI-Powered Monitoring • Crowd Analytics • Real-Time Security Intelligence"
)

# =========================================================
# API HELPERS
# =========================================================

@st.cache_data(ttl=5)
def fetch(endpoint):
    try:
        r = requests.get(f"{API_URL}/{endpoint}", timeout=5)
        if r.status_code == 200:
            return r.json()
        return []
    except Exception:
        return []

def post_json(endpoint, payload):
    try:
        r = requests.post(
            f"{API_URL}/{endpoint}",
            json=payload,
            timeout=10
        )
        return r
    except Exception as e:
        st.error(str(e))
        return None

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("""
# 🧠 ASSBI

AI Surveillance  
Business Intelligence  
Real-Time Monitoring
""")

menu = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "🏙 Location Management",
        "📍 Location Points",
        "📷 Camera Management",
        "🎥 Live Cameras",
        "📡 Telemetry",
        "🚨 Alerts",
        "🔍 Detections",
        "🤖 AI Chat"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("ASSBI • AI Surveillance + BI")

# =========================================================
# DASHBOARD
# =========================================================

if menu == "📊 Dashboard":

    cameras   = fetch("cameras")
    alerts    = fetch("alerts")
    telemetry = fetch("crowd-telemetry")

    active_cameras = len([
        c for c in cameras
        if c.get("status") == "active"
    ])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>📷 Cameras</div>
            <div class='metric-value'>{len(cameras)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>🟢 Active</div>
            <div class='metric-value'>{active_cameras}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>🚨 Alerts</div>
            <div class='metric-value'>{len(alerts)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>📡 Telemetry</div>
            <div class='metric-value'>{len(telemetry)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("## 📈 Crowd Analytics")

    telemetry_df = pd.DataFrame(telemetry)

    if not telemetry_df.empty:

        if "timestamp" in telemetry_df.columns:
            telemetry_df["timestamp"] = pd.to_datetime(
                telemetry_df["timestamp"],
                errors="coerce"
            )

        if "person_count" in telemetry_df.columns:
            fig = px.line(
                telemetry_df,
                x="timestamp" if "timestamp" in telemetry_df.columns else None,
                y="person_count",
                title="Person Count"
            )
            st.plotly_chart(fig, use_container_width=True)

        if "crowd_density_score" in telemetry_df.columns:
            fig = px.area(
                telemetry_df,
                x="timestamp" if "timestamp" in telemetry_df.columns else None,
                y="crowd_density_score",
                title="Crowd Density"
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("## 🚨 Recent Alerts")

    alerts_df = pd.DataFrame(alerts)

    if not alerts_df.empty:
        st.dataframe(alerts_df, use_container_width=True)
    else:
        st.info("No alerts available")

# =========================================================
# LOCATION MANAGEMENT
# =========================================================

elif menu == "🏙 Location Management":

    st.markdown("## 🏙 City Management")

    with st.form("city_form"):
        city_name = st.text_input("City Name")
        city_submit = st.form_submit_button("Add City")

    if city_submit:

        if not city_name.strip():
            st.warning("City name required")
        else:
            res = post_json("cities/", {"name": city_name})

            if res and res.status_code in [200, 201]:
                st.success("City added")
            elif res:
                st.error(res.text)

    st.markdown("---")
    st.markdown("## 🛣 Street Management")

    cities = fetch("cities")

    city_map = {
        c["name"]: c["city_id"]
        for c in cities
    } if cities else {}

    with st.form("street_form"):

        street_name = st.text_input("Street Name")

        selected_city = st.selectbox(
            "City",
            list(city_map.keys()) if city_map else []
        )

        street_submit = st.form_submit_button("Add Street")

    if street_submit:

        if not city_map:
            st.error("No cities found")
        else:

            payload = {
                "name": street_name,
                "city_id": city_map[selected_city]
            }

            res = post_json("streets/", payload)

            if res and res.status_code in [200, 201]:
                st.success("Street added")
            elif res:
                st.error(res.text)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏙 Cities")
        st.dataframe(
            pd.DataFrame(fetch("cities")),
            use_container_width=True
        )

    with col2:
        st.markdown("### 🛣 Streets")
        st.dataframe(
            pd.DataFrame(fetch("streets")),
            use_container_width=True
        )

# =========================================================
# LOCATION POINTS
# =========================================================

elif menu == "📍 Location Points":

    st.markdown("## 📍 Add Monitoring Location")

    streets = fetch("streets")

    street_map = {
        s["name"]: s["street_id"]
        for s in streets
    } if streets else {}

    with st.form("location_form"):

        location_name = st.text_input("Location Name")

        selected_street = st.selectbox(
            "Street",
            list(street_map.keys()) if street_map else []
        )

        latitude = st.number_input(
            "Latitude",
            value=41.3111,
            format="%.6f"
        )

        longitude = st.number_input(
            "Longitude",
            value=69.2797,
            format="%.6f"
        )

        submit_location = st.form_submit_button("Add Location")

    if submit_location:

        payload = {
            "name": location_name,
            "street_id": street_map.get(selected_street),
            "latitude": latitude,
            "longitude": longitude
        }

        res = post_json("locations/", payload)

        if res and res.status_code in [200, 201]:
            st.success("Location added")
        elif res:
            st.error(res.text)

    st.markdown("---")

    st.markdown("## 📍 Existing Locations")

    df = pd.DataFrame(fetch("locations"))

    if not df.empty:
        st.dataframe(df, use_container_width=True)

# =========================================================
# CAMERA MANAGEMENT
# =========================================================

elif menu == "📷 Camera Management":

    st.markdown("## 📷 Add New Camera")

    streets   = fetch("streets")
    locations = fetch("locations")

    street_options = {
        f"{s['name']} (ID:{s['street_id']})": s["street_id"]
        for s in streets
    } if streets else {}

    location_options = {
        f"{l['name']} (ID:{l['location_id']})": l["location_id"]
        for l in locations
    } if locations else {}

    with st.form("camera_form"):

        camera_name = st.text_input("Camera Name")

        selected_street = st.selectbox(
            "Street",
            list(street_options.keys()) if street_options else []
        )

        selected_location = st.selectbox(
            "Location",
            list(location_options.keys()) if location_options else []
        )

        status = st.selectbox(
            "Camera Status",
            ["active", "inactive", "maintenance"]
        )

        video_url = st.text_input(
            "Stream URL (RTSP / HTTP / YouTube)"
        )

        uploaded_video = st.file_uploader(
            "Upload MP4 Video",
            type=["mp4"]
        )

        submit = st.form_submit_button("Add Camera")

    if submit:

        data = {
            "camera_name": camera_name,
            "street_id": street_options.get(selected_street),
            "location_id": location_options.get(selected_location),
            "status": status,
            "video_url": video_url,
        }

        files = {}

        if uploaded_video:
            files["video_file"] = (
                uploaded_video.name,
                uploaded_video,
                "video/mp4"
            )

        try:

            r = requests.post(
                f"{API_URL}/cameras/",
                data=data,
                files=files,
                timeout=30
            )

            if r.status_code in [200, 201]:
                st.success("Camera added successfully")
            else:
                st.error(r.text)

        except Exception as e:
            st.error(str(e))

    st.markdown("---")
    st.markdown("## 📷 Existing Cameras")

    cameras = fetch("cameras")

    if not cameras:
        st.info("No cameras found")

    for cam in cameras:

        sc = {
            "active": "status-online",
            "inactive": "status-offline",
            "maintenance": "status-maintenance"
        }.get(cam.get("status"), "status-online")

        st.markdown(f"""
        <div class='card'>
            <h3>📷 {cam.get('camera_name', 'Unknown')}</h3>

            <p>
                <b>ID:</b> {cam.get('camera_id')}
                &nbsp;
                <b>Street:</b> {cam.get('street_id')}
                &nbsp;
                <b>Location:</b> {cam.get('location_id')}
            </p>

            <p class='{sc}'>
                ● {cam.get('status', 'unknown').upper()}
            </p>

            <p>
                <b>Source:</b>
                {cam.get('video_url') or cam.get('video_file', 'N/A')}
            </p>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# LIVE CAMERAS
# =========================================================

elif menu == "🎥 Live Cameras":

    st.markdown("## 🎥 Live Camera Monitoring")

    cameras = fetch("cameras")

    if not cameras:
        st.warning("No cameras found")
        st.stop()

    cam_map = {
        f"[{c['camera_id']}] {c['camera_name']}": c
        for c in cameras
    }

    selected_name = st.selectbox(
        "Select Camera",
        list(cam_map.keys())
    )

    cam = cam_map[selected_name]

    source = cam.get("video_url") or cam.get("video_file")

    st.markdown(
        f"""
        **Source:** `{source or 'not set'}`
        &nbsp;|&nbsp;
        **Status:** `{cam.get('status', '-')}`
        """
    )

    if not source:
        st.error("Camera source missing")
        st.stop()

    col_btn1, col_btn2, _ = st.columns([1, 1, 4])

    with col_btn1:
        start = st.button(
            "▶ Start",
            type="primary",
            use_container_width=True
        )

    with col_btn2:
        stop = st.button(
            "⏹ Stop",
            use_container_width=True
        )

    if "ws_running" not in st.session_state:
        st.session_state.ws_running = False

    if "ws_queue" not in st.session_state:
        st.session_state.ws_queue = None

    if "ws_thread" not in st.session_state:
        st.session_state.ws_thread = None

    if "ws_stop_flag" not in st.session_state:
        st.session_state.ws_stop_flag = threading.Event()

    def start_stream(camera_id):

        st.session_state.ws_stop_flag.clear()

        q = queue.Queue(maxsize=3)
        flag = st.session_state.ws_stop_flag

        def worker():

            try:

                ws = websocket.create_connection(
                    f"{WS_URL}/ws/stream/{camera_id}",
                    timeout=10
                )

                while not flag.is_set():

                    raw = ws.recv()
                    data = json.loads(raw)

                    if q.full():
                        try:
                            q.get_nowait()
                        except queue.Empty:
                            pass

                    q.put(data)

                ws.close()

            except Exception as e:
                q.put({"error": str(e)})

        t = threading.Thread(target=worker, daemon=True)
        t.start()

        st.session_state.ws_queue = q
        st.session_state.ws_thread = t
        st.session_state.ws_running = True

    if start:

        if st.session_state.ws_running:
            st.session_state.ws_stop_flag.set()
            time.sleep(0.3)

        start_stream(cam["camera_id"])

    if stop:
        st.session_state.ws_stop_flag.set()
        st.session_state.ws_running = False
        st.session_state.ws_queue = None

    if st.session_state.ws_running:

        col_video, col_stats = st.columns([3, 1])

        with col_video:
            frame_placeholder = st.empty()

        with col_stats:
            count_placeholder = st.empty()
            fps_placeholder = st.empty()

        for _ in range(25):

            q = st.session_state.ws_queue

            if q is None:
                break

            try:
                data = q.get(timeout=1)
            except queue.Empty:
                continue

            if "error" in data:
                st.error(data["error"])
                break

            try:

                img = Image.open(
                    BytesIO(base64.b64decode(data["frame"]))
                )

                frame_placeholder.image(
                    img,
                    use_container_width=True
                )

                count = data.get("person_count", 0)
                fps = data.get("fps", 0)

                count_placeholder.metric(
                    "People",
                    count
                )

                fps_placeholder.metric(
                    "FPS",
                    fps
                )

            except Exception as e:
                st.error(str(e))

            time.sleep(0.03)

        st.rerun()

    else:

        st.markdown("""
        <div style='
            background:rgba(17,25,40,0.7);
            border-radius:16px;
            padding:40px;
            border:1px dashed rgba(255,255,255,0.1);
            text-align:center;
            color:#6B7280;
        '>
            Press ▶ Start to begin monitoring
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# TELEMETRY
# =========================================================

elif menu == "📡 Telemetry":

    st.markdown("## 📡 Crowd Telemetry")

    df = pd.DataFrame(fetch("crowd-telemetry"))

    if not df.empty:

        st.dataframe(df, use_container_width=True)

        if "person_count" in df.columns:

            fig = px.histogram(
                df,
                x="person_count",
                title="Person Count Distribution"
            )

            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No telemetry data")

# =========================================================
# ALERTS
# =========================================================

elif menu == "🚨 Alerts":

    st.markdown("## 🚨 Security Alerts")

    df = pd.DataFrame(fetch("alerts"))

    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No alerts")

# =========================================================
# DETECTIONS
# =========================================================

elif menu == "🔍 Detections":

    st.markdown("## 🔍 Object Detections")

    df = pd.DataFrame(fetch("detected-objects"))

    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No detections")

# =========================================================
# AI CHAT
# =========================================================

elif menu == "🤖 AI Chat":

    st.markdown("## 🤖 AI Surveillance Assistant")

    if "history" not in st.session_state:
        st.session_state.history = []

    for chat in st.session_state.history:

        st.markdown(
            f"""
            <div class='chat-user'>
                <b>👤 You</b><br>
                {chat['user']}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class='chat-ai'>
                <b>🤖 ASSBI AI</b><br>
                {chat['bot']}
            </div>
            """,
            unsafe_allow_html=True
        )

    msg = st.text_input("Message")

    if st.button("Send") and msg:

        try:

            r = requests.post(
                f"{API_URL}/chatbot/",
                json={"message": msg},
                timeout=20
            )

            if r.status_code == 200:
                reply = r.json().get(
                    "response",
                    "No response"
                )
            else:
                reply = r.text

        except Exception:
            reply = "Backend connection error"

        st.session_state.history.append({
            "user": msg,
            "bot": reply
        })

        st.rerun()

