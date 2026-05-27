import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import datetime
import os

# ─────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# ─────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────

st.set_page_config(
    page_title="ASSBI · Surveillance Ops",
    layout="wide",
    page_icon="⬡",
    initial_sidebar_state="expanded"
)

st_autorefresh(interval=5000, key="refresh")

# ─────────────────────────────────────────────────────────
# DESIGN SYSTEM — Premium Business Intelligence
# Aesthetic: Refined dark · Geist + DM Serif · Zinc palette
# ─────────────────────────────────────────────────────────

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&family=DM+Mono:wght@300;400;500&family=DM+Serif+Display:ital@0;1&display=swap" rel="stylesheet">

<style>

:root {
  --bg:          #0c0c0e;
  --surface:     #111115;
  --surface-2:   #18181d;
  --surface-3:   #1e1e25;
  --border:      rgba(255,255,255,0.06);
  --border-2:    rgba(255,255,255,0.10);
  --border-3:    rgba(255,255,255,0.16);
  --text-1:      #fafafa;
  --text-2:      #a1a1aa;
  --text-3:      #52525b;
  --accent:      #6ee7b7;
  --accent-2:    #34d399;
  --accent-dim:  rgba(110,231,183,0.08);
  --accent-glow: rgba(110,231,183,0.15);
  --blue:        #93c5fd;
  --blue-dim:    rgba(147,197,253,0.08);
  --amber:       #fbbf24;
  --amber-dim:   rgba(251,191,36,0.08);
  --red:         #f87171;
  --red-dim:     rgba(248,113,113,0.08);
  --radius:      10px;
  --radius-lg:   14px;
  --radius-xl:   18px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
  font-family: 'DM Sans', sans-serif !important;
  background: var(--bg) !important;
  color: var(--text-1) !important;
  -webkit-font-smoothing: antialiased;
}

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-2); border-radius: 2px; }

/* ════════════════════════════════════════
   SIDEBAR
════════════════════════════════════════ */
section[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
  min-width: 240px !important;
  max-width: 240px !important;
  padding-top: 0 !important;
}
section[data-testid="stSidebar"] > div {
  background: var(--surface) !important;
  padding-top: 0 !important;
}

.sb-top {
  padding: 28px 20px 20px;
  border-bottom: 1px solid var(--border);
}
.sb-logo {
  display: flex;
  align-items: center;
  gap: 11px;
  margin-bottom: 6px;
}
.sb-logo-icon {
  width: 34px;
  height: 34px;
  background: linear-gradient(135deg, var(--accent) 0%, #10b981 100%);
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  color: #052e16;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: 0 0 20px var(--accent-glow);
}
.sb-logo-text {
  font-family: 'DM Serif Display', serif;
  font-size: 19px;
  color: var(--text-1);
  letter-spacing: -0.01em;
  line-height: 1;
}
.sb-logo-sub {
  font-size: 10px;
  color: var(--text-3);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  font-weight: 400;
}
.sb-pulse {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-top: 14px;
  padding: 7px 12px;
  background: rgba(110,231,183,0.06);
  border: 1px solid rgba(110,231,183,0.15);
  border-radius: 8px;
}
.sb-pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
  animation: pulse 2s ease-in-out infinite;
  flex-shrink: 0;
}
@keyframes pulse {
  0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(110,231,183,0.4); }
  50% { opacity: 0.7; box-shadow: 0 0 0 4px rgba(110,231,183,0); }
}
.sb-pulse-text {
  font-size: 10.5px;
  color: var(--accent);
  font-weight: 500;
  letter-spacing: 0.02em;
}

.sb-nav-label {
  font-size: 9px;
  font-weight: 600;
  color: var(--text-3);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  padding: 20px 20px 6px;
}
.sb-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--border);
  margin-top: 8px;
}
.sb-endpoint {
  font-family: 'DM Mono', monospace;
  font-size: 9px;
  color: var(--text-3);
  word-break: break-all;
}

