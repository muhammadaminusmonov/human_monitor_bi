# streamlit_app.py
# AI Surveillance + BI Dashboard (ASSBI Frontend - FULL VERSION WITH LIVE CAMERA)

import streamlit as st
import requests
import pandas as pd
import time
import cv2
from PIL import Image
import numpy as np

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="ASSBI Smart Surveillance",
    layout="wide",
    page_icon="🧠"
)

# -----------------------
# UI STYLE
# -----------------------
st.markdown("""
<style>
.big-font {font-size:28px; font-weight:700;}
.chat-box {background:#0f172a; padding:10px; border-radius:10px; margin:5px 0;}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='big-font'>🧠 ASSBI Smart Surveillance & BI Platform</div>", unsafe_allow_html=True)

# -----------------------
# API
# -----------------------
@st.cache_data(ttl=5)
def fetch(endpoint):
    try:
        r = requests.get(f"{API_URL}/{endpoint}")
        return r.json() if r.status_code == 200 else []
    except:
        return []

# -----------------------
# MENU
# -----------------------
menu = st.sidebar.radio("Navigation", [
    "📊 Dashboard",
    "🏙️ Cities",
    "📷 Cameras",
    "🎥 Live Camera",
    "📡 Telemetry",
    "🚨 Alerts",
    "🔍 Detections",
    "🤖 AI Chat"
])

st.sidebar.info("ASSBI AI Surveillance System")

# -----------------------
# DASHBOARD
# -----------------------
if menu == "📊 Dashboard":
    cameras = fetch("cameras")
    alerts = fetch("alerts")
    telemetry = fetch("crowd-telemetry")

    col1, col2, col3 = st.columns(3)
    col1.metric("Cameras", len(cameras))
    col2.metric("Alerts", len(alerts))
    col3.metric("Telemetry", len(telemetry))

    st.subheader("Recent Alerts")
    st.dataframe(pd.DataFrame(alerts[-10:]), use_container_width=True)

# -----------------------
# LIVE CAMERA STREAM
# -----------------------
elif menu == "🎥 Live Camera":

    st.subheader("📡 Live CCTV Feed")

    camera_url = st.text_input("Enter Camera Stream URL (or backend stream endpoint)", "http://localhost:8000/video-feed")

    frame_window = st.image([])

    cap = None

    try:
        cap = cv2.VideoCapture(camera_url)
    except:
        st.error("Cannot open stream")

    run = st.checkbox("Start Live Stream")

    while run:
        if cap is None:
            st.error("Camera not available")
            break

        ret, frame = cap.read()

        if not ret:
            st.warning("No frame received")
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_window.image(frame)

        time.sleep(0.03)

# -----------------------
# OTHER MODULES
# -----------------------
elif menu == "🏙️ Cities":
    st.dataframe(fetch("cities"))

elif menu == "📷 Cameras":
    st.dataframe(fetch("cameras"))

elif menu == "📡 Telemetry":
    df = pd.DataFrame(fetch("crowd-telemetry"))
    st.dataframe(df)
    if not df.empty:
        st.line_chart(df[["person_count", "crowd_density_score"]])

elif menu == "🚨 Alerts":
    st.dataframe(fetch("alerts"))

elif menu == "🔍 Detections":
    st.dataframe(fetch("detected-objects"))

# -----------------------
# AI CHAT
# -----------------------
elif menu == "🤖 AI Chat":

    st.subheader("Talk with AI")

    if "history" not in st.session_state:
        st.session_state.history = []

    for h in st.session_state.history:
        st.markdown(f"**You:** {h['user']}")
        st.markdown(f"**AI:** {h['bot']}")

    msg = st.text_input("Message")

    if st.button("Send") and msg:
        try:
            r = requests.post(f"{API_URL}/chatbot/", json={"message": msg})
            reply = r.json().get("response", "No response")
        except:
            reply = "Error connecting to backend"

        st.session_state.history.append({"user": msg, "bot": reply})
        st.rerun()

# -----------------------
# FOOTER
# -----------------------
st.sidebar.markdown("---")
st.sidebar.caption("ASSBI • AI Surveillance + BI")