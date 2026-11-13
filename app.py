import io
import os
import csv
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
""", unsafe_allow_html=True)

# Main brand header — custom logo replaces generic rocket/space icon.
logo_path = "assets/gravityware_logo.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=440)
st.markdown("<div class='gw-eyebrow'>TEAM BIGWIN · NASA SPACE APPS 2026</div>", unsafe_allow_html=True)
st.markdown("<div class='small-muted'>Healthy Astronauts. Successful Missions. &nbsp; · &nbsp; Monitor · Adapt · Thrive</div>", unsafe_allow_html=True)

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
    story.append(Paragraph("Educational prototype only. Not a diagnosis, treatment recommendation, or clinically validated medical score. Follow qualified medical and mission protocols for health concerns.", styles["Italic"]))
    doc.build(story)
    return buffer.getvalue()

# ---------- Sidebar ----------
with st.sidebar:
    if os.path.exists("assets/gravityware_logo.png"):
        st.image("assets/gravityware_logo.png", use_container_width=True)
    st.markdown("<div class='gw-eyebrow'>MISSION CONTROL</div>", unsafe_allow_html=True)
    st.write(f"Signed in: **{st.session_state.get('user_email', get_user_email(user) or 'Astronaut')}**")
    page = st.radio("Navigation", ["Dashboard", "Daily Health Log", "Health History", "Reports", "Gravity Adaptation", "About"])
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
    st.markdown("<div class='gw-hero'><div class='gw-eyebrow'>MISSION CONTROL</div><div class='gw-hero-title'>Welcome back, <span>Astronaut!</span></div><div class='gw-hero-sub'>Your Health. Our Mission. &nbsp; · &nbsp; Personal health overview and gravity adaptation tracking.</div></div>", unsafe_allow_html=True)
    rows = load_records()
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
            st.plotly_chart(px.line(chart_df, x="record_date", y="heart_rate", markers=True, title="Heart rate history", template="plotly_dark"), use_container_width=True)
        if "spo2" in chart_df:
            st.plotly_chart(px.line(chart_df, x="record_date", y="spo2", markers=True, title="Blood oxygen (SpO₂) history", template="plotly_dark"), use_container_width=True)
        st.caption("Trends are descriptive only and should be interpreted by qualified medical personnel.")
    else:
        st.info("No daily records yet. Open Daily Health Entry to add the first record.")
        st.metric("Records logged", 0)
    st.subheader("Mission gravity environment")
    st.write("Earth (1g), orbital microgravity, Moon (0.16g), Mars (0.38g), or Return to Earth (1g). Select the environment when entering each daily record.")

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
        gravity = st.selectbox("Gravity environment", ["Earth (1g)", "Orbital microgravity", "Moon (0.16g)", "Mars (0.38g)", "Return to Earth (1g)"])
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

# ---------- History ----------
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

# ---------- About ----------
elif page == "About":
    st.header("About GravityWare")
    st.markdown("""
**GravityWare — Understanding Health Beyond Earth** is a Team BigwIN educational prototype exploring daily astronaut health logging and health changes across mission gravity environments.

**Included in v1.3**
- Individual astronaut registration and sign-in
- Account-isolated permanent daily records
- Vital signs, sleep, wellbeing, exercise, symptoms and notes
- Health history and trend charts
- Baseline comparison across gravity environments
- PDF and CSV date-range reports

**Scientific and safety limitations**
- The app is not a medical device and does not diagnose, predict, or recommend treatment.
- The gravity adaptation comparison is experimental and descriptive, not clinically validated.
- Orbital conditions are described as microgravity (apparent weightlessness), not literal zero gravity.
- Only enter simulated or explicitly authorized demonstration data. Do not enter sensitive real medical records in this competition prototype.
- Follow qualified medical and mission protocols for health concerns or emergencies.
""")
    st.markdown("[NASA Human Research Program](https://www.nasa.gov/hrp/) · [NASA Human Research Roadmap](https://humanresearchroadmap.nasa.gov/)")