section[data-testid="stSidebar"] .stRadio > label { display: none !important; }
section[data-testid="stSidebar"] .stRadio input[type="radio"] { display: none !important; }
section[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child { display: none !important; }
section[data-testid="stSidebar"] .stRadio svg { display: none !important; }

section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
  display: flex;
  flex-direction: column;
  gap: 1px;
  padding: 4px 12px;
}
section[data-testid="stSidebar"] .stRadio label {
  font-family: 'DM Sans', sans-serif !important;
  font-size: 13.5px !important;
  font-weight: 400 !important;
  letter-spacing: -0.01em !important;
  text-transform: none !important;
  color: var(--text-2) !important;
  padding: 9px 12px !important;
  border-radius: 8px !important;
  margin: 0 !important;
  border: none !important;
  cursor: pointer !important;
  display: flex !important;
  align-items: center !important;
  transition: color 0.12s, background 0.12s !important;
}
section[data-testid="stSidebar"] .stRadio label:hover {
  color: var(--text-1) !important;
  background: var(--surface-2) !important;
}
section[data-testid="stSidebar"] .stRadio [aria-checked="true"] label,
section[data-testid="stSidebar"] .stRadio label:has(+ [aria-checked="true"]) {
  color: var(--accent) !important;
  background: var(--accent-dim) !important;
  font-weight: 500 !important;
}

/* ════════════════════════════════════════
   TOP BAR
════════════════════════════════════════ */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 2px 22px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 28px;
}
.topbar-left { display: flex; flex-direction: column; gap: 2px; }
.topbar-page {
  font-family: 'DM Serif Display', serif;
  font-size: 22px;
  color: var(--text-1);
  letter-spacing: -0.02em;
  line-height: 1;
}
.topbar-desc {
  font-size: 12px;
  color: var(--text-3);
  font-weight: 300;
}
.topbar-right { display: flex; align-items: center; gap: 10px; }
.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.01em;
  border: 1px solid var(--border-2);
  background: var(--surface-2);
  color: var(--text-2);
  font-family: 'DM Mono', monospace;
}
.chip-live {
  background: rgba(110,231,183,0.07);
  border-color: rgba(110,231,183,0.2);
  color: var(--accent);
}
.chip-live::before {
  content: '';
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent);
  animation: pulse 2s ease-in-out infinite;
}

/* ════════════════════════════════════════
   KPI CARDS
════════════════════════════════════════ */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 28px;
}
.kpi {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 22px 22px 20px;
  position: relative;
  overflow: hidden;
  transition: border-color 0.2s;
}
.kpi:hover { border-color: var(--border-2); }
.kpi-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}
.kpi-icon {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  border: 1px solid var(--border-2);
  background: var(--surface-2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}
.kpi-badge {
  font-size: 10px;
  font-weight: 500;
  padding: 3px 8px;
  border-radius: 6px;
  font-family: 'DM Mono', monospace;
}
.kpi-badge-green { background: rgba(110,231,183,0.1); color: var(--accent); border: 1px solid rgba(110,231,183,0.2); }
.kpi-badge-blue  { background: var(--blue-dim); color: var(--blue); border: 1px solid rgba(147,197,253,0.2); }
.kpi-badge-amber { background: var(--amber-dim); color: var(--amber); border: 1px solid rgba(251,191,36,0.2); }

.kpi-num {
  font-family: 'DM Serif Display', serif;
  font-size: 40px;
  color: var(--text-1);
  line-height: 1;
  letter-spacing: -0.02em;
  margin-bottom: 5px;
}
.kpi-label {
  font-size: 12px;
  color: var(--text-3);
  font-weight: 400;
}
.kpi-glow {
  position: absolute;
  bottom: -20px;
  right: -20px;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  opacity: 0.04;
  filter: blur(20px);
}

/* ════════════════════════════════════════
   SECTION HEADERS
════════════════════════════════════════ */
.sec {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 32px 0 14px;
}
.sec-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-3);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  white-space: nowrap;
}
.sec-line {
  flex: 1;
  height: 1px;
  background: var(--border);
}

/* ════════════════════════════════════════
   CARDS (generic)
════════════════════════════════════════ */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px 22px;
}

/* ════════════════════════════════════════
   STATUS PILLS
════════════════════════════════════════ */
.pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 10.5px;
  font-weight: 500;
  letter-spacing: 0.02em;
}
.pill::before { content: '●'; font-size: 5px; }
.pill-active   { color: var(--accent);  background: rgba(110,231,183,0.08); border: 1px solid rgba(110,231,183,0.18); }
.pill-inactive { color: var(--red);     background: var(--red-dim);          border: 1px solid rgba(248,113,113,0.18); }
.pill-maint    { color: var(--amber);   background: var(--amber-dim);        border: 1px solid rgba(251,191,36,0.18); }

