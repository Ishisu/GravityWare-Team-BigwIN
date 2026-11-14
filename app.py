import io
import os
import csv
import html
from datetime import date, datetime, timedelta
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from supabase import create_client

st.set_page_config(page_title="GravityWare | Astronaut Health Monitor", page_icon=None, layout="wide", initial_sidebar_state="expanded")

# ---------- GravityWare visual system ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root { color-scheme: dark; }
.stApp { background: radial-gradient(ellipse at 78% 4%, rgba(22,105,178,.22), transparent 36%), radial-gradient(ellipse at 8% 95%, rgba(42,78,168,.18), transparent 32%), #050b18; color:#eaf3ff; font-family:Inter, sans-serif; }
[data-testid="stHeader"] { background:rgba(4,10,22,.72); }
[data-testid="stToolbar"] { right:1rem; }
section[data-testid="stSidebar"] { background:linear-gradient(180deg,#071329 0%,#091a34 72%,#061022 100%); border-right:1px solid #1a3556; }
section[data-testid="stSidebar"] > div { padding-top:1rem; }
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#c4d7ef; }
section[data-testid="stSidebar"] [data-testid="stRadio"] label { background:transparent; border-radius:12px; padding:8px 10px; margin:2px 0; }
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:#102b50; }
h1,h2,h3 { color:#f0f6ff !important; letter-spacing:-.025em; }
h1 { font-weight:800 !important; }
p, label, .stMarkdown { color:#d4e3f5; }
.small-muted { color:#91aaca; font-size:.9rem; }
.gw-eyebrow { color:#43c4ff; letter-spacing:.18em; text-transform:uppercase; font-size:.76rem; font-weight:700; }
.gw-hero { padding:22px 26px 20px; border:1px solid rgba(67,153,226,.25); border-radius:22px; background:linear-gradient(110deg,rgba(12,31,61,.96),rgba(9,22,45,.84) 56%,rgba(20,65,112,.48)); box-shadow:0 16px 44px rgba(0,0,0,.22); margin-bottom:20px; }
.gw-hero-title { font-size:clamp(1.8rem,4vw,2.65rem); font-weight:800; color:#f4f8ff; line-height:1.12; }
.gw-hero-title span { background:linear-gradient(90deg,#25c4ff,#8272ff); -webkit-background-clip:text; background-clip:text; color:transparent; }
.gw-hero-sub { color:#9db7d8; font-size:1rem; margin-top:7px; }
div[data-testid="stMetric"] { background:linear-gradient(145deg,rgba(18,43,77,.95),rgba(10,24,47,.96)); border:1px solid #24476e; padding:16px 17px; border-radius:17px; box-shadow:0 8px 24px rgba(0,0,0,.16); }
div[data-testid="stMetricLabel"] { color:#9eb9dc !important; }
div[data-testid="stMetricValue"] { color:#f2f7ff !important; }
div[data-testid="stForm"] { background:linear-gradient(145deg,#0b1b32,#0a172a); border:1px solid #234365; padding:20px; border-radius:18px; }
.stTextInput input,.stNumberInput input,.stDateInput input,.stTextArea textarea { background:#0b1b31 !important; color:#eff7ff !important; border:1px solid #294968 !important; border-radius:10px !important; }
.stSelectbox div[data-baseweb="select"] > div,.stMultiSelect div[data-baseweb="select"] > div { background:#0b1b31; border-color:#294968; border-radius:10px; }
.stSlider [data-baseweb="slider"] { color:#24b9ff; }
div.stButton > button, div.stDownloadButton > button, button[kind="primary"] { border-radius:11px; border:1px solid #267cc2; background:linear-gradient(100deg,#087ed5,#2859c8); color:white; font-weight:650; min-height:2.7rem; }
div.stButton > button:hover, div.stDownloadButton > button:hover { border-color:#61d4ff; color:white; box-shadow:0 0 18px rgba(35,166,255,.25); }
[data-testid="stPlotlyChart"] { background:linear-gradient(145deg,rgba(12,29,54,.9),rgba(8,19,37,.95)); border:1px solid #203e60; border-radius:17px; padding:8px; }
[data-testid="stDataFrame"] { border:1px solid #244365; border-radius:14px; overflow:hidden; }
[data-testid="stAlert"] { border-radius:13px; }
hr { border-color:#1c3859; }
footer { visibility:hidden; }
</style>
<style>
/* v1.7.1 visual refinement: quieter, information-first research interface */
.stApp { background:#081321 !important; font-family:Arial, Helvetica, sans-serif !important; }
section[data-testid="stSidebar"] { background:#0b1b2d !important; border-right:1px solid #263b52 !important; }
h1,h2,h3 { letter-spacing:-.012em !important; font-weight:650 !important; }
h1 { font-size:1.85rem !important; }
h2 { font-size:1.45rem !important; }
h3 { font-size:1.12rem !important; }
.gw-eyebrow { letter-spacing:.10em !important; font-size:.70rem !important; }
.gw-hero { background:#10243a !important; border:1px solid #29445f !important; border-radius:12px !important; box-shadow:none !important; padding:18px 22px !important; }
.gw-hero-title { font-size:clamp(1.55rem,3vw,2.15rem) !important; font-weight:700 !important; }
.gw-hero-title span { background:none !important; color:#55c4ee !important; -webkit-text-fill-color:#55c4ee !important; }
.gw-hero-sub { font-size:.94rem !important; color:#b6c7d8 !important; }
div[data-testid="stMetric"] { background:#10243a !important; border:1px solid #29445f !important; border-radius:10px !important; box-shadow:none !important; padding:13px 15px !important; }
div[data-testid="stForm"] { background:#0d1d30 !important; border:1px solid #29445f !important; border-radius:10px !important; box-shadow:none !important; }
div.stButton > button, div.stDownloadButton > button, button[kind="primary"] { background:#176b9b !important; border:1px solid #3689b7 !important; border-radius:7px !important; box-shadow:none !important; font-weight:600 !important; }
div.stButton > button:hover, div.stDownloadButton > button:hover { background:#1d7eae !important; border-color:#62b9dc !important; box-shadow:none !important; }
[data-testid="stPlotlyChart"] { background:#0d1d30 !important; border:1px solid #29445f !important; border-radius:10px !important; box-shadow:none !important; }
[data-testid="stDataFrame"] { border:1px solid #29445f !important; border-radius:8px !important; }
[data-testid="stAlert"] { border-radius:8px !important; }
hr { border-color:#263b52 !important; }

</style>
<style>
/* GravityWare v1.7.3 — final restrained mission-operations visual system */
:root {
  --gw-bg: #081321;
  --gw-panel: #102238;
  --gw-panel-soft: #0d1c2e;
  --gw-border: #29435d;
  --gw-text: #e8f0f7;
  --gw-muted: #a9bacb;
  --gw-accent: #42b9df;
  --gw-accent-strong: #197ca8;
}
.stApp {
  background: var(--gw-bg) !important;
  color: var(--gw-text) !important;
  font-family: "Segoe UI", Arial, sans-serif !important;
}
[data-testid="stHeader"] { background: rgba(8,19,33,.96) !important; }
[data-testid="stToolbar"] { right: 1rem; }
.block-container {
  max-width: 1480px !important;
  padding-top: 1.6rem !important;
  padding-bottom: 2.5rem !important;
}
section[data-testid="stSidebar"] {
  background: #0b1b2c !important;
  border-right: 1px solid var(--gw-border) !important;
}
section[data-testid="stSidebar"] > div { padding-top: 1.15rem !important; }
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
  color: #c5d3df !important;
  line-height: 1.45 !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label {
  border-radius: 8px !important;
  padding: .48rem .62rem !important;
  margin: 2px 0 !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
  background: #142d45 !important;
}
h1, h2, h3, h4 {
  color: #f0f5fa !important;
  letter-spacing: -.018em !important;
  font-family: "Segoe UI", Arial, sans-serif !important;
}
h1 { font-size: 1.85rem !important; font-weight: 700 !important; }
h2 { font-size: 1.42rem !important; font-weight: 650 !important; }
h3 { font-size: 1.12rem !important; font-weight: 650 !important; }
p, label, .stMarkdown { color: #d2deea; }
.small-muted, [data-testid="stCaptionContainer"] {
  color: var(--gw-muted) !important;
}
.gw-eyebrow {
  color: var(--gw-accent) !important;
  letter-spacing: .105em !important;
  text-transform: uppercase;
  font-size: .70rem !important;
  font-weight: 700 !important;
}
.gw-hero {
  background: #10263c !important;
  border: 1px solid #2c4b66 !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  padding: 19px 22px !important;
  margin: .5rem 0 1.1rem !important;
}
.gw-hero-title {
  color: #f3f7fb !important;
  font-size: clamp(1.55rem, 2.7vw, 2.15rem) !important;
  font-weight: 700 !important;
  line-height: 1.18 !important;
}
.gw-hero-title span {
  color: #62c6e8 !important;
  background: none !important;
  -webkit-text-fill-color: #62c6e8 !important;
}
.gw-hero-sub { color: #b8c9d8 !important; font-size: .94rem !important; }
div[data-testid="stMetric"] {
  background: #10243a !important;
  border: 1px solid #2b4863 !important;
  border-radius: 10px !important;
  box-shadow: none !important;
  padding: 13px 15px !important;
}
div[data-testid="stMetricLabel"] { color: #b7c8d8 !important; }
div[data-testid="stMetricValue"] {
  color: #f1f6fa !important;
  font-weight: 650 !important;
}
div[data-testid="stForm"], [data-testid="stExpander"] {
  background: #0e2033 !important;
  border: 1px solid #2a465f !important;
  border-radius: 10px !important;
  box-shadow: none !important;
}
[data-testid="stExpander"] summary {
  background: #132a40 !important;
  border-radius: 9px !important;
}
.stTextInput input, .stNumberInput input, .stDateInput input,
.stTextArea textarea {
  background: #0b1b2c !important;
  color: #edf4fa !important;
  border: 1px solid #38536c !important;
  border-radius: 7px !important;
}
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {
  background: #0b1b2c !important;
  border-color: #38536c !important;
  border-radius: 7px !important;
}
div.stButton > button, div.stDownloadButton > button,
button[kind="primary"], button[kind="secondary"] {
  border-radius: 7px !important;
  min-height: 2.55rem !important;
  font-weight: 600 !important;
  box-shadow: none !important;
}
div.stButton > button[kind="primary"],
button[kind="primary"] {
  background: #176f99 !important;
  border: 1px solid #3b98bd !important;
  color: #fff !important;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
  border-color: #69c5e3 !important;
  filter: brightness(1.08);
}
[data-testid="stPlotlyChart"] {
  background: #0e2033 !important;
  border: 1px solid #2a465f !important;
  border-radius: 10px !important;
  padding: 7px !important;
  box-shadow: none !important;
}
[data-testid="stDataFrame"], [data-testid="stTable"] {
  border: 1px solid #2a465f !important;
  border-radius: 9px !important;
  overflow: hidden !important;
}
[data-testid="stAlert"] { border-radius: 8px !important; }
[data-testid="stNotification"] { border-radius: 8px !important; }
hr { border-color: #263f57 !important; }
a { color: #70c9e8 !important; }
a:hover { color: #a0e1f5 !important; }
:focus-visible { outline: 2px solid #69c5e3 !important; outline-offset: 2px !important; }
footer { visibility: hidden; }
@media (max-width: 900px) {
  .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
  .gw-hero { padding: 16px !important; }
}
</style>
""", unsafe_allow_html=True)

# Main brand header — custom logo replaces generic rocket/space icon.
logo_path = "assets/gravityware_logo.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=340)
st.markdown("<div class='gw-eyebrow'>TEAM BIGWIN · NASA SPACE APPS 2026</div>", unsafe_allow_html=True)
st.markdown("<div class='small-muted'>Astronaut health monitoring · Team BigwIN research prototype</div>", unsafe_allow_html=True)

# ---------- Supabase setup ----------
def get_secret(name: str) -> Optional[str]:
    try:
        value = st.secrets.get(name)
        if value:
            return str(value).strip()
    except Exception:
        pass
    return None

SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_KEY = get_secret("SUPABASE_KEY")

def supabase_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def set_auth_session(client, access_token, refresh_token):
    # A fresh client is created for this Streamlit session; tokens are stored per browser session.
    client.auth.set_session(access_token, refresh_token)
    return client

def get_user_id(user):
    return getattr(user, "id", None) or (user.get("id") if isinstance(user, dict) else None)

def get_user_email(user):
    return getattr(user, "email", None) or (user.get("email") if isinstance(user, dict) else None)


def get_user_metadata(user):
    if isinstance(user, dict):
        return user.get("user_metadata") or {}
    return getattr(user, "user_metadata", {}) or {}

def auth_screen():
    st.subheader("Astronaut account access")
    st.info("Create an individual account or sign in. Each account can view and manage only its own records.")
    tab_login, tab_signup = st.tabs(["Sign in", "Create account"])
    client = supabase_client()
    if client is None:
        st.error("Supabase is not configured yet. Follow SETUP_GUIDE.md to create a Supabase project and add SUPABASE_URL and SUPABASE_KEY to Streamlit secrets.")
        st.stop()

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email address", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Sign in", use_container_width=True)
        if submitted:
            try:
                result = client.auth.sign_in_with_password({"email": email.strip(), "password": password})
                if result.session and result.user:
                    st.session_state["access_token"] = result.session.access_token
                    st.session_state["refresh_token"] = result.session.refresh_token
                    st.session_state["user_id"] = get_user_id(result.user)
                    st.session_state["user_email"] = get_user_email(result.user)
                    st.session_state["navigation_page"] = "Dashboard"
                    st.rerun()
                st.error("Sign-in did not return an active session. Check your email and password.")
            except Exception as exc:
                st.error(f"Sign-in failed: {exc}")

    with tab_signup:
        with st.form("signup_form"):
            astronaut_name = st.text_input("Astronaut display name")
            astronaut_code = st.text_input("Astronaut ID / callsign", placeholder="e.g. BW-001")
            email = st.text_input("Email address", key="signup_email")
            password = st.text_input("Create password", type="password", key="signup_password")
            confirm = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Create account", use_container_width=True)
        if submitted:
            if not astronaut_name.strip() or not astronaut_code.strip() or not email.strip():
                st.warning("Please complete the name, astronaut ID and email fields.")
            elif len(password) < 8:
                st.warning("Use a password with at least 8 characters.")
            elif password != confirm:
                st.warning("The passwords do not match.")
            else:
                try:
                    result = client.auth.sign_up({
                        "email": email.strip(),
                        "password": password,
                        "options": {"data": {"astronaut_name": astronaut_name.strip(), "astronaut_code": astronaut_code.strip()}}
                    })
                    if result.session and result.user:
                        st.session_state["access_token"] = result.session.access_token
                        st.session_state["refresh_token"] = result.session.refresh_token
                        st.session_state["user_id"] = get_user_id(result.user)
                        st.session_state["user_email"] = get_user_email(result.user)
                        st.session_state["navigation_page"] = "Dashboard"
                        st.success("Account created.")
                        st.rerun()
                    else:
                        st.success("Account created. Check your email for the confirmation link, then return here and sign in.")
                except Exception as exc:
                    st.error(f"Account creation failed: {exc}")

if "access_token" not in st.session_state or "refresh_token" not in st.session_state:
    auth_screen()
    st.stop()

client = supabase_client()
if client is None:
    st.error("Supabase configuration is missing.")
    st.stop()

try:
    client = set_auth_session(client, st.session_state["access_token"], st.session_state["refresh_token"])
    current_user = client.auth.get_user()
    user = current_user.user
    user_id = get_user_id(user)
    if not user_id:
        raise RuntimeError("Could not identify the signed-in user.")
    st.session_state["user_id"] = user_id
except Exception:
    for key in ["access_token", "refresh_token", "user_id", "user_email"]:
        st.session_state.pop(key, None)
    st.warning("Your login session expired. Please sign in again.")
    st.rerun()

# ---------- Helpers ----------
def safe_execute(query):
    try:
        return query.execute().data
    except Exception as exc:
        st.error(f"Database operation failed: {exc}")
        return None

def load_records(start=None, end=None):
    query = client.table("health_records").select("*").order("record_date", desc=True)
    if start:
        query = query.gte("record_date", start.isoformat())
    if end:
        query = query.lte("record_date", end.isoformat())
    return safe_execute(query)

def make_pdf(df: pd.DataFrame, report_title: str, astronaut_label: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=12*mm, leftMargin=12*mm, topMargin=12*mm, bottomMargin=12*mm)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("GravityWare — Astronaut Health Report", styles["Title"]),
        Paragraph(report_title, styles["Heading2"]),
        Paragraph(f"Astronaut: {astronaut_label} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]),
        Spacer(1, 8*mm),
    ]
    if df.empty:
        story.append(Paragraph("No health records were found for this date range.", styles["Normal"]))
    else:
        cols = ["record_date", "mission_day", "gravity_environment", "heart_rate", "systolic_bp", "diastolic_bp", "spo2", "temperature_c", "sleep_hours", "stress_level", "fatigue_level", "exercise_minutes", "symptoms"]
        view = df[[c for c in cols if c in df.columns]].copy()
        data = [list(view.columns)] + view.fillna("").astype(str).values.tolist()
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#17324f")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#aab8c7")),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 7),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#edf3f8")]),
        ]))
        story.append(table)
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("NASA research context (educational references): NASA Human Research Program — https://www.nasa.gov/hrp/ ; Five Hazards of Human Spaceflight — https://www.nasa.gov/hrp/hazards/ ; Risks of Human Spaceflight — https://www.nasa.gov/hrp/risks/ ; Ongoing HRP Research in Space — https://www.nasa.gov/hrp/ongoing-hrp-research/ . These pages provide scientific context only; the health readings in this report are user-entered demonstration data, not NASA astronaut data.", styles["Normal"]))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("Educational prototype only. Not a diagnosis, treatment recommendation, or clinically validated medical score. Follow qualified medical and mission protocols for health concerns.", styles["Italic"]))
    doc.build(story)
    return buffer.getvalue()


# ---------- Collaboration access and review helpers ----------
def get_collaboration_role():
    """Role is granted by an administrator in Supabase, never by user-editable metadata."""
    try:
        rows = client.table("reviewer_access").select("role").eq("user_id", user_id).eq("active", True).execute().data or []
        roles = {row.get("role") for row in rows}
        if "doctor" in roles:
            return "doctor"
        if "mission_control" in roles:
            return "mission_control"
    except Exception:
        return "astronaut"
    return "astronaut"

collaboration_role = get_collaboration_role()

def get_review_cases():
    try:
        return client.table("mission_reviews").select("*").order("updated_at", desc=True).execute().data or []
    except Exception as exc:
        st.error("Could not load collaboration cases. Check that the collaboration database setup has been completed.")
        st.caption(str(exc))
        return []

def update_review_case(case_id, values):
    try:
        values["updated_at"] = datetime.now().astimezone().isoformat()
        client.table("mission_reviews").update(values).eq("id", case_id).execute()
        st.success("Review updated.")
        st.rerun()
    except Exception as exc:
        st.error(f"Could not update the review: {exc}")


# ---------- Sidebar ----------
user_metadata = get_user_metadata(user)
astronaut_display_name = str(user_metadata.get("astronaut_name") or "Astronaut").strip() or "Astronaut"
astronaut_display_code = str(user_metadata.get("astronaut_code") or "").strip()
MISSION_OPTIONS = {
    "Orbital microgravity": {"gravity": "Approximately 0g", "mission": "Low Earth Orbit Research Station"},
    "Moon (0.16g)": {"gravity": "0.16g", "mission": "Moon Surface Exploration"},
    "Mars (0.38g)": {"gravity": "0.38g", "mission": "Mars Surface Research Base"},
}
mission_environment = str(user_metadata.get("mission_environment") or "Orbital microgravity")
if mission_environment not in MISSION_OPTIONS:
    mission_environment = "Orbital microgravity"
stored_mission_name = str(user_metadata.get("mission_name") or "").strip()
_default_mission_names = {item["mission"] for item in MISSION_OPTIONS.values()}
# If an older/default mission label conflicts with the saved gravity environment,
# display the matching mission label. Preserve genuinely custom mission names.
mission_name = (
    MISSION_OPTIONS[mission_environment]["mission"]
    if not stored_mission_name or stored_mission_name in _default_mission_names
    else stored_mission_name
)

role_labels = {
    "doctor": "MEDICAL REVIEWER",
    "mission_control": "MISSION CONTROL",
    "astronaut": "ASTRONAUT PORTAL",
}
current_role_label = role_labels.get(collaboration_role, "ASTRONAUT PORTAL")

with st.sidebar:
    if os.path.exists("assets/gravityware_logo.png"):
        st.image("assets/gravityware_logo.png", use_container_width=True)
    st.markdown(f"<div class='gw-eyebrow'>{current_role_label}</div>", unsafe_allow_html=True)
    st.write(f"Signed in: **{st.session_state.get('user_email', get_user_email(user) or 'Astronaut')}**")
    st.caption(f"👩‍🚀 {astronaut_display_name}" + (f" · {astronaut_display_code}" if astronaut_display_code else ""))

    with st.expander("Edit Astronaut Profile"):
        with st.form("edit_astronaut_profile"):
            edited_name = st.text_input("Astronaut display name", value=astronaut_display_name)
            edited_code = st.text_input("Astronaut ID / callsign", value=astronaut_display_code)
            edited_environment = st.selectbox("Mission gravity environment", list(MISSION_OPTIONS), index=list(MISSION_OPTIONS).index(mission_environment))
            edited_mission = st.text_input("Mission name", value=mission_name)
            save_profile = st.form_submit_button("Save profile", use_container_width=True)
        if save_profile:
            if not edited_name.strip() or not edited_code.strip():
                st.warning("Please enter both the astronaut name and ID/callsign.")
            else:
                try:
                    client.auth.update_user({"data": {
                        "astronaut_name": edited_name.strip(),
                        "astronaut_code": edited_code.strip(),
                        "mission_environment": edited_environment,
                        "mission_name": (
                            MISSION_OPTIONS[edited_environment]["mission"]
                            if not edited_mission.strip() or edited_mission.strip() in {item["mission"] for item in MISSION_OPTIONS.values()}
                            else edited_mission.strip()
                        )
                    }})
                    st.success("Astronaut profile updated.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not update profile: {exc}")

    navigation_pages = ["Dashboard", "Daily Health Log", "Import CSV", "Early Warning AI", "My Gravity-Aware Assessment", "Gravity Health Education", "Health History", "Reports", "Gravity Adaptation", "NASA Research", "About"]
    if collaboration_role == "doctor":
        navigation_pages.insert(7, "Medical Review Center")
    elif collaboration_role == "mission_control":
        navigation_pages.insert(7, "Mission Control Center")
    page = st.radio("Navigation", navigation_pages, key="navigation_page")
    if st.button("Sign out", use_container_width=True):
        try:
            client.auth.sign_out()
        except Exception:
            pass
        for key in ["access_token", "refresh_token", "user_id", "user_email"]:
            st.session_state.pop(key, None)
        st.rerun()

# ---------- Dashboard ----------
if page == "Dashboard":
    safe_astronaut_name = html.escape(astronaut_display_name)
    st.markdown(f"<div class='gw-hero'><div class='gw-eyebrow'>{current_role_label}</div><div class='gw-hero-title'>Mission health overview · <span>{safe_astronaut_name}</span></div><div class='gw-hero-sub'>Review recent measurements, personal trends and mission context.</div></div>", unsafe_allow_html=True)
    rows = load_records()

    with st.expander("Request medical review", expanded=False):
        st.write("Use this form to share a health concern with an authorized medical reviewer. It creates a review case; it is not an emergency service.")
        with st.form("request_medical_review"):
            concern = st.text_area("What would you like the medical team to review?", placeholder="Describe the change, symptoms, or concern in your own words.")
            selected_date = st.date_input("Related health-record date", value=date.today())
            submitted_case = st.form_submit_button("Submit for medical review", use_container_width=True)
        if submitted_case:
            if not concern.strip():
                st.warning("Please describe what you would like reviewed.")
            else:
                try:
                    client.table("mission_reviews").insert({
                        "user_id": user_id,
                        "astronaut_name": astronaut_display_name,
                        "astronaut_code": astronaut_display_code,
                        "gravity_environment": mission_environment,
                        "record_date": selected_date.isoformat(),
                        "case_summary": concern.strip(),
                        "status": "Awaiting medical review",
                        "created_by": user_id
                    }).execute()
                    st.success("Your request has been submitted to the authorized medical review team.")
                except Exception as exc:
                    st.error("The review request could not be submitted. The administrator may need to install the collaboration database setup.")
                    st.caption(str(exc))

    # Astronaut-facing read-only view of the complete collaboration history.
    st.subheader("My Medical Reviews")
    st.caption("Track your submitted requests, the medical team's assessment, and Mission Control's recorded operational decision.")
    if st.button("Refresh my medical reviews", key="refresh_my_medical_reviews"):
        st.rerun()
    try:
        my_cases = (
            client.table("mission_reviews")
            .select("id, astronaut_name, astronaut_code, gravity_environment, record_date, case_summary, status, doctor_assessment, doctor_recommendation, mission_decision, mission_action, created_at, updated_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
            .data or []
        )
        if not my_cases:
            st.info("You have not submitted any medical review requests yet. Submitted requests will appear here.")
        else:
            for case in my_cases:
                case_title = f"Review #{case.get('id')} · {case.get('status') or 'Status unavailable'}"
                with st.expander(case_title, expanded=False):
                    st.caption(
                        f"Submitted: {case.get('created_at') or 'Not available'} · "
                        f"Related record date: {case.get('record_date') or 'Not available'}"
                    )
                    st.write("**Your concern**")
                    st.write(case.get("case_summary") or "No concern description recorded.")
                    st.write("**Mission environment**")
                    st.write(case.get("gravity_environment") or "Not recorded")
                    st.divider()
                    st.write("**Doctor's assessment**")
                    st.write(case.get("doctor_assessment") or "The medical reviewer has not added an assessment yet.")
                    st.write("**Doctor's recommendation**")
                    st.write(case.get("doctor_recommendation") or "No recommendation has been recorded yet.")
                    st.divider()
                    st.write("**Mission Control decision**")
                    st.write(case.get("mission_decision") or "Mission Control has not recorded a decision yet.")
                    st.write("**Operational action**")
                    st.write(case.get("mission_action") or "No operational action has been recorded yet.")
                    st.caption(f"Last updated: {case.get('updated_at') or 'Not available'}")
    except Exception as exc:
        st.error("Your medical review history could not be loaded. Check the collaboration table and your account's row-level access.")
        st.caption(str(exc))

    records = rows or []
    df = pd.DataFrame(records)
    if not df.empty:
        latest = df.iloc[0]
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Latest heart rate", f"{latest.get('heart_rate','—')} bpm")
        c2.metric("Latest SpO₂", f"{latest.get('spo2','—')}%")
        c3.metric("Sleep", f"{latest.get('sleep_hours','—')} h")
        c4.metric("Records logged", len(df))
        st.subheader("Recent health indicators")
        chart_df = df.sort_values("record_date")
        if "heart_rate" in chart_df:
            st.plotly_chart(px.line(chart_df, x="record_date", y="heart_rate", markers=True, title="Heart rate history", template="plotly_dark").update_layout(paper_bgcolor="#0d1d30", plot_bgcolor="#0d1d30", font_color="#d9e5f0", margin=dict(l=20,r=20,t=50,b=20)), use_container_width=True)
        if "spo2" in chart_df:
            st.plotly_chart(px.line(chart_df, x="record_date", y="spo2", markers=True, title="Blood oxygen (SpO₂) history", template="plotly_dark").update_layout(paper_bgcolor="#0d1d30", plot_bgcolor="#0d1d30", font_color="#d9e5f0", margin=dict(l=20,r=20,t=50,b=20)), use_container_width=True)
        st.caption("Trends are descriptive only and should be interpreted by qualified medical personnel.")
    else:
        st.info("No daily records yet. Open Daily Health Entry to add the first record.")
        st.metric("Records logged", 0)
    st.subheader("Your mission environment")
    st.write(f"**{mission_name} · {mission_environment} ({MISSION_OPTIONS[mission_environment]['gravity']})**")
    st.info("Your mission environment is saved in your astronaut profile and is used to tailor the educational explanations and health observations below. It does not change clinical safety thresholds.")
    st.subheader("Your health insights")
    if not df.empty:
        insight_df = df.sort_values("record_date")
        latest_row = insight_df.iloc[-1]
        if len(insight_df) >= 3:
            earlier = insight_df.iloc[:-1].tail(min(7, len(insight_df)-1))
            for field, label, lower_better in [("sleep_hours", "Sleep", True), ("fatigue_level", "Fatigue", False), ("stress_level", "Stress", False), ("heart_rate", "Heart rate", None)]:
                if field in insight_df and pd.notna(latest_row.get(field)) and earlier[field].notna().any():
                    baseline = float(earlier[field].median()); current = float(latest_row[field])
                    delta = current - baseline
                    if abs(delta) >= (0.8 if field in ["sleep_hours","stress_level","fatigue_level"] else 8):
                        direction = "higher" if delta > 0 else "lower"
                        st.write(f"- **{label}:** latest value is {direction} than the recent personal median ({current:g} vs {baseline:g}). This is a trend observation, not a diagnosis.")
        st.caption("Gravity context helps explain possible spaceflight relevance; it cannot establish that gravity caused an individual health change.")

# ---------- Daily Entry ----------
elif page == "Daily Health Log":
    st.header("Daily Astronaut Health Entry")
    st.write("Submit one record for each astronaut per mission date. Fields marked optional can be left blank.")
    with st.form("daily_health_form", clear_on_submit=True):
        c1,c2 = st.columns(2)
        record_date = c1.date_input("Record date", value=date.today())
        mission_day = c2.number_input("Mission day", min_value=0, max_value=5000, value=1, step=1)
        astronaut_name = st.text_input("Astronaut display name", value=(getattr(user, "user_metadata", {}) or {}).get("astronaut_name", "") if not isinstance(user, dict) else user.get("user_metadata", {}).get("astronaut_name", ""))
        astronaut_code = st.text_input("Astronaut ID / callsign", value=(getattr(user, "user_metadata", {}) or {}).get("astronaut_code", "") if not isinstance(user, dict) else user.get("user_metadata", {}).get("astronaut_code", ""))
        gravity = mission_environment
        st.text_input("Mission gravity environment (from your profile)", value=f"{mission_environment} · {MISSION_OPTIONS[mission_environment]['gravity']}", disabled=True)
        st.markdown("#### Vital signs")
        c1,c2,c3 = st.columns(3)
        heart_rate = c1.number_input("Heart rate (bpm)", 30, 220, 70)
        systolic = c2.number_input("Systolic BP (mmHg)", 60, 250, 120)
        diastolic = c3.number_input("Diastolic BP (mmHg)", 30, 160, 80)
        c1,c2,c3 = st.columns(3)
        spo2 = c1.number_input("SpO₂ (%)", 50, 100, 98)
        temperature = c2.number_input("Temperature (°C)", 30.0, 43.0, 36.8, step=0.1, format="%.1f")
        sleep = c3.number_input("Sleep (hours)", 0.0, 24.0, 8.0, step=0.5)
        st.markdown("#### Daily wellbeing")
        c1,c2,c3 = st.columns(3)
        stress = c1.slider("Stress level", 0, 10, 2)
        fatigue = c2.slider("Fatigue level", 0, 10, 2)
        exercise = c3.number_input("Exercise (minutes)", 0, 600, 30)
        mood = st.selectbox("Mood", ["Good", "Okay", "Low", "Anxious", "Irritable"])
        symptoms = st.multiselect("Symptoms (select any)", ["Dizziness", "Nausea", "Headache", "Vision changes", "Facial fullness", "Muscle discomfort", "Back discomfort", "Sleep difficulty", "None"])
        notes = st.text_area("Additional notes (optional)", max_chars=1000)
        consent = st.checkbox("I confirm this is a demonstration / authorized entry and the information is accurate.")
        submitted = st.form_submit_button("Save daily health record", use_container_width=True)
    if submitted:
        if not astronaut_name.strip() or not astronaut_code.strip():
            st.error("Please provide the astronaut display name and ID/callsign.")
        elif not consent:
            st.warning("Please confirm the entry before saving.")
        else:
            payload = {
                "user_id": user_id, "record_date": record_date.isoformat(), "mission_day": int(mission_day),
                "astronaut_name": astronaut_name.strip(), "astronaut_code": astronaut_code.strip(),
                "gravity_environment": gravity, "heart_rate": int(heart_rate), "systolic_bp": int(systolic),
                "diastolic_bp": int(diastolic), "spo2": int(spo2), "temperature_c": float(temperature),
                "sleep_hours": float(sleep), "stress_level": int(stress), "fatigue_level": int(fatigue),
                "exercise_minutes": int(exercise), "mood": mood,
                "symptoms": [s for s in symptoms if s != "None"], "notes": notes.strip() or None
            }
            try:
                client.table("health_records").insert(payload).execute()
                st.success("Daily health record saved permanently to your GravityWare database.")
                st.rerun()
            except Exception as exc:
                if "duplicate" in str(exc).lower() or "unique" in str(exc).lower():
                    st.error("A record already exists for this astronaut ID and date. Open Health History to review it.")
                else:
                    st.error(f"Could not save the record: {exc}")

# ---------- CSV bulk import ----------
elif page == "Import CSV":
    st.header("Import astronaut health records from CSV")
    st.write("Upload the 21-day synthetic demo CSV for the astronaut signed into this account. Records are saved to this account only.")
    st.info("Use one astronaut CSV per account. Do not upload the combined 63-record file to a single account, because it would mix the three demo astronauts' histories.")
    st.caption(f"Signed-in astronaut: {astronaut_display_name} · {astronaut_display_code or 'No astronaut ID set'}")
    uploaded_csv = st.file_uploader("Choose astronaut CSV file", type=["csv"], key="gw_csv_upload")
    if uploaded_csv is not None:
        try:
            import_df = pd.read_csv(uploaded_csv)
            required_columns = ["record_date", "mission_day", "astronaut_name", "astronaut_code", "gravity_environment", "heart_rate", "systolic_bp", "diastolic_bp", "spo2", "temperature_c", "sleep_hours", "stress_level", "fatigue_level", "exercise_minutes", "mood"]
            missing_columns = [col for col in required_columns if col not in import_df.columns]
            if missing_columns:
                st.error("This CSV is missing required columns: " + ", ".join(missing_columns))
            elif import_df.empty:
                st.warning("The selected CSV contains no records.")
            else:
                codes = import_df["astronaut_code"].dropna().astype(str).str.strip().unique().tolist()
                names = import_df["astronaut_name"].dropna().astype(str).str.strip().unique().tolist()
                if len(codes) != 1 or len(names) != 1:
                    st.error("Upload a CSV containing exactly one astronaut ID and one astronaut name.")
                elif not astronaut_display_code or codes[0] != astronaut_display_code:
                    st.error(f"This file is for {codes[0]}, but the signed-in profile is {astronaut_display_code or 'missing an astronaut ID'}. Update the profile or sign in to the matching astronaut account before importing.")
                elif names[0] != astronaut_display_name:
                    st.error(f"The CSV name ({names[0]}) does not match this account's profile ({astronaut_display_name}). Update the profile before importing.")
                else:
                    st.subheader("Import preview")
                    st.write(f"**{len(import_df)} records** for **{names[0]} ({codes[0]})**")
                    st.dataframe(import_df.head(8), use_container_width=True, hide_index=True)
                    confirm_import = st.checkbox("I confirm these are synthetic / authorized demonstration records and belong to this signed-in astronaut account.")
                    if st.button("Import records to my account", type="primary", disabled=not confirm_import):
                        allowed_gravity = {"Earth (1g)", "Orbital microgravity", "Moon (0.16g)", "Mars (0.38g)", "Return to Earth (1g)"}
                        allowed_moods = {"Good", "Okay", "Low", "Anxious", "Irritable"}
                        payloads, validation_errors = [], []
                        for row_num, row in import_df.iterrows():
                            try:
                                record_day = pd.to_datetime(row["record_date"], errors="raise").date()
                                gravity_value = str(row["gravity_environment"]).strip()
                                mood_value = str(row["mood"]).strip()
                                if gravity_value not in allowed_gravity:
                                    raise ValueError(f"unsupported gravity environment: {gravity_value}")
                                if mood_value not in allowed_moods:
                                    raise ValueError(f"unsupported mood: {mood_value}")
                                def as_num(field):
                                    val = pd.to_numeric(row[field], errors="raise")
                                    if pd.isna(val):
                                        raise ValueError(f"{field} is blank")
                                    return float(val)
                                rec = {
                                    "user_id": user_id,
                                    "record_date": record_day.isoformat(),
                                    "mission_day": int(as_num("mission_day")),
                                    "astronaut_name": names[0],
                                    "astronaut_code": codes[0],
                                    "gravity_environment": gravity_value,
                                    "heart_rate": int(round(as_num("heart_rate"))),
                                    "systolic_bp": int(round(as_num("systolic_bp"))),
                                    "diastolic_bp": int(round(as_num("diastolic_bp"))),
                                    "spo2": int(round(as_num("spo2"))),
                                    "temperature_c": round(as_num("temperature_c"), 1),
                                    "sleep_hours": round(as_num("sleep_hours"), 1),
                                    "stress_level": int(round(as_num("stress_level"))),
                                    "fatigue_level": int(round(as_num("fatigue_level"))),
                                    "exercise_minutes": int(round(as_num("exercise_minutes"))),
                                    "mood": mood_value,
                                    "symptoms": [] if pd.isna(row.get("symptoms")) or not str(row.get("symptoms")).strip() else [x.strip() for x in str(row.get("symptoms")).replace(",", ";").split(";") if x.strip() and x.strip().lower() != "none"],
                                    "notes": None if pd.isna(row.get("notes")) or not str(row.get("notes")).strip() else str(row.get("notes")).strip()
                                }
                                limits = {"heart_rate": (30,220), "systolic_bp": (60,250), "diastolic_bp": (30,160), "spo2": (50,100), "temperature_c": (30,43), "sleep_hours": (0,24), "stress_level": (0,10), "fatigue_level": (0,10), "exercise_minutes": (0,600), "mission_day": (0,5000)}
                                for field, (lo, hi) in limits.items():
                                    if not lo <= rec[field] <= hi:
                                        raise ValueError(f"{field} must be between {lo} and {hi}")
                                payloads.append(rec)
                            except Exception as exc:
                                validation_errors.append(f"CSV row {row_num + 2}: {exc}")
                        if validation_errors:
                            st.error("Import stopped because some rows need correction. No records were saved.")
                            for issue in validation_errors[:10]:
                                st.write("- " + issue)
                        else:
                            try:
                                existing_rows = client.table("health_records").select("record_date").eq("astronaut_code", codes[0]).execute().data or []
                                existing_dates = {str(item.get("record_date")) for item in existing_rows}
                                new_rows = [item for item in payloads if item["record_date"] not in existing_dates]
                                duplicate_count = len(payloads) - len(new_rows)
                                if new_rows:
                                    client.table("health_records").insert(new_rows).execute()
                                st.success(f"Import complete: {len(new_rows)} new records saved. {duplicate_count} existing date(s) were skipped. Your existing records were not overwritten.")
                                st.rerun()
                            except Exception as exc:
                                st.error(f"Could not complete the import: {exc}")
        except Exception as exc:
            st.error(f"Could not read this CSV file: {exc}")
    st.caption("CSV readings are demonstration data, not NASA astronaut telemetry or clinical measurements. The import does not create a diagnosis or validate medical safety.")

# ---------- Early Warning AI ----------
elif page == "Early Warning AI":
    from early_warning import analyze_health_records, MIN_ML_RECORDS

    st.header("Personalized Early Warning & AI Research")
    st.markdown(
        "GravityWare reviews the astronaut's own saved records for unusual changes and patterns. "
        "This is an experimental research feature, **not a diagnosis, medical advice, or a clinically validated warning system**."
    )
    rows = load_records()
    health_df = pd.DataFrame(rows or [])
    if health_df.empty:
        st.info("No health records are available yet. Add daily entries first; this page will analyse your saved history.")
    else:
        result = analyze_health_records(health_df)
        latest = result["latest"]
        st.caption(f"Analysis uses {result['record_count']} saved record(s), ordered by date. It only analyses records belonging to your signed-in account.")
        if result["record_count"] < 3:
            st.warning("Personal baseline is still being established. Add more daily records before relying on trend comparisons.")
        c1, c2, c3 = st.columns(3)
        c1.metric("Records analysed", result["record_count"])
        c2.metric("Indicators reviewed", len(result["indicators"]))
        c3.metric("AI model status", "Research mode" if result["ml_available"] else "Baseline mode")
        st.subheader("Latest personal health snapshot")
        metric_labels = [("heart_rate", "Heart rate", " bpm"), ("spo2", "SpO₂", "%"), ("sleep_hours", "Sleep", " h"), ("stress_level", "Stress", "/10"), ("fatigue_level", "Fatigue", "/10")]
        cols = st.columns(5)
        for col, (key, label, unit) in zip(cols, metric_labels):
            value = latest.get(key)
            col.metric(label, f"{value}{unit}" if pd.notna(value) else "—")
        st.divider()
        st.subheader("Personalized change review")
        if result["findings"]:
            for finding in result["findings"]:
                message = f"**{finding['indicator']} — {finding['level']}**  \n{finding['message']}"
                if finding["level"] == "High review priority":
                    st.error(message)
                elif finding["level"] == "Monitor":
                    st.warning(message)
                else:
                    st.info(message)
        else:
            st.success("No notable personal-baseline deviations were detected by the current experimental checks.")
        st.caption("These labels describe statistical changes from this user's own history. They are not clinical severity levels or emergency triage.")
        st.divider()
        st.subheader("Experimental AI pattern screening")
        if result["ml_available"]:
            if result["ml_flag"]:
                st.warning("The latest multi-indicator pattern was unusual relative to the earlier records used by this experimental Isolation Forest model.")
            else:
                st.success("The experimental model did not flag the latest multi-indicator pattern as unusual relative to the earlier records.")
            st.write(f"Model: Isolation Forest · Training records: {result['training_records']} · Input indicators: {', '.join(result['model_features'])}")
            st.caption("An anomaly is not evidence of disease. The model is unsupervised, trained only on this account's small history, and has not been clinically validated.")
        else:
            st.info(f"AI pattern screening becomes available after at least {MIN_ML_RECORDS} usable records. Until then, only transparent personal-baseline comparisons are shown.")
        st.subheader("Indicator trends")
        trend_cols = [c for c in ["heart_rate", "spo2", "temperature_c", "sleep_hours", "stress_level", "fatigue_level"] if c in health_df.columns]
        if trend_cols:
            plot_df = health_df.copy()
            plot_df["record_date"] = pd.to_datetime(plot_df["record_date"], errors="coerce")
            selected = st.multiselect("Choose indicators to view", trend_cols, default=trend_cols[:3], key="early_warning_trends")
            if selected:
                long_df = plot_df[["record_date"] + selected].melt("record_date", var_name="Indicator", value_name="Entered value")
                st.plotly_chart(px.line(long_df, x="record_date", y="Entered value", color="Indicator", markers=True, title="Personal health history", template="plotly_dark"), use_container_width=True)
        st.subheader("How to interpret this page")
        st.markdown("""
- **Monitor:** a recent reading differs from the user's historical median by a robust statistical amount.
- **High review priority:** multiple indicators changed together, or one indicator changed substantially compared with that user's history.
- **AI pattern screening:** an unsupervised model looks for unusual combinations; it does not identify a disease or predict a medical event.
- A short history, missing values, device errors, mission activity and environmental context can all affect results.
- For concerning symptoms or urgent health concerns, follow qualified medical and mission protocols rather than relying on this prototype.
""")
        st.info("Data boundary: all analysed values are user-entered records. This feature does not connect to NASA telemetry, wearables, or a validated clinical dataset.")

# ---------- Gravity-aware personal assessment ----------
elif page == "My Gravity-Aware Assessment":
    st.header("Your Gravity-Aware Health Assessment")
    st.write(f"**{astronaut_display_name} · {mission_name} · {mission_environment} ({MISSION_OPTIONS[mission_environment]['gravity']})**")
    st.info("This page combines your saved records, personal trends and mission context. It is an educational screening aid, not a clinical normal-range calculator, diagnosis or emergency triage tool.")
    rows = load_records()
    assess_df = pd.DataFrame(rows or [])
    if assess_df.empty:
        st.warning("No health records are saved yet. Add records or import your astronaut CSV to receive personalized trend explanations.")
    else:
        assess_df = assess_df.sort_values("record_date")
        latest = assess_df.iloc[-1]
        st.subheader("What do your latest records suggest?")
        st.caption("Categories describe whether a pattern is commonly discussed in spaceflight research and whether your own trend deserves attention. They do not certify that a reading is medically normal.")
        env_notes = {
            "Orbital microgravity": ["Fluid shifts toward the upper body, muscle and bone deconditioning, and cardiovascular adaptation are recognized spaceflight topics.", "Report new visual changes, fainting, chest pain, severe headache or breathing difficulty promptly under mission medical procedures."],
            "Moon (0.16g)": ["Lunar gravity is about 16% of Earth's. Long-duration human health effects at this gravity are not yet established; movement, balance, muscle and bone loading are important monitoring topics.", "Persistent dizziness, falls, new visual changes, fainting, chest pain or breathing difficulty require prompt medical assessment."],
            "Mars (0.38g)": ["Martian gravity is about 38% of Earth's. Long-duration human health effects in Martian gravity have not been directly established in humans; physical conditioning, movement and recovery are relevant monitoring topics.", "Persistent dizziness, falls, new visual changes, fainting, chest pain or breathing difficulty require prompt medical assessment."]
        }
        st.markdown("**What is known about your environment?**")
        st.write(env_notes[mission_environment][0])
        st.markdown("**Symptoms that should not be dismissed as normal adaptation**")
        st.warning(env_notes[mission_environment][1])
        if len(assess_df) < 3:
            st.info("Your personal baseline is still being established. Add more consistent records before interpreting trends.")
        else:
            prior = assess_df.iloc[:-1].tail(min(7, len(assess_df)-1))
            metrics = [("heart_rate","Heart rate","bpm",8),("spo2","SpO₂","%",2),("sleep_hours","Sleep","hours",0.8),("stress_level","Stress","/10",2),("fatigue_level","Fatigue","/10",2)]
            for key,label,unit,threshold in metrics:
                if key not in assess_df or pd.isna(latest.get(key)) or not prior[key].notna().any(): continue
                base=float(prior[key].median()); val=float(latest[key]); delta=val-base
                if abs(delta) < threshold:
                    status="Within recent personal pattern"
                    st.success(f"**{label}: {val:g}{unit}** — close to the recent personal median ({base:g}{unit}). This is a descriptive comparison, not proof that it is medically normal.")
                else:
                    status="Monitor personal change"
                    st.warning(f"**{label}: {val:g}{unit}** — differs from the recent personal median ({base:g}{unit}). Recheck under consistent conditions and consider symptoms, workload and measurement quality.")
                    st.write("**Why it may matter:** changes in this measure can be relevant to recovery or spaceflight adaptation. The gravity environment alone cannot explain the change.")
        st.subheader("How to interpret the result")
        st.markdown("- **Consistent with personal pattern:** little change from recent records; not a medical clearance.\n- **Monitor:** a noticeable personal trend; repeat and document it.\n- **Medical review:** symptoms, persistent or worsening changes, or clinician-defined thresholds should be reviewed by qualified medical staff.\n- **Urgent assessment:** follow mission emergency procedures for severe or sudden symptoms; do not wait for this app.")
        st.caption("No universal gravity-specific clinical thresholds are applied. Clinical thresholds must be supplied and approved by qualified flight medical professionals.")

# ---------- Gravity health education ----------
elif page == "Gravity Health Education":
    st.header("Gravity Health Education")
    st.write("Learn how different gravity environments can affect the human body. The mission briefing below is tailored to your saved profile; the learning library also lets you explore other environments.")

    mission_briefings = {
        "Orbital microgravity": {
            "title": "Your environment: orbital microgravity",
            "intro": "Your spacecraft and everything inside it are in continuous free fall around Earth. This creates apparent weightlessness, even though Earth's gravity is still acting on the spacecraft.",
            "why": "Without the usual loading from standing and moving on Earth, body fluids redistribute toward the upper body and muscles and bones receive less mechanical loading.",
            "focus": "Pay particular attention to fluid-shift symptoms, exercise and strength maintenance, sleep and recovery, circulation, and any new visual symptoms.",
            "limits": "Many spaceflight effects are documented from human experience in orbit. An individual symptom still needs context and must not be dismissed as normal just because you are in microgravity."
        },
        "Moon (0.16g)": {
            "title": "Your environment: lunar surface gravity",
            "intro": "The Moon's surface gravity is about 0.16 times Earth's. You still have weight and are pulled toward the surface, but your weight is much lower than it is on Earth.",
            "why": "Movement and physical loading differ from Earth. Lower loading may affect muscles and bones over time, while unfamiliar movement can make balance and mobility important to monitor.",
            "focus": "Pay particular attention to mobility, balance, falls, muscle conditioning, exercise, persistent pain or weakness, and recovery after activity.",
            "limits": "Long-duration human health outcomes in lunar gravity have not been directly established. These are monitoring considerations, not predictions that a specific condition will occur."
        },
        "Mars (0.38g)": {
            "title": "Your environment: Martian surface gravity",
            "intro": "Mars surface gravity is about 0.38 times Earth's. It is stronger than lunar gravity but much weaker than Earth's surface gravity.",
            "why": "Partial gravity changes the loads experienced during standing, walking and exercise. The body may still experience less mechanical loading than it does on Earth.",
            "focus": "Pay particular attention to conditioning, mobility, balance, exercise, sleep, fatigue and recovery during the mission.",
            "limits": "Humans have not lived long-term on Mars. The long-term health effects of living in 0.38g remain uncertain, so the page presents possible monitoring areas rather than confirmed outcomes."
        }
    }

    briefing = mission_briefings[mission_environment]
    st.subheader(briefing["title"])
    st.caption(f"{mission_name} · {mission_environment} · {MISSION_OPTIONS[mission_environment]['gravity']}")
    st.info(briefing["intro"])
    st.markdown("**Why this environment matters to your body**")
    st.write(briefing["why"])
    st.markdown("**Health topics to pay attention to during this mission**")
    st.write(briefing["focus"])
    st.caption(briefing["limits"])

    education = {
        "Orbital microgravity": [
            ("What is microgravity?", "In orbit, astronauts and their spacecraft are in continuous free fall around Earth, so they experience apparent weightlessness. It is not literally zero gravity."),
            ("Fluid shifts", "Without the usual gravity-driven pooling in the legs, body fluids shift toward the chest and head. Some astronauts notice facial puffiness or nasal congestion."),
            ("Muscles and bones", "Muscles and bones normally respond to loading. Reduced loading in space can contribute to muscle and bone loss, which is why exercise and medical monitoring matter."),
            ("Cardiovascular adaptation", "The heart and blood vessels adjust to fluid redistribution and the absence of normal upright posture. Changes in circulation should be interpreted with the astronaut's symptoms and medical history."),
            ("Vision and circulation", "Spaceflight can affect fluid distribution, circulation and eye-related structures. New visual symptoms should be reported rather than assumed to be normal."),
            ("Exercise and recovery", "Planned exercise helps counter some muscle and bone deconditioning. Follow the mission exercise plan and report difficulty completing it or unusual symptoms.")
        ],
        "Moon (0.16g)": [
            ("What is lunar gravity?", "The Moon's surface gravity is about 0.16 times Earth's. You still have weight, but it is much lower than on Earth."),
            ("Movement and balance", "Moving in a different gravity field may require adaptation. Falls, persistent dizziness or coordination problems deserve attention."),
            ("Muscles and bones", "Lower loading could affect muscles and bones over time, but long-duration human health outcomes in lunar gravity are not yet known directly."),
            ("Exercise and conditioning", "Exercise and functional movement are important to maintain conditioning. Follow the mission plan and report persistent pain, weakness or difficulty moving."),
            ("What should I monitor?", "Track mobility, falls, exercise, recovery and new symptoms consistently. Report persistent or worsening changes to mission medical staff.")
        ],
        "Mars (0.38g)": [
            ("What is Martian gravity?", "Mars surface gravity is about 0.38 times Earth's. It is stronger than lunar gravity but much weaker than Earth's."),
            ("Movement and conditioning", "Partial gravity changes the loads experienced during movement. Conditioning, balance and mobility are useful areas to monitor."),
            ("Muscles and bones", "Less loading than on Earth may affect muscles and bones over time. The exact long-term effects of living in Martian gravity in humans remain unknown."),
            ("Sleep, fatigue and recovery", "Mission workload, schedule and environment can affect sleep and recovery. Track changes over time and discuss persistent fatigue with medical staff."),
            ("What should I monitor?", "Track exercise, mobility, sleep, fatigue and symptoms consistently, and discuss persistent changes with mission medical staff.")
        ]
    }

    st.subheader("Learning topics for your mission")
    for title, body in education[mission_environment]:
        with st.expander(title):
            st.write(body)

    st.subheader("Explore other gravity environments")
    st.write("These short comparisons are general education. They do not change your saved mission profile.")
    other_environments = [env for env in education if env != mission_environment]
    for env in other_environments:
        with st.expander(f"Learn about {env}"):
            st.write(mission_briefings[env]["intro"])
            st.write(mission_briefings[env]["why"])
            for title, body in education[env]:
                st.markdown(f"**{title}**")
                st.write(body)

    st.subheader("Gravity compared with Earth")
    vals = {"Earth": 1.0, "Orbital apparent weightlessness": 0.0, "Moon": 0.16, "Mars": 0.38}
    for name, val in vals.items():
        st.write(f"**{name}:** {val:.2f}g" if val else f"**{name}:** apparent weightlessness (not zero gravity)")

    st.subheader("Learn from NASA")
    st.markdown("- [NASA Human Research Program — Hazards](https://www.nasa.gov/hrp/hazards/)\\n- [NASA Human Research Program — Risks](https://www.nasa.gov/hrp/risks/)\\n- [NASA Ongoing HRP Research](https://www.nasa.gov/hrp/ongoing-hrp-research/)")
    st.caption("NASA references provide scientific context. GravityWare's demo records are synthetic/user-entered data, not NASA telemetry. Lunar and Martian long-duration human evidence is limited. This page is educational and is not medical advice.")
# ---------- History ----------
elif page == "Medical Review Center":
    st.header("Medical Review Center")
    st.caption("For authorized medical reviewers. Review astronaut-submitted records and document clinical assessments for the mission medical team.")
    st.warning("This prototype supports documentation and communication. It does not diagnose, prescribe treatment, or determine fitness for duty. Follow approved medical protocols.")
    cases = get_review_cases()
    if cases:
        st.subheader("Open and recent cases")
        display = pd.DataFrame(cases)
        preferred = [c for c in ["id", "astronaut_name", "astronaut_code", "gravity_environment", "record_date", "status", "updated_at"] if c in display.columns]
        st.dataframe(display[preferred] if preferred else display, use_container_width=True, hide_index=True)
        case_ids = [row["id"] for row in cases]
        selected_id = st.selectbox("Select a case to review", case_ids, format_func=lambda x: next((f'Case {r["id"]} · {r.get("astronaut_name","Astronaut")} · {r.get("status","Open")}' for r in cases if r["id"] == x), str(x)))
        selected = next(r for r in cases if r["id"] == selected_id)
        st.markdown(f"**Astronaut:** {selected.get('astronaut_name','')} · {selected.get('astronaut_code','')}")
        st.markdown(f"**Mission environment:** {selected.get('gravity_environment','Not recorded')} · **Record date:** {selected.get('record_date','')}")
        st.markdown("**Submitted observations**")
        st.write(selected.get("case_summary") or "No summary supplied.")
        with st.form(f"doctor_review_{selected_id}"):
            assessment = st.text_area("Medical assessment / review notes", value=selected.get("doctor_assessment") or "", height=130, help="Document your professional review. Avoid entering a diagnosis unless appropriate to your professional role and protocol.")
            recommendation = st.text_area("Recommendations and follow-up", value=selected.get("doctor_recommendation") or "", height=100)
            status = st.selectbox("Review status", ["Awaiting medical review", "Reviewed — follow-up required", "Reviewed — monitoring advised", "Closed by medical reviewer"], index=["Awaiting medical review", "Reviewed — follow-up required", "Reviewed — monitoring advised", "Closed by medical reviewer"].index(selected.get("status","Awaiting medical review")) if selected.get("status") in ["Awaiting medical review", "Reviewed — follow-up required", "Reviewed — monitoring advised", "Closed by medical reviewer"] else 0)
            submitted = st.form_submit_button("Save medical review", use_container_width=True)
        if submitted:
            update_review_case(selected_id, {"doctor_assessment": assessment, "doctor_recommendation": recommendation, "status": status, "doctor_reviewer_id": user_id})
    else:
        st.info("There are no review cases yet. Astronauts can submit a case from their personal dashboard when this workflow is enabled.")
    st.caption("Access is granted by an administrator through the reviewer_access table. Do not use this demonstration account for real patient care.")

elif page == "Mission Control Center":
    st.header("Mission Control Center")
    st.caption("Operational review of astronaut health cases and the medical team's documented recommendations.")
    st.warning("Mission Control records operational actions. It must not replace or override clinical judgement.")
    cases = get_review_cases()
    if cases:
        st.subheader("Medical case overview")
        display = pd.DataFrame(cases)
        preferred = [c for c in ["id", "astronaut_name", "astronaut_code", "gravity_environment", "record_date", "status", "updated_at"] if c in display.columns]
        st.dataframe(display[preferred] if preferred else display, use_container_width=True, hide_index=True)
        case_ids = [row["id"] for row in cases]
        selected_id = st.selectbox("Select a case", case_ids, format_func=lambda x: next((f'Case {r["id"]} · {r.get("astronaut_name","Astronaut")} · {r.get("status","Open")}' for r in cases if r["id"] == x), str(x)))
        selected = next(r for r in cases if r["id"] == selected_id)
        st.markdown(f"**Astronaut:** {selected.get('astronaut_name','')} · {selected.get('astronaut_code','')}")
        st.markdown(f"**Environment:** {selected.get('gravity_environment','Not recorded')} · **Date:** {selected.get('record_date','')}")
        st.markdown("**Medical assessment**")
        st.write(selected.get("doctor_assessment") or "No medical assessment has been recorded yet.")
        st.markdown("**Medical recommendations**")
        st.write(selected.get("doctor_recommendation") or "No recommendations have been recorded yet.")
        with st.form(f"mission_decision_{selected_id}"):
            decision = st.text_area("Mission operational decision", value=selected.get("mission_decision") or "", height=120, help="Record operational coordination only. Do not make a clinical diagnosis or fitness-for-duty decision here.")
            action = st.text_area("Operational actions / owner / follow-up date", value=selected.get("mission_action") or "", height=90)
            submitted = st.form_submit_button("Save mission decision", use_container_width=True)
        if submitted:
            update_review_case(selected_id, {"mission_decision": decision, "mission_action": action, "mission_reviewer_id": user_id})
    else:
        st.info("No cases are available for mission-control review yet.")
    st.caption("Access is granted by an administrator through the reviewer_access table. This is a demonstration workflow, not a connection to NASA Mission Control.")

elif page == "Health History":
    st.header("Your Health History")
    c1,c2 = st.columns(2)
    start = c1.date_input("From", value=date.today()-timedelta(days=30), key="hist_start")
    end = c2.date_input("To", value=date.today(), key="hist_end")
    if start > end:
        st.warning("The start date must be before the end date.")
    else:
        rows = load_records(start, end)
        df = pd.DataFrame(rows or [])
        if df.empty:
            st.info("No records found for this period.")
        else:
            display_cols = ["record_date","mission_day","astronaut_code","gravity_environment","heart_rate","systolic_bp","diastolic_bp","spo2","temperature_c","sleep_hours","stress_level","fatigue_level","exercise_minutes","mood","symptoms"]
            st.dataframe(df[[c for c in display_cols if c in df.columns]], use_container_width=True, hide_index=True)
            st.caption("Only records belonging to your signed-in account are returned by the database security policies.")

# ---------- Reports ----------
elif page == "Reports":
    st.header("Health Reports")
    c1,c2 = st.columns(2)
    start = c1.date_input("Report from", value=date.today()-timedelta(days=7), key="report_start")
    end = c2.date_input("Report to", value=date.today(), key="report_end")
    if start > end:
        st.warning("The start date must be before the end date.")
    else:
        rows = load_records(start, end)
        df = pd.DataFrame(rows or [])
        st.write(f"**{len(df)}** record(s) in the selected period.")
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        label = st.session_state.get("user_email", "Astronaut")
        csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Download CSV report", data=csv_bytes, file_name=f"gravityware_report_{start}_{end}.csv", mime="text/csv", use_container_width=True)
        pdf_bytes = make_pdf(df, f"Period: {start.isoformat()} to {end.isoformat()}", label)
        st.download_button("Download PDF report", data=pdf_bytes, file_name=f"gravityware_report_{start}_{end}.pdf", mime="application/pdf", use_container_width=True)
        st.caption("Reports are generated from your account's saved records. CSV contains all returned fields; PDF is a concise summary.")

# ---------- Gravity Adaptation ----------
elif page == "Gravity Adaptation":
    st.header("Gravity Adaptation Monitor")
    st.subheader("Mission gravity environment comparison")
    st.caption("A concise educational comparison of the three mission environments. The human-health effects of long-duration partial gravity remain uncertain.")
    env_cols = st.columns(3)
    env_comparisons = [
        ("Orbital microgravity", "Approximately 0g", "Apparent weightlessness during continuous free fall. Research has documented fluid shifts, muscle and bone deconditioning, and cardiovascular adaptation in spaceflight."),
        ("Moon", "0.16g", "About 16% of Earth's surface gravity. Movement, balance, conditioning and muscle/bone loading are relevant topics; long-duration human health effects at lunar gravity are not established."),
        ("Mars", "0.38g", "About 38% of Earth's surface gravity. Movement, physical conditioning and recovery are relevant topics; long-duration human health effects at Martian gravity are not established."),
    ]
    for col, (env_title, env_value, env_text) in zip(env_cols, env_comparisons):
        with col:
            with st.container(border=True):
                st.markdown(f"**{env_title}**")
                st.metric("Gravity", env_value)
                st.write(env_text)
    st.info("Scientific boundary: known microgravity observations should not be assumed to predict human health outcomes on the Moon or Mars. This comparison is educational, not a clinical assessment.")
    st.divider()
    rows = load_records()
    df = pd.DataFrame(rows or [])
    if df.empty:
        st.info("Add daily records first to view gravity adaptation trends.")
    else:
        df = df.sort_values("record_date")
        baseline_date = st.selectbox("Choose baseline record date", df["record_date"].astype(str).tolist(), index=0)
        baseline = df[df["record_date"].astype(str) == baseline_date].iloc[0]
        latest = df.iloc[-1]
        metrics = ["heart_rate","spo2","sleep_hours","stress_level","fatigue_level"]
        changes = []
        for metric in metrics:
            b = float(baseline[metric])
            current = float(latest[metric])
            changes.append({"Indicator": metric.replace("_"," ").title(), "Baseline": b, "Latest": current, "Change": round(current-b,2)})
        st.dataframe(pd.DataFrame(changes), use_container_width=True, hide_index=True)
        st.info("The baseline comparison is descriptive and experimental. It is not a validated medical score and cannot prove that gravity caused a change.")
        st.plotly_chart(px.line(df, x="record_date", y=["heart_rate","spo2"], markers=True, title="Selected health indicators over time", template="plotly_dark"), use_container_width=True)

# ---------- NASA Research & Mission Hazards ----------
elif page == "NASA Research":
    st.header("NASA Research & Mission Hazards")
    st.markdown("""
This section translates NASA Human Research Program material into educational context for the GravityWare monitoring concept. **NASA research is the scientific reference; the readings entered in GravityWare remain demonstration data and are not NASA telemetry.**

### The five hazards of human spaceflight
NASA's Human Research Program groups important exploration challenges into five hazards. The cards below summarize the hazards and explain how GravityWare's current prototype relates to them.
""")
    hazards = [
        ("1 · Space radiation", "Space radiation can expose crew members to health risks during missions beyond Earth's protection. Radiation exposure is not measured by this app.", "GravityWare connection: an educational awareness topic only. No radiation sensor, dose calculation, or radiation-risk prediction is implemented."),
        ("2 · Isolation & confinement", "Living and working in a confined environment for long periods can affect behavioral health, sleep, teamwork, and performance.", "GravityWare connection: daily sleep, stress, fatigue, and mood self-reports can help a user review personal trends. These entries are not a psychological assessment."),
        ("3 · Distance from Earth", "As missions travel farther from Earth, communication delays and limited access to immediate support increase the importance of crew autonomy and preparation.", "GravityWare connection: the daily log and personal history are designed to support self-review. The app does not provide mission control communications or emergency medical support."),
        ("4 · Gravity fields", "Moving between Earth's gravity, microgravity, and partial gravity environments can affect multiple body systems and require adaptation.", "GravityWare connection: the Gravity Adaptation page compares an astronaut's entered indicators with a selected personal baseline. It is descriptive and experimental; it does not establish causation or a medical threshold."),
        ("5 · Hostile / closed environments", "Spacecraft and exploration environments are closed and demanding, making environmental and operational conditions relevant to crew health.", "GravityWare connection: mission context is included in the concept, but the current app does not measure cabin air, water, contaminants, or other environmental hazards."),
    ]
    for title, summary, link in hazards:
        with st.container(border=True):
            st.subheader(title)
            st.write(summary)
            st.caption(link)

    st.divider()
    st.subheader("Examples of ongoing NASA human-health research")
    st.markdown("""
NASA's ongoing research page describes investigations that can inform what health domains a future monitoring system might consider:

- **ARCHeR (Artemis II):** monitoring well-being, activity, and sleep; the page describes a wrist-worn actigraphy device that measures motion, sleep patterns, and light exposure.
- **Immune Biomarkers:** analysis of blood and saliva samples to study how deep-space missions affect the immune system. GravityWare does not collect or analyze biological samples.
- **Artemis II Standard Measures:** a consistent set of crew health information collected for a research data bank.
- **CIPHER:** a suite of studies examining how multiple body systems change during spaceflight.
- **Brain Fluid Pressure / vision research:** studies examining relationships between fluid pressure, eyes, and brain changes in space.

These are research examples, not live feeds or datasets connected to GravityWare. The current app's vital signs and wellbeing entries are manually entered demonstration values.
""")
    st.info("Scientific boundary: NASA sources inform the challenge context and feature rationale. GravityWare does not reproduce NASA clinical protocols, use NASA astronaut records, or validate its experimental baseline comparison.")
    st.subheader("NASA references")
    st.markdown("""
- [NASA 5 Hazards of Human Spaceflight](https://www.nasa.gov/hrp/hazards/)
- [NASA Risks of Human Spaceflight](https://www.nasa.gov/hrp/risks/)
- [NASA Ongoing HRP Research in Space](https://www.nasa.gov/hrp/ongoing-hrp-research/)
- [NASA Human Research Program](https://www.nasa.gov/hrp/)
- [Official NASA Space Apps 2026 challenge brief](https://www.spaceappschallenge.org/2026/challenges/health-monitoring-software/)
""")

# ---------- About ----------
elif page == "About":
    st.header("About GravityWare")
    st.markdown("""
**GravityWare — Understanding Health Beyond Earth** is a Team BigwIN educational prototype exploring daily astronaut health logging and health changes across mission gravity environments.

**Current prototype features**
- Individual astronaut registration and sign-in
- Account-isolated permanent daily records
- Vital signs, sleep, wellbeing, exercise, symptoms and notes
- Health history and trend charts
- Experimental personalized early-warning page with robust baseline comparisons and unsupervised anomaly screening (requires sufficient history)
- Baseline comparison across gravity environments
- PDF and CSV date-range reports
- NASA Research & Mission Hazards explorer summarizing NASA's five human-spaceflight hazards
- NASA HRP research examples and source links; NASA references included in exported PDF reports

**NASA resource-use statement**
NASA Human Research Program resources inform the hazard summaries and the rationale for sleep, wellbeing, and gravity-related trend review. GravityWare does not ingest NASA astronaut datasets or live telemetry. All values entered in the health log are user-entered demonstration data.

**Scientific and safety limitations**
- The app is not a medical device and does not diagnose, predict, or recommend treatment. The Early Warning AI page is experimental research software, not clinically validated.
- The gravity adaptation comparison is experimental and descriptive, not clinically validated.
- Orbital conditions are described as microgravity (apparent weightlessness), not literal zero gravity.
- Only enter simulated or explicitly authorized demonstration data. Do not enter sensitive real medical records in this competition prototype.
- Follow qualified medical and mission protocols for health concerns or emergencies.
""")
    st.markdown("[NASA Human Research Program](https://www.nasa.gov/hrp/) · [NASA Five Hazards](https://www.nasa.gov/hrp/hazards/) · [NASA Risks](https://www.nasa.gov/hrp/risks/) · [Ongoing NASA HRP Research](https://www.nasa.gov/hrp/ongoing-hrp-research/)")
