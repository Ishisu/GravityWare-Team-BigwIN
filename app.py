import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# ============================================================
# GRAVITYWARE v1.2 | Team BigwIN
# Educational astronaut health + gravity adaptation prototype
# ============================================================

st.set_page_config(
    page_title="GravityWare | Astronaut Health & Adaptation",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #07111f 0%, #101b32 55%, #10152a 100%);
    color: #e8f1ff;
}
section[data-testid="stSidebar"] { background: #0b1425; }
h1, h2, h3 { color: #73d5ff !important; }
div[data-testid="stMetric"] {
    background: #14243b; border: 1px solid #294461;
    padding: 14px; border-radius: 12px;
}
.stButton button, .stDownloadButton button {
    background: #087eaa; color: white; border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

APP_NAME = "GravityWare"
VERSION = "1.2"
GRAVITY_LEVELS = {
    "Earth (1g)": 1.0,
    "Microgravity (Orbit)": 0.0,
    "Moon (0.16g)": 0.16,
    "Mars (0.38g)": 0.38,
    "Return to Earth (1g)": 1.0,
}

COLUMNS = [
    "Date", "Heart Rate", "Systolic BP", "Diastolic BP", "SpO2",
    "Temperature", "Sleep Hours", "Stress", "Fatigue",
    "Exercise Minutes", "Mood", "Gravity Phase", "Gravity Symptoms"
]

def create_sample_data():
    now = datetime.now()
    samples = [
        [6, 72, 118, 78, 98, 36.7, 7.5, 3, 2, 45, "Good", "Earth (1g)", "None"],
        [5, 75, 120, 80, 98, 36.8, 7.0, 4, 3, 40, "Good", "Earth (1g)", "None"],
        [4, 78, 121, 81, 97, 36.8, 6.5, 5, 4, 35, "Okay", "Microgravity (Orbit)", "Nausea"],
        [3, 80, 124, 82, 97, 36.9, 6.0, 5, 5, 35, "Okay", "Microgravity (Orbit)", "Dizziness"],
        [2, 82, 126, 84, 96, 37.0, 5.5, 6, 6, 30, "Okay", "Microgravity (Orbit)", "Dizziness, Fatigue"],
        [1, 79, 122, 81, 97, 36.8, 7.0, 4, 3, 40, "Good", "Microgravity (Orbit)", "None"],
        [0, 76, 120, 80, 98, 36.7, 7.5, 3, 2, 45, "Good", "Microgravity (Orbit)", "None"],
    ]
    records = []
    for r in samples:
        records.append({
            "Date": now - timedelta(days=r[0]),
            "Heart Rate": r[1], "Systolic BP": r[2], "Diastolic BP": r[3],
            "SpO2": r[4], "Temperature": r[5], "Sleep Hours": r[6],
            "Stress": r[7], "Fatigue": r[8], "Exercise Minutes": r[9],
            "Mood": r[10], "Gravity Phase": r[11], "Gravity Symptoms": r[12],
        })
    return pd.DataFrame(records, columns=COLUMNS)

if "health_data" not in st.session_state:
    st.session_state.health_data = create_sample_data()

if "baseline_index" not in st.session_state:
    st.session_state.baseline_index = 0

def assess_health(reading):
    urgent, warnings = [], []
    symptoms = str(reading.get("Gravity Symptoms", "None"))
    emergency_symptoms = [
        "Chest pain", "Severe breathing difficulty", "Fainting",
        "New confusion or weakness"
    ]
    if symptoms != "None":
        for symptom in symptoms.split(", "):
            if symptom in emergency_symptoms:
                urgent.append(f"Reported emergency symptom: {symptom}")
    if reading["SpO2"] < 90:
        urgent.append("Very low oxygen saturation reading")
    if reading["Systolic BP"] >= 180 or reading["Diastolic BP"] >= 120:
        urgent.append("Very high blood pressure reading")
    if reading["Heart Rate"] < 40 or reading["Heart Rate"] > 130:
        urgent.append("Heart rate outside this prototype's urgent-review limits")
    if reading["Temperature"] >= 39.5:
        urgent.append("High temperature reading")
    if reading["SpO2"] < 95:
        warnings.append("Oxygen saturation below the prototype reference threshold")
    if reading["Systolic BP"] >= 140 or reading["Diastolic BP"] >= 90:
        warnings.append("Elevated blood pressure reading")
    if reading["Heart Rate"] < 50 or reading["Heart Rate"] > 100:
        warnings.append("Heart rate outside a general reference range")
    if reading["Temperature"] >= 38:
        warnings.append("Elevated temperature")
    if reading["Sleep Hours"] < 5:
        warnings.append("Low sleep duration")
    if reading["Stress"] >= 8:
        warnings.append("High reported stress")
    if reading["Fatigue"] >= 8:
        warnings.append("High reported fatigue")
    if urgent:
        return "RED", urgent + warnings
    if warnings:
        return "YELLOW", warnings
    return "GREEN", ["No rule-based warning detected in entered readings"]

def gravity_assessment(baseline, current):
    indicators, details = [], []
    checks = [
        ("Heart rate change", abs(current["Heart Rate"] - baseline["Heart Rate"]) >= 15,
         f"Heart rate changed by {current['Heart Rate'] - baseline['Heart Rate']:+.0f} bpm from baseline."),
        ("Reduced sleep", baseline["Sleep Hours"] - current["Sleep Hours"] >= 2,
         f"Sleep changed by {current['Sleep Hours'] - baseline['Sleep Hours']:+.1f} hours from baseline."),
        ("Increased fatigue", current["Fatigue"] - baseline["Fatigue"] >= 3,
         f"Fatigue changed by {current['Fatigue'] - baseline['Fatigue']:+.0f} points."),
        ("Increased stress", current["Stress"] - baseline["Stress"] >= 3,
         f"Stress changed by {current['Stress'] - baseline['Stress']:+.0f} points."),
        ("Low recorded exercise", current["Exercise Minutes"] < 30,
         "Recorded exercise is below this prototype's 30-minute monitoring prompt."),
    ]
    for name, triggered, detail in checks:
        if triggered:
            indicators.append(name)
            details.append(detail)
    symptom_text = str(current.get("Gravity Symptoms", "None"))
    monitored = ["Dizziness", "Nausea", "Vision changes", "Facial fullness", "Muscle discomfort"]
    if symptom_text != "None":
        for symptom in monitored:
            if symptom in symptom_text:
                indicators.append(symptom)
                details.append(f"Reported symptom: {symptom}.")
    count = len(indicators)
    status = "NO FLAGGED CHANGE" if count == 0 else ("SOME CHANGES TO REVIEW" if count <= 2 else "MULTIPLE CHANGES TO REVIEW")
    if not details:
        details.append("No monitored changes were flagged against the selected baseline.")
    return count, status, indicators, details

def recommendations(level):
    if level == "RED":
        return [
            "Follow the mission emergency medical protocol immediately.",
            "Notify the designated medical officer or flight surgeon.",
            "Do not delay emergency care to repeat measurements."
        ]
    if level == "YELLOW":
        return [
            "Repeat the measurement and verify sensor quality where appropriate.",
            "Compare the reading with the astronaut's personal baseline.",
            "Inform the mission medical officer according to mission protocol."
        ]
    return [
        "Continue routine health monitoring.",
        "Maintain mission-approved sleep, hydration and exercise routines.",
        "Report new or worsening symptoms to the medical team."
    ]

# Sidebar and navigation
with st.sidebar:
    st.title("🚀 GravityWare")
    st.caption("ASTRONAUT HEALTH + GRAVITY ADAPTATION")
    st.divider()
    astronaut_id = st.text_input("Astronaut ID", "ASTRA-001")
    mission = st.selectbox("Mission", ["Earth Orbit", "Lunar Mission", "Mars Mission"])
    gravity_phase = st.selectbox("Current Gravity Environment", list(GRAVITY_LEVELS), index=1)
    mission_day = st.number_input("Mission Day", min_value=0, max_value=2000, value=12)
    page = st.radio("Navigation", [
        "Mission Dashboard", "Health Monitoring", "Gravity Adaptation",
        "Body Systems", "Mission Report", "About"
    ])
    st.divider()
    st.caption(f"Team BigwIN | {APP_NAME} v{VERSION}")

data = st.session_state.health_data
baseline_index = min(st.session_state.baseline_index, len(data) - 1)
baseline = data.iloc[baseline_index].to_dict()
latest = data.iloc[-1].to_dict()
health_level, health_reasons = assess_health(latest)
gam_count, gam_status, gam_indicators, gam_details = gravity_assessment(baseline, latest)

st.title("🛰️ GravityWare")
st.markdown("### Understanding Health Beyond Earth")
st.caption("Your Health. Your Mission. Your Safety. | Team BigwIN | Prototype v1.2")
st.info(
    f"Astronaut: {astronaut_id}  |  Mission: {mission}  |  "
    f"Selected environment: {gravity_phase}  |  Mission day: {mission_day}"
)

if page == "Mission Dashboard":
    st.subheader("Mission Health Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Heart Rate", f"{latest['Heart Rate']} bpm")
    c2.metric("Blood Pressure", f"{latest['Systolic BP']}/{latest['Diastolic BP']}")
    c3.metric("Oxygen Saturation", f"{latest['SpO2']}%")
    c4.metric("Sleep", f"{latest['Sleep Hours']} hrs")
    st.divider()
    st.subheader("Rule-based Health Assessment")
    if health_level == "RED":
        st.error("🔴 RED — Urgent medical review required")
    elif health_level == "YELLOW":
        st.warning("🟡 YELLOW — Attention recommended")
    else:
        st.success("🟢 GREEN — No rule-based warning detected")
    for reason in health_reasons:
        st.write("•", reason)
    st.divider()
    st.subheader("Gravity Adaptation Monitor (GAM)")
    a, b, c = st.columns(3)
    a.metric("Change indicators", gam_count)
    b.metric("Monitoring summary", gam_status)
    c.metric("Gravity level", f"{GRAVITY_LEVELS[gravity_phase]:.2f} g")
    st.caption("GAM counts selected changes from a comparison baseline. It is experimental, not a validated medical score.")
    for detail in gam_details:
        st.write("•", detail)
    st.divider()
    st.subheader("Health Trends")
    chart1, chart2 = st.columns(2)
    with chart1:
        fig = px.line(data, x="Date", y="Heart Rate", markers=True,
                      title="Heart Rate Trend", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    with chart2:
        fig = px.line(data, x="Date", y="Sleep Hours", markers=True,
                      title="Sleep Trend", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    fig = px.line(data, x="Date", y="Fatigue", markers=True,
                  title="Fatigue Trend", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Recent Health Records")
    st.dataframe(data.sort_values("Date", ascending=False), use_container_width=True)

elif page == "Health Monitoring":
    st.subheader("Enter Astronaut Health Readings")
    with st.form("health_form"):
        left, right = st.columns(2)
        with left:
            heart_rate = st.number_input("Heart Rate (bpm)", 20, 220, 75)
            systolic = st.number_input("Systolic BP", 50, 250, 120)
            diastolic = st.number_input("Diastolic BP", 30, 150, 80)
            spo2 = st.number_input("Oxygen Saturation (%)", 50, 100, 98)
            temperature = st.number_input("Temperature (°C)", 30.0, 43.0, 36.8, step=0.1)
        with right:
            sleep = st.number_input("Sleep Hours", 0.0, 24.0, 7.0, step=0.5)
            stress = st.slider("Stress Level", 1, 10, 3)
            fatigue = st.slider("Fatigue Level", 1, 10, 3)
            exercise = st.number_input("Exercise Minutes", 0, 300, 45)
            mood = st.selectbox("Mood", ["Good", "Okay", "Low", "Very Low"])
        phase = st.selectbox("Gravity Environment for this reading", list(GRAVITY_LEVELS), index=list(GRAVITY_LEVELS).index(gravity_phase))
        symptoms = st.multiselect("Reported Symptoms", [
            "Dizziness", "Nausea", "Vision changes", "Facial fullness",
            "Muscle discomfort", "Headache", "Chest pain",
            "Severe breathing difficulty", "Fainting", "New confusion or weakness"
        ])
        submitted = st.form_submit_button("Save Readings and Assess Health", use_container_width=True)
    if submitted:
        new_record = {
            "Date": datetime.now(), "Heart Rate": heart_rate,
            "Systolic BP": systolic, "Diastolic BP": diastolic,
            "SpO2": spo2, "Temperature": temperature, "Sleep Hours": sleep,
            "Stress": stress, "Fatigue": fatigue, "Exercise Minutes": exercise,
            "Mood": mood, "Gravity Phase": phase,
            "Gravity Symptoms": ", ".join(symptoms) if symptoms else "None"
        }
        st.session_state.health_data = pd.concat(
            [st.session_state.health_data, pd.DataFrame([new_record])],
            ignore_index=True
        )
        level, reasons = assess_health(new_record)
        st.success("Reading added to this session.")
        if level == "RED":
            st.error("RED — Urgent medical review required")
        elif level == "YELLOW":
            st.warning("YELLOW — Attention recommended")
        else:
            st.success("GREEN — No rule-based warning detected")
        for reason in reasons:
            st.write("•", reason)
        base = st.session_state.health_data.iloc[baseline_index].to_dict()
        count, status, _, details = gravity_assessment(base, new_record)
        st.subheader("Gravity Adaptation Results")
        st.metric("Change indicators", count)
        st.write("**Monitoring summary:**", status)
        for detail in details:
            st.write("•", detail)
        st.info("For emergency symptoms, follow mission emergency protocols immediately. Do not rely on this prototype to decide whether care is needed.")

elif page == "Gravity Adaptation":
    st.subheader("🌍 Gravity Adaptation Monitor")
    st.write("Explore the gravity environments and compare health readings with a chosen baseline.")
    gravity_df = pd.DataFrame({
        "Environment": list(GRAVITY_LEVELS.keys()),
        "Gravity (g)": list(GRAVITY_LEVELS.values())
    })
    fig = px.bar(gravity_df, x="Environment", y="Gravity (g)",
                 title="Approximate Gravity Levels Relative to Earth",
                 template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    st.divider()
    st.subheader("Choose comparison baseline")
    options = [f"Record {i+1} — {pd.to_datetime(row['Date']).strftime('%Y-%m-%d %H:%M')} — {row['Gravity Phase']}"
               for i, row in data.iterrows()]
    chosen = st.selectbox("Baseline record", range(len(options)),
                          format_func=lambda i: options[i],
                          index=baseline_index)
    st.session_state.baseline_index = chosen
    baseline = data.iloc[chosen].to_dict()
    latest = data.iloc[-1].to_dict()
    count, status, indicators, details = gravity_assessment(baseline, latest)
    st.caption("For the intended workflow, choose a pre-flight Earth record as the baseline.")
    comparison = pd.DataFrame({
        "Measurement": ["Heart Rate", "Systolic BP", "Diastolic BP", "SpO2",
                        "Sleep Hours", "Stress", "Fatigue", "Exercise Minutes"],
        "Baseline": [baseline[k] for k in ["Heart Rate", "Systolic BP", "Diastolic BP", "SpO2",
                                            "Sleep Hours", "Stress", "Fatigue", "Exercise Minutes"]],
        "Latest": [latest[k] for k in ["Heart Rate", "Systolic BP", "Diastolic BP", "SpO2",
                                        "Sleep Hours", "Stress", "Fatigue", "Exercise Minutes"]]
    })
    st.dataframe(comparison, use_container_width=True, hide_index=True)
    st.metric("Flagged change indicators", count)
    st.write("**Monitoring summary:**", status)
    for detail in details:
        st.info(detail)
    st.caption("These are changes in entered data. They do not prove that gravity caused those changes.")

elif page == "Body Systems":
    st.subheader("🧍 Human Body Systems in Space")
    body_systems = {
        "Cardiovascular": "Track heart rate and blood pressure. Fluid redistribution and cardiovascular adaptation are important spaceflight research topics.",
        "Vision and Fluid Shift": "Track reported vision changes, headaches and facial fullness. Spaceflight-associated fluid shifts are an important research area.",
        "Balance and Vestibular": "Track dizziness, nausea and orientation difficulties. Changes in gravity can affect balance adaptation.",
        "Muscles and Bones": "Track exercise, fatigue and muscle discomfort. Reduced mechanical loading can contribute to muscle and bone deconditioning.",
        "Mental Wellness": "Track sleep, stress, mood and fatigue. Isolation and mission conditions can affect wellbeing."
    }
    selected = st.selectbox("Select a body system", list(body_systems))
    st.markdown(f"### {selected}")
    st.write(body_systems[selected])
    st.info("This explorer provides educational information and symptom tracking. It cannot measure internal fluid distribution, bone density or eye structure without specialist equipment.")

elif page == "Mission Report":
    st.subheader("📄 Astronaut Mission Health Report")
    st.write("**Team:** BigwIN")
    st.write("**Astronaut ID:**", astronaut_id)
    st.write("**Mission:**", mission)
    st.write("**Selected gravity environment:**", gravity_phase)
    st.write("**Mission day:**", mission_day)
    st.write("**Generated:**", datetime.now().strftime("%Y-%m-%d %H:%M"))
    st.divider()
    st.write("### Latest Health Assessment")
    st.write("**Risk level:**", health_level)
    for reason in health_reasons:
        st.write("•", reason)
    st.write("### Gravity Adaptation Monitor")
    st.write("**Flagged change indicators:**", gam_count)
    st.write("**Monitoring summary:**", gam_status)
    for detail in gam_details:
        st.write("•", detail)
    st.write("### Suggested next steps")
    for action in recommendations(health_level):
        st.write("•", action)
    csv_bytes = data.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Health History CSV", csv_bytes,
                       "gravityware_health_history.csv", "text/csv")
    report = f"""GRAVITYWARE v{VERSION} — MISSION HEALTH REPORT
TEAM BIGWIN

Astronaut ID: {astronaut_id}
Mission: {mission}
Selected gravity environment: {gravity_phase}
Mission day: {mission_day}
Generated: {datetime.now()}

HEALTH ASSESSMENT: {health_level}
{chr(10).join('- ' + x for x in health_reasons)}

GRAVITY ADAPTATION MONITOR
Flagged change indicators: {gam_count}
Monitoring summary: {gam_status}
{chr(10).join('- ' + x for x in gam_details)}

SUGGESTED NEXT STEPS
{chr(10).join('- ' + x for x in recommendations(health_level))}

LIMITATIONS
Educational prototype using simulated or manually entered data.
Not a clinical diagnosis or validated medical decision system.
Follow mission medical protocols.
"""
    st.download_button("⬇️ Download Mission Report TXT", report,
                       "gravityware_mission_report.txt", "text/plain")

elif page == "About":
    st.subheader("About GravityWare")
    st.markdown("""
**GravityWare** is an educational astronaut health and gravity-adaptation
monitoring prototype developed by **Team BigwIN**.

Its central feature, the **Gravity Adaptation Monitor (GAM)**, compares
entered health readings and reported symptoms with a selected baseline
across different gravity environments.

**Features**
- Astronaut health monitoring
- Personal baseline comparison
- Earth, orbital microgravity, Moon and Mars gravity profiles
- Gravity-related symptom tracking
- Explainable rule-based health alerts
- Health trend charts and downloadable reports

**Approximate gravity levels**
- Earth: 1g
- Moon: 0.16g
- Mars: 0.38g
- Orbital microgravity: apparent weightlessness; gravity is not literally zero

**Technology:** Python, Streamlit, Pandas and Plotly.

**Data notice:** Initial readings are simulated demonstration data, not real
astronaut medical records. The health rules and GAM are experimental and
not clinically validated. Changes shown by GAM do not establish that gravity
caused those changes.
""")
    st.markdown("[NASA Human Research Program](https://www.nasa.gov/hrp/)")
    st.markdown("[NASA Human Research Roadmap](https://humanresearchroadmap.nasa.gov/)")

st.divider()
st.caption(f"GravityWare v{VERSION} | Team BigwIN | Educational space-health prototype")
st.caption("Not for diagnosis or treatment. Follow qualified medical and mission protocols.")