/* ════════════════════════════════════════
   CAMERA ROWS
════════════════════════════════════════ */
.cam-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  margin-bottom: 8px;
  transition: border-color 0.15s, background 0.15s;
}
.cam-row:hover {
  border-color: var(--border-2);
  background: var(--surface-2);
}
.cam-thumb {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--surface-3);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}
.cam-name {
  font-size: 13.5px;
  font-weight: 500;
  color: var(--text-1);
  margin-bottom: 2px;
}
.cam-meta {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  color: var(--text-3);
  letter-spacing: 0.02em;
}

/* ════════════════════════════════════════
   FORM ELEMENTS
════════════════════════════════════════ */
.stTextInput input,
.stNumberInput input {
  background: var(--surface-2) !important;
  border: 1px solid var(--border-2) !important;
  border-radius: 9px !important;
  color: var(--text-1) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 13.5px !important;
  padding: 10px 14px !important;
  transition: border-color 0.15s, box-shadow 0.15s !important;
}
.stTextInput input:focus,
.stNumberInput input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--accent-dim) !important;
  outline: none !important;
}
.stTextInput input::placeholder { color: var(--text-3) !important; }

.stTextInput label,
.stNumberInput label,
.stSelectbox label,
.stFileUploader label {
  font-family: 'DM Sans', sans-serif !important;
  font-size: 11px !important;
  font-weight: 500 !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
  color: var(--text-3) !important;
}

.stSelectbox > div > div {
  background: var(--surface-2) !important;
  border: 1px solid var(--border-2) !important;
  border-radius: 9px !important;
  color: var(--text-1) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 13.5px !important;
}

/* ════════════════════════════════════════
   BUTTONS
════════════════════════════════════════ */
.stButton > button {
  background: var(--surface-2) !important;
  border: 1px solid var(--border-2) !important;
  color: var(--text-2) !important;
  border-radius: 9px !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  padding: 9px 18px !important;
  width: auto !important;
  transition: background 0.15s, border-color 0.15s, color 0.15s !important;
}
.stButton > button:hover {
  background: var(--surface-3) !important;
  border-color: var(--border-3) !important;
  color: var(--text-1) !important;
}
.stButton > button:focus {
  box-shadow: 0 0 0 3px var(--accent-dim) !important;
  outline: none !important;
}
div[data-testid="stButton"] button[kind="primary"],
.stButton > button[kind="primary"] {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
  color: #052e16 !important;
  font-weight: 600 !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover,
.stButton > button[kind="primary"]:hover {
  background: var(--accent-2) !important;
  border-color: var(--accent-2) !important;
  box-shadow: 0 0 20px var(--accent-glow) !important;
}

/* ════════════════════════════════════════
   DATA TABLE
════════════════════════════════════════ */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-lg) !important;
  background: var(--surface) !important;
  overflow: hidden !important;
}
[data-testid="stDataFrame"] th {
  background: var(--surface-2) !important;
  color: var(--text-3) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 10px !important;
  font-weight: 600 !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  border-bottom: 1px solid var(--border) !important;
}
[data-testid="stDataFrame"] td {
  background: var(--surface) !important;
  color: var(--text-2) !important;
  font-family: 'DM Mono', monospace !important;
  font-size: 12px !important;
  border-bottom: 1px solid var(--border) !important;
}

/* ════════════════════════════════════════
   ALERTS
════════════════════════════════════════ */
.stAlert {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-left: 2px solid var(--accent) !important;
  border-radius: var(--radius) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 12.5px !important;
  color: var(--text-2) !important;
}

/* ════════════════════════════════════════
   EXPANDERS
════════════════════════════════════════ */
[data-testid="stExpander"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
}
[data-testid="stExpander"] summary {
  font-family: 'DM Sans', sans-serif !important;
  font-size: 13px !important;
  color: var(--text-2) !important;
}

/* ════════════════════════════════════════
   METRIC
════════════════════════════════════════ */
[data-testid="stMetric"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 16px 18px !important;
}
[data-testid="stMetricLabel"] {
  font-family: 'DM Sans', sans-serif !important;
  font-size: 10px !important;
  font-weight: 600 !important;
  letter-spacing: 0.08em !important;
  color: var(--text-3) !important;
  text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
  font-family: 'DM Serif Display', serif !important;
  font-size: 30px !important;
  color: var(--text-1) !important;
}

