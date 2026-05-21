

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# ------------------------------------------------
# CONFIG
# ------------------------------------------------

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="ASSBI Smart Surveillance",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------
# AUTO REFRESH
# ------------------------------------------------

st_autorefresh(interval=5000, key="refresh")

# ------------------------------------------------
# CUSTOM CSS
# ------------------------------------------------

st.markdown("""
<style>

/* ------------------------------------------------ */
/* GLOBAL */
/* ------------------------------------------------ */

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0B1120;
    color: white;
}

/* ------------------------------------------------ */
/* MAIN TITLE */
/* ------------------------------------------------ */

.main-title {
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(90deg, #00E5FF, #4ADE80);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
}

/* ------------------------------------------------ */
/* CARDS */
/* ------------------------------------------------ */

.card {
    background: rgba(17, 25, 40, 0.75);
    border: 1px solid rgba(255,255,255,0.08);

    padding: 22px;
    border-radius: 20px;

    margin-bottom: 18px;

    box-shadow:
        0 8px 32px rgba(0,0,0,0.35);

    transition: 0.3s ease;
}

.card:hover {
    transform: translateY(-4px);
    border: 1px solid #00E5FF;
}

/* ------------------------------------------------ */
/* KPI */
/* ------------------------------------------------ */

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

/* ------------------------------------------------ */
/* STATUS */
/* ------------------------------------------------ */

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

/* ------------------------------------------------ */
/* SIDEBAR */
/* ------------------------------------------------ */

section[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid rgba(255,255,255,0.06);
}

/* ------------------------------------------------ */
/* BUTTON */
/* ------------------------------------------------ */

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

/* ------------------------------------------------ */
/* INPUTS */
/* ------------------------------------------------ */

.stTextInput input {
    border-radius: 12px !important;
}

.stSelectbox div[data-baseweb="select"] {
    border-radius: 12px !important;
}

/* ------------------------------------------------ */
/* CHAT */
/* ------------------------------------------------ */

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

/* ------------------------------------------------ */
/* TABLE */
/* ------------------------------------------------ */

[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
}

</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# HEADER
# ------------------------------------------------

st.markdown("""
<div class='main-title'>
🧠 ASSBI Smart Surveillance Platform
</div>
""", unsafe_allow_html=True)

st.caption(
    "AI-Powered Monitoring • Crowd Analytics • Real-Time Security Intelligence"
)

# ------------------------------------------------
# API HELPER
# ------------------------------------------------

@st.cache_data(ttl=5)
def fetch(endpoint):
    try:
        r = requests.get(f"{API_URL}/{endpoint}")

        if r.status_code == 200:
            return r.json()

        return []

    except:
        return []

# ------------------------------------------------
# SIDEBAR
# ------------------------------------------------

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

    cameras = fetch("cameras")
    alerts = fetch("alerts")
    telemetry = fetch("crowd-telemetry")

    col1, col2, col3 = st.columns(3)

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
            <div class='metric-title'>🚨 Alerts</div>
            <div class='metric-value'>{len(alerts)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>📡 Telemetry</div>
            <div class='metric-value'>{len(telemetry)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("## 📈 Crowd Analytics")

    telemetry_df = pd.DataFrame(telemetry)

    if not telemetry_df.empty:

        if "person_count" in telemetry_df.columns:

            fig = px.line(
                telemetry_df,
                y="person_count",
                title="Person Count"
            )

            st.plotly_chart(fig, use_container_width=True)

        if "crowd_density_score" in telemetry_df.columns:

            fig2 = px.line(
                telemetry_df,
                y="crowd_density_score",
                title="Crowd Density"
            )

            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("## 🚨 Recent Alerts")

    alerts_df = pd.DataFrame(alerts)

    if not alerts_df.empty:
        st.dataframe(alerts_df, use_container_width=True)

# =========================================================
# LOCATION MANAGEMENT
# =========================================================

elif menu == "🏙 Location Management":

    st.markdown("## 🏙 City Management")

    with st.form("city_form"):

        city_name = st.text_input("City Name")

        city_submit = st.form_submit_button("Add City")

    if city_submit:

        res = requests.post(
    f"{API_URL}/cities/",
    params={"name": city_name}
)

        if res.status_code == 200:
            st.success("City added successfully")
        else:
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

    if street_submit and city_map:

        res = requests.post(
    f"{API_URL}/streets/",
    params={
        "name": street_name,
        "city_id": city_map[selected_city]
    }
)

        if res.status_code == 200:
            st.success("Street added successfully")
        else:
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
# CAMERA MANAGEMENT
# =========================================================

elif menu == "📷 Camera Management":

    st.markdown("## 📷 Add New Camera")

    streets = fetch("streets")

    street_options = {
        f"{s['name']} (ID:{s['street_id']})": s["street_id"]
        for s in streets
    } if streets else {}

    locations = fetch("locations")

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

        video_url = st.text_input("Stream URL")

        uploaded_video = st.file_uploader(
            "Upload MP4 Video",
            type=["mp4"]
        )

        submit = st.form_submit_button("Add Camera")

    if submit:

        data = {
            "camera_name": camera_name,
            "street_id": street_options[selected_street],
            "location_id": location_options[selected_location],
            "status": status,
            "video_url": video_url
        }

        files = {}

        if uploaded_video:
            files["video_file"] = (
                uploaded_video.name,
                uploaded_video,
                "video/mp4"
            )

        try:

            response = requests.post(
                f"{API_URL}/cameras/",
                data=data,
                files=files
            )

            if response.status_code == 200:
                st.success("Camera added successfully")
            else:
                st.error(response.text)

        except Exception as e:
            st.error(str(e))

    st.markdown("---")
    st.markdown("## 📷 Existing Cameras")

    cameras = fetch("cameras")

    for cam in cameras:

        status_class = {
            "active": "status-online",
            "inactive": "status-offline",
            "maintenance": "status-maintenance"
        }.get(cam["status"], "status-online")

        st.markdown(f"""
        <div class='card'>

            <h3>📷 {cam['camera_name']}</h3>

            <p>
            <b>ID:</b> {cam['camera_id']}<br>
            <b>Street:</b> {cam['street_id']}<br>
            <b>Location:</b> {cam['location_id']}
            </p>

            <p class='{status_class}'>
            ● {cam['status'].upper()}
            </p>

        </div>
        """, unsafe_allow_html=True)

# =========================================================
# LIVE CAMERAS
# =========================================================

elif menu == "🎥 Live Cameras":

    st.markdown("## 🎥 Live Camera Monitoring")

    cameras = fetch("cameras")

    cols = st.columns(2)

    for i, cam in enumerate(cameras):

        with cols[i % 2]:

            st.markdown(f"""
            <div class='card'>
            <h3>📷 {cam['camera_name']}</h3>
            </div>
            """, unsafe_allow_html=True)

            if cam.get("video_url"):
                st.video(cam["video_url"])
            else:
                st.warning("No stream available")

# =========================================================
# TELEMETRY
# =========================================================

elif menu == "📡 Telemetry":

    st.markdown("## 📡 Crowd Telemetry")

    telemetry = fetch("crowd-telemetry")

    df = pd.DataFrame(telemetry)

    if not df.empty:
        st.dataframe(df, use_container_width=True)

# =========================================================
# ALERTS
# =========================================================

elif menu == "🚨 Alerts":

    st.markdown("## 🚨 Security Alerts")

    alerts = fetch("alerts")

    df = pd.DataFrame(alerts)

    if not df.empty:
        st.dataframe(df, use_container_width=True)

# =========================================================
# DETECTIONS
# =========================================================

elif menu == "🔍 Detections":

    st.markdown("## 🔍 Object Detections")

    detections = fetch("detected-objects")

    df = pd.DataFrame(detections)

    if not df.empty:
        st.dataframe(df, use_container_width=True)

# =========================================================
# AI CHAT
# =========================================================

elif menu == "🤖 AI Chat":

    st.markdown("## 🤖 AI Surveillance Assistant")

    if "history" not in st.session_state:
        st.session_state.history = []

    for chat in st.session_state.history:

        st.markdown(f"""
        <div class='chat-user'>
            <b>👤 You</b><br>
            {chat['user']}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='chat-ai'>
            <b>🤖 ASSBI AI</b><br>
            {chat['bot']}
        </div>
        """, unsafe_allow_html=True)

    msg = st.text_input("Message")

    if st.button("Send") and msg:

        try:

            response = requests.post(
                f"{API_URL}/chatbot/",
                json={"message": msg}
            )

            reply = response.json().get(
                "response",
                "No response"
            )

        except:
            reply = "Backend connection error"

        st.session_state.history.append({
            "user": msg,
            "bot": reply
        })

        st.rerun()