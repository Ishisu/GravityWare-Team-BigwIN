# GravityWare — Team BigwIN

**Understanding Health Beyond Earth**  
NASA Space Apps Challenge 2026 · Astronaut health-monitoring software prototype

GravityWare is a Streamlit prototype for astronaut health logging, personal trend review, gravity-environment education, experimental pattern screening, and a demonstration medical-review / mission-control workflow.

## Main features

- Individual astronaut sign-in and profile settings using Supabase Auth.
- Daily health logging and account-specific health history.
- CSV import with preview and validation.
- Personal trend review and experimental Early Warning AI screening.
- Gravity-aware assessment using the astronaut's saved mission environment and personal history.
- Educational comparison of orbital microgravity, Moon gravity (0.16g), and Mars gravity (0.38g).
- Gravity Health Education and NASA Human Research Program context.
- PDF and CSV report downloads.
- Demonstration workflow: astronaut requests review, a doctor records an assessment, and Mission Control records an operational decision.
- Astronaut dashboard displays the latest medical-review outcome.

## Run locally (Windows)

Open this project folder in VS Code. Configure `.streamlit/secrets.toml` using `.streamlit/secrets.toml.example`, then run:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Keep the terminal open while using the app. Streamlit normally opens at `http://localhost:8501`.

See `SETUP_GUIDE.md` for setup and deployment guidance.

## Supabase and existing data

- This project uses Supabase Auth and the existing `health_records`, `reviewer_access`, and `mission_reviews` tables.
- **For an already configured GravityWare Supabase project, do not rerun `database/setup.sql` or the collaboration migration.** They are initial setup scripts, not routine launch steps.
- Keep `.streamlit/secrets.toml` private. Never upload it to GitHub or share its contents.
- Use only the publishable/anon key in the client configuration with RLS enabled. Never put a service-role or secret key in the app.
- Before any future database or RLS changes, take and verify a backup.

## Demo data and scientific limitations

Use fictional profiles and synthetic or explicitly authorized demonstration records only. The health readings are not NASA astronaut records or live spacecraft telemetry. NASA resources are used as scientific and educational context, not as a live data connection.

Gravity-aware comparisons are descriptive and experimental. They are not clinically validated, do not establish that gravity caused a change, and do not provide diagnosis, treatment, medical clearance, or emergency triage. Long-duration human health effects in lunar and Martian gravity are uncertain. Follow qualified medical and mission procedures for real concerns.

## Collaboration workflow limitations

The doctor / Mission Control workflow is a competition prototype, not a live NASA integration or production clinical record system. Reviewer roles are assigned by a Supabase administrator. The app does not send email or push notifications. Do not use real patient or astronaut health data. UI-level role separation does not by itself establish production-grade database security.

## Project files

- `app.py` — Streamlit application.
- `early_warning.py` — experimental pattern-screening logic.
- `requirements.txt` — Python dependencies.
- `assets/` — GravityWare branding.
- `data/sample_astronaut_data.csv` — sample demonstration data.
- `database/setup.sql` — initial health-record schema for a fresh Supabase project only.
- `database/collaboration_setup_v1_7_4.sql` — initial collaboration schema/policies; do not rerun on an existing configured project.
- `.streamlit/secrets.toml.example` — configuration template; copy to `secrets.toml` and fill privately.
- `COMPETITION_FINAL_CHECKLIST.md` — final submission and demo checklist.
- `COLLABORATION_SETUP_GUIDE.md` — reviewer setup and workflow notes.

## NASA references

- NASA Five Hazards of Human Spaceflight: https://www.nasa.gov/hrp/hazards/
- NASA Risks of Human Spaceflight: https://www.nasa.gov/hrp/risks/
- NASA Ongoing HRP Research in Space: https://www.nasa.gov/hrp/ongoing-hrp-research/
- NASA Human Research Program: https://www.nasa.gov/hrp/
- Official NASA Space Apps 2026 challenge brief: https://www.spaceappschallenge.org/2026/challenges/health-monitoring-software/