/* ════════════════════════════════════════
   VIDEO PLACEHOLDER
════════════════════════════════════════ */
.vid-ph {
  background: var(--surface);
  border: 1px dashed var(--border-2);
  border-radius: var(--radius-lg);
  padding: 80px 40px;
  text-align: center;
  color: var(--text-3);
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.vid-icon { font-size: 32px; margin-bottom: 14px; opacity: 0.15; }

/* ════════════════════════════════════════
   MISC
════════════════════════════════════════ */
.stCaption {
  font-family: 'DM Mono', monospace !important;
  font-size: 9.5px !important;
  color: var(--text-3) !important;
  letter-spacing: 0.05em !important;
}

hr {
  border: none !important;
  border-top: 1px solid var(--border) !important;
  margin: 20px 0 !important;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# PLOTLY THEME
# ─────────────────────────────────────────────────────────

PLOT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#111115",
    font=dict(family="DM Sans, sans-serif", color="#52525b", size=10),
    margin=dict(l=8, r=8, t=36, b=8),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.06)", zeroline=False, tickfont=dict(color="#52525b")),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.06)", zeroline=False, tickfont=dict(color="#52525b")),
    title_font=dict(family="DM Sans, sans-serif", size=12, color="#71717a"),
)

# ─────────────────────────────────────────────────────────
# API HELPERS
# ─────────────────────────────────────────────────────────

def fetch(endpoint):
    """GET request — returns list or dict."""
    try:
        url = f"{API_URL}/{endpoint.strip('/')}/"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
        st.warning(f"[{r.status_code}] {url}")
        return []
    except Exception as e:
        st.error(f"Backend offline: {e}")
        return []


def post_query(endpoint, params: dict):
    """POST with query params (cities, streets)."""
    try:
        url = f"{API_URL}/{endpoint.strip('/')}/"
        r = requests.post(url, params=params, timeout=10)
        return r
    except Exception as e:
        st.error(f"POST error: {e}")
        return None


def post_form(endpoint, data: dict, files=None):
    """POST with form data (locations, cameras)."""
    try:
        url = f"{API_URL}/{endpoint.strip('/')}/"
        r = requests.post(url, data=data, files=files, timeout=30)
        return r
    except Exception as e:
        st.error(f"POST error: {e}")
        return None


# ─────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div class="sb-top">
        <div class="sb-logo">
            <div class="sb-logo-icon">⬡</div>
            <div>
                <div class="sb-logo-text">ASSBI</div>
            </div>
        </div>
        <div class="sb-logo-sub">Surveillance Intelligence</div>
        <div class="sb-pulse">
            <div class="sb-pulse-dot"></div>
            <span class="sb-pulse-text">All systems operational</span>
        </div>
    </div>
    <div class="sb-nav-label">Navigation</div>
    """, unsafe_allow_html=True)

    menu = st.radio(
        "nav",
        ["Dashboard", "Locations", "Points", "Cameras", "Live Feed"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="sb-nav-label" style="margin-top:12px;">Tools</div>', unsafe_allow_html=True)

    with st.expander("Backend Probe"):
        if st.button("Ping API"):
            try:
                r = requests.get(f"{API_URL}/cameras/", timeout=5)
                st.success(f"HTTP {r.status_code}")
                try:
                    st.json(r.json())
                except Exception:
                    st.text(r.text)
            except Exception as e:
                st.error(str(e))

    st.markdown(f"""
    <div class="sb-footer">
        <div class="sb-endpoint">{API_URL}</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# PAGE HEADER HELPER
# ─────────────────────────────────────────────────────────

ts = datetime.datetime.now().strftime("%b %d, %Y  %H:%M")

PAGE_META = {
    "Dashboard": ("Dashboard",  "Real-time surveillance overview"),
    "Locations": ("Locations",  "Manage cities and street registry"),
    "Points":    ("Points",     "Configure monitoring points"),
    "Cameras":   ("Cameras",    "Deploy and manage camera fleet"),
    "Live Feed": ("Live Feed",  "YOLO-annotated vehicle detection stream"),
}

title, desc = PAGE_META.get(menu, ("ASSBI", ""))

st.markdown(f"""
<div class="topbar">
    <div class="topbar-left">
        <div class="topbar-page">{title}</div>
        <div class="topbar-desc">{desc}</div>
    </div>
    <div class="topbar-right">
        <div class="chip">{ts}</div>
        <div class="chip chip-live">Live</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────

if menu == "Dashboard":

    cameras   = fetch("cameras")
    locations = fetch("locations")
    streets   = fetch("streets")
    cities    = fetch("cities")

    active_c  = len([c for c in cameras if c.get("status") == "active"])
    inactive_c = len([c for c in cameras if c.get("status") == "inactive"])

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi">
            <div class="kpi-top">
                <div class="kpi-icon">◎</div>
                <span class="kpi-badge kpi-badge-blue">Fleet</span>
            </div>
            <div class="kpi-num">{len(cameras)}</div>
            <div class="kpi-label">Total cameras deployed</div>
            <div class="kpi-glow" style="background:#93c5fd;"></div>
        </div>
        <div class="kpi">
            <div class="kpi-top">
                <div class="kpi-icon">●</div>
                <span class="kpi-badge kpi-badge-green">Online</span>
            </div>
            <div class="kpi-num">{active_c}</div>
            <div class="kpi-label">Active feeds</div>
            <div class="kpi-glow" style="background:#6ee7b7;"></div>
        </div>
        <div class="kpi">
            <div class="kpi-top">
                <div class="kpi-icon">⬡</div>
                <span class="kpi-badge kpi-badge-amber">Network</span>
            </div>
            <div class="kpi-num">{len(cities)}</div>
            <div class="kpi-label">Cities monitored</div>
            <div class="kpi-glow" style="background:#fbbf24;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Charts ──
    if cameras:
        st.markdown('<div class="sec"><div class="sec-title">Fleet analytics</div><div class="sec-line"></div></div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)

        with c1:
            status_counts = {}
            for cam in cameras:
                s = cam.get("status", "unknown")
                status_counts[s] = status_counts.get(s, 0) + 1

            fig = go.Figure(go.Bar(
                x=list(status_counts.keys()),
                y=list(status_counts.values()),
                marker_color=["#6ee7b7" if k == "active" else "#f87171" if k == "inactive" else "#fbbf24"
                              for k in status_counts.keys()],
                marker_line_color="#0c0c0e",
                marker_line_width=1,
            ))
            fig.update_layout(title="Camera status breakdown", **PLOT)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            loc_map = {l["location_id"]: l["name"] for l in locations} if locations else {}
            loc_counts = {}
            for cam in cameras:
                lid = cam.get("location_id")
                label = loc_map.get(lid, f"Loc {lid}")
                loc_counts[label] = loc_counts.get(label, 0) + 1

            if loc_counts:
                fig2 = go.Figure(go.Bar(
                    x=list(loc_counts.keys()),
                    y=list(loc_counts.values()),
                    marker_color="#93c5fd",
                    marker_line_color="#0c0c0e",
                    marker_line_width=1,
                ))
                fig2.update_layout(title="Cameras per location", **PLOT)
                st.plotly_chart(fig2, use_container_width=True)

    # ── Quick stats row ──
    st.markdown('<div class="sec"><div class="sec-title">Infrastructure</div><div class="sec-line"></div></div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Cities",    len(cities))
    m2.metric("Streets",   len(streets))
    m3.metric("Locations", len(locations))
    m4.metric("Inactive",  inactive_c)

# ─────────────────────────────────────────────────────────
# LOCATIONS  (cities + streets)
# ─────────────────────────────────────────────────────────

elif menu == "Locations":

    st.markdown('<div class="sec"><div class="sec-title">Register city</div><div class="sec-line"></div></div>', unsafe_allow_html=True)

    with st.form("city_form", clear_on_submit=True):
        city_name = st.text_input("City name")
        submitted = st.form_submit_button("Add City", type="primary")
        if submitted:
            if not city_name.strip():
                st.warning("City name is required.")
            else:
                res = post_query("cities", {"name": city_name.strip()})
                if res and res.status_code in [200, 201]:
                    st.success(f"'{city_name}' registered.")
                    st.rerun()
                elif res:
                    st.error(f"[{res.status_code}] {res.text}")

    st.markdown('<div class="sec"><div class="sec-title">Register street</div><div class="sec-line"></div></div>', unsafe_allow_html=True)

    cities   = fetch("cities")
    city_map = {c["name"]: c["city_id"] for c in cities} if cities else {}

    if not city_map:
        st.warning("No cities yet — register one above first.")
    else:
        with st.form("street_form", clear_on_submit=True):
            street_name   = st.text_input("Street name")
            selected_city = st.selectbox("City", list(city_map.keys()))
            submitted = st.form_submit_button("Add Street", type="primary")
            if submitted:
                if not street_name.strip():
                    st.warning("Street name is required.")
                else:
                    res = post_query("streets", {
                        "name":    street_name.strip(),
                        "city_id": city_map[selected_city]
                    })
                    if res and res.status_code in [200, 201]:
                        st.success(f"'{street_name}' registered.")
                        st.rerun()
                    elif res:
                        st.error(f"[{res.status_code}] {res.text}")

    st.markdown('<div class="sec"><div class="sec-title">Directory</div><div class="sec-line"></div></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.caption("CITIES")
        st.dataframe(pd.DataFrame(fetch("cities")), use_container_width=True, hide_index=True)
    with c2:
        st.caption("STREETS")
        st.dataframe(pd.DataFrame(fetch("streets")), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────
# POINTS  (locations)
# ─────────────────────────────────────────────────────────

elif menu == "Points":

    st.markdown('<div class="sec"><div class="sec-title">Add monitoring point</div><div class="sec-line"></div></div>', unsafe_allow_html=True)

    streets    = fetch("streets")
    street_map = {s["name"]: s["street_id"] for s in streets} if streets else {}

    if not street_map:
        st.warning("No streets found — add streets first in Locations.")
    else:
        with st.form("loc_form", clear_on_submit=True):
            loc_name   = st.text_input("Point name")
            sel_street = st.selectbox("Street", list(street_map.keys()))
            submitted  = st.form_submit_button("Add Point", type="primary")
            if submitted:
                if not loc_name.strip():
                    st.warning("Name required.")
                else:
                    res = post_form("locations", {
                        "name":      loc_name.strip(),
                        "street_id": street_map[sel_street],
                    })
                    if res and res.status_code in [200, 201]:
                        st.success(f"'{loc_name}' added.")
                        st.rerun()
                    elif res:
                        st.error(f"[{res.status_code}] {res.text}")

    st.markdown('<div class="sec"><div class="sec-title">All points</div><div class="sec-line"></div></div>', unsafe_allow_html=True)

    locations = fetch("locations")
    if not locations:
        st.info("No monitoring points on record.")
    else:
        df = pd.DataFrame(locations)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown('<div class="sec"><div class="sec-title">Remove point</div><div class="sec-line"></div></div>', unsafe_allow_html=True)
        loc_del_map = {f"{l['name']} (ID:{l['location_id']})": l["location_id"] for l in locations}
        sel_del = st.selectbox("Select point to delete", list(loc_del_map.keys()), key="del_loc")
        if st.button("Delete Point", key="del_loc_btn"):
            try:
                r = requests.delete(f"{API_URL}/locations/{loc_del_map[sel_del]}/", timeout=5)
                if r.status_code in [200, 204]:
                    st.success("Point removed.")
                    st.rerun()
                else:
                    st.error(f"[{r.status_code}] {r.text}")
            except Exception as e:
                st.error(str(e))

# ─────────────────────────────────────────────────────────
# CAMERAS
# ─────────────────────────────────────────────────────────

elif menu == "Cameras":

    st.markdown('<div class="sec"><div class="sec-title">Deploy camera</div><div class="sec-line"></div></div>', unsafe_allow_html=True)

    locations = fetch("locations")
    l_opts    = {f"{l['name']} (ID:{l['location_id']})": l["location_id"] for l in locations} if locations else {}

    if not l_opts:
        st.warning("No locations — add monitoring points first.")
    else:
        with st.form("cam_form", clear_on_submit=True):
            cam_name  = st.text_input("Camera name")
            sel_loc   = st.selectbox("Location", list(l_opts.keys()))
            c1, c2    = st.columns(2)
            with c1:
                status = st.selectbox("Status", ["active", "inactive", "maintenance"])
            with c2:
                video_url = st.text_input("Stream URL (RTSP / HTTP / YouTube)")
            uploaded  = st.file_uploader("Upload MP4 (optional)", type=["mp4"])
            submitted = st.form_submit_button("Deploy Camera", type="primary")

            if submitted:
                if not cam_name.strip():
                    st.warning("Camera name required.")
                else:
                    form_data = {
                        "camera_name": cam_name.strip(),
                        "location_id": l_opts[sel_loc],
                        "status":      status,
                        "video_url":   video_url or "",
                    }
                    files = None
                    if uploaded:
                        files = {"video_file": (uploaded.name, uploaded.read(), "video/mp4")}

                    res = post_form("cameras", form_data, files=files)
                    if res and res.status_code in [200, 201]:
                        st.success("Camera deployed.")
                        st.rerun()
                    elif res:
                        st.error(f"[{res.status_code}] {res.text}")

    st.markdown('<div class="sec"><div class="sec-title">Camera fleet</div><div class="sec-line"></div></div>', unsafe_allow_html=True)

    cameras = fetch("cameras")
    if not cameras:
        st.info("No cameras deployed.")
    else:
        for cam in cameras:
            s  = cam.get("status", "unknown")
            pc = {"active": "pill-active", "inactive": "pill-inactive", "maintenance": "pill-maint"}.get(s, "pill-maint")
            src = cam.get("video_url") or cam.get("video_file") or "—"
            st.markdown(f"""
            <div class="cam-row">
                <div class="cam-thumb">◎</div>
                <div style="flex:1; min-width:0;">
                    <div class="cam-name">{cam.get('camera_name', 'Unknown')}</div>
                    <div class="cam-meta">cam·{cam.get('camera_id','—')} &nbsp;/&nbsp; loc·{cam.get('location_id','—')} &nbsp;/&nbsp; {src}</div>
                </div>
                <span class="pill {pc}">{s}</span>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# LIVE FEED
# ── FIXED: uses WebSocket /ws/stream/{id} instead of
#    plain MJPEG so YOLO-annotated frames + vehicle counts
#    are received and displayed correctly.
# ─────────────────────────────────────────────────────────

elif menu == "Live Feed":

    cameras = fetch("cameras")
    if not cameras:
        st.warning("No cameras deployed.")
        st.stop()

    cam_map  = {f"CAM·{c['camera_id']}  {c.get('camera_name', '')}": c for c in cameras}
    sel_name = st.selectbox("Select camera", list(cam_map.keys()))
    cam      = cam_map[sel_name]
    cam_id   = cam["camera_id"]
    source   = cam.get("video_url") or cam.get("video_file")

    st.caption(
        f"source: {source or 'not configured'}   ·   "
        f"status: {cam.get('status','—')}   ·   "
        f"location_id: {cam.get('location_id','—')}"
    )

    if not source:
        st.error("Camera source not configured — set a URL or upload an MP4 in the Cameras page.")
        st.stop()

    # Derive WebSocket base URL from the HTTP API_URL
    ws_base = API_URL.replace("https://", "wss://").replace("http://", "ws://")
    ws_url  = f"{ws_base}/ws/stream/{cam_id}"

    col_b1, col_b2, _ = st.columns([1, 1, 5])
    with col_b1:
        show = st.button("▶ Show Stream", type="primary", use_container_width=True)
    with col_b2:
        hide = st.button("■ Hide", use_container_width=True)

    if "show_stream" not in st.session_state:
        st.session_state.show_stream = False
    if "stream_cam_id" not in st.session_state:
        st.session_state.stream_cam_id = None

    if show:
        st.session_state.show_stream   = True
        st.session_state.stream_cam_id = cam_id
    if hide:
        st.session_state.show_stream   = False
        st.session_state.stream_cam_id = None

    if st.session_state.show_stream and st.session_state.stream_cam_id == cam_id:

        # ── Embedded HTML component that owns the WebSocket lifecycle.
        #    The backend sends JSON: { frame: "<base64 jpeg>", counts: {car:N,...}, total: N }
        #    We render the annotated frame as a data-URI and overlay the vehicle counts.
        st.components.v1.html(f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: transparent;
    font-family: 'DM Sans', 'Segoe UI', sans-serif;
    color: #fafafa;
  }}

  /* ── wrapper ── */
  #wrapper {{
    position: relative;
    width: 100%;
    background: #111115;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    overflow: hidden;
    min-height: 360px;
  }}

  /* ── frame image ── */
  #feed {{
    width: 100%;
    display: block;
    border-radius: 12px;
  }}

  /* ── placeholder shown before first frame ── */
  #placeholder {{
    width: 100%;
    min-height: 360px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #3f3f46;
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    gap: 14px;
  }}
  #placeholder .icon {{ font-size: 32px; opacity: 0.15; }}

  /* ── vehicle count overlay (top-left) ── */
  #overlay {{
    position: absolute;
    top: 14px;
    left: 14px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    pointer-events: none;
  }}
  .chip {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(0,0,0,0.72);
    border: 1px solid rgba(110,231,183,0.25);
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 500;
    color: #6ee7b7;
    backdrop-filter: blur(8px);
    white-space: nowrap;
  }}
  .chip .lbl {{ color: #a1a1aa; font-weight: 400; font-size: 11px; }}
  .chip .num {{ font-variant-numeric: tabular-nums; font-size: 14px; }}

  /* ── status bar (bottom) ── */
  #statusbar {{
    position: absolute;
    bottom: 0; left: 0; right: 0;
    background: rgba(0,0,0,0.6);
    border-top: 1px solid rgba(255,255,255,0.06);
    padding: 7px 14px;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 10px;
    color: #52525b;
    backdrop-filter: blur(4px);
    font-family: 'DM Mono', monospace;
  }}
  #dot {{
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #52525b;
    flex-shrink: 0;
    transition: background 0.3s;
  }}
  #dot.live {{
    background: #6ee7b7;
    animation: blink 2s ease-in-out infinite;
  }}
  @keyframes blink {{
    0%,100% {{ opacity:1; box-shadow: 0 0 0 0 rgba(110,231,183,0.4); }}
    50%      {{ opacity:.7; box-shadow: 0 0 0 4px rgba(110,231,183,0); }}
  }}
  #fps {{ margin-left: auto; }}
</style>
</head>
<body>
<div id="wrapper">
  <div id="placeholder">
    <div class="icon">▶</div>
    Connecting to detection stream…
  </div>
  <img id="feed" style="display:none;" alt="YOLO stream" />
  <div id="overlay"></div>
  <div id="statusbar">
    <div id="dot"></div>
    <span id="status">Connecting · {ws_url}</span>
    <span id="fps"></span>
  </div>
</div>

<script>
  const WS_URL    = "{ws_url}";
  const feed      = document.getElementById('feed');
  const overlay   = document.getElementById('overlay');
  const dot       = document.getElementById('dot');
  const statusEl  = document.getElementById('status');
  const fpsEl     = document.getElementById('fps');
  const ph        = document.getElementById('placeholder');

  let frameCount = 0, lastTick = Date.now(), ws = null, retryTimer = null;

  /* ── build vehicle count chips ── */
  function renderCounts(counts, total) {{
    overlay.innerHTML = '';



    // per-class chips (skip zeroes)
    if (counts && typeof counts === 'object') {{
      for (const [cls, n] of Object.entries(counts)) {{
        if (!n) continue;
        const c = document.createElement('div');
        c.className = 'chip';
        c.innerHTML = '<span class="lbl">' + cls + '</span><span class="num">' + n + '</span>';
        overlay.appendChild(c);
      }}
    }}
  }}

  /* ── fps counter ── */
  function tick() {{
    frameCount++;
    const now = Date.now();
    if (now - lastTick >= 1000) {{
      fpsEl.textContent = frameCount + ' fps';
      frameCount = 0;
      lastTick = now;
    }}
  }}

  /* ── WebSocket connect (with auto-retry) ── */
  function connect() {{
    if (ws) {{ try {{ ws.close(); }} catch(_) {{}} }}

    ws = new WebSocket(WS_URL);

    ws.onopen = () => {{
      dot.classList.add('live');
      statusEl.textContent = 'Live · ' + WS_URL;
      if (retryTimer) {{ clearTimeout(retryTimer); retryTimer = null; }}
    }};

    ws.onmessage = (evt) => {{
      let data;
      try {{ data = JSON.parse(evt.data); }}
      catch {{ return; }}   // ignore non-JSON (e.g. ping frames)

      /* show annotated frame */
      if (data.frame) {{
        feed.src = 'data:image/jpeg;base64,' + data.frame;
        if (ph.style.display !== 'none') {{
          ph.style.display  = 'none';
          feed.style.display = 'block';
        }}
      }}

      /* vehicle counts */
      renderCounts(data.counts ?? {{}}, data.total ?? 0);
      tick();
    }};

    ws.onerror = () => {{
      dot.classList.remove('live');
      statusEl.textContent = 'Connection error — retrying…';
    }};

    ws.onclose = (evt) => {{
      dot.classList.remove('live');
      statusEl.textContent = 'Disconnected (code ' + evt.code + ') — reconnecting in 3 s…';
      fpsEl.textContent = '';
      // auto-reconnect after 3 s
      retryTimer = setTimeout(connect, 3000);
    }};
  }}

  connect();
</script>
</body>
</html>
""", height=520, scrolling=False)

        st.caption(f"WebSocket stream · {ws_url}  ·  YOLO vehicle detection active")

    else:
        st.markdown("""
        <div class="vid-ph">
            <div class="vid-icon">▶</div>
            Select a camera and press Show Stream
        </div>
        """, unsafe_allow_html=True)