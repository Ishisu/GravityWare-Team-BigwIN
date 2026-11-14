# GravityWare — Setup and deployment guide

This guide covers the Team BigwIN GravityWare Streamlit prototype on Windows / VS Code and Streamlit Community Cloud.

## 1. Important: existing Supabase project

If you are continuing with the existing GravityWare Supabase project and its astronaut accounts, **do not run either SQL file again**:

- `database/setup.sql`
- `database/collaboration_setup_v1_7_4.sql`

They are initial setup scripts. Rerunning database scripts against an already configured project is not part of normal installation and may affect existing policies or objects. Back up the database before any future schema or security changes.

## 2. Configure local secrets

1. Open the extracted `GravityWare_v1.7_Team_BigwIN` project folder in VS Code.
2. Open `.streamlit/secrets.toml.example`.
3. Make a copy named `secrets.toml` in the same `.streamlit` folder.
4. Enter your own Supabase Project URL and publishable key (or legacy anon key):

```toml
SUPABASE_URL = "https://YOUR-PROJECT-REF.supabase.co"
SUPABASE_KEY = "YOUR-PUBLISHABLE-OR-ANON-KEY"
```

5. Save the file. Do not paste secrets into chat, screenshots, source control, or public project submissions.
6. Never use a Supabase `service_role` key or secret key in this Streamlit app.

## 3. Install and run on Windows

Open VS Code Terminal in the folder containing `app.py`. Run these commands one at a time:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

If you already created `.venv` and installed requirements for this project, you only need the final command to launch it. Keep the terminal open while using the app. Open the local URL printed by Streamlit, normally `http://localhost:8501`.

If `py -3.13` is unavailable, use the Python launcher/version installed on your computer to create the environment.

## 4. Streamlit Community Cloud deployment

1. Push the project files to a GitHub repository.
2. Do not upload `.streamlit/secrets.toml`, passwords, private keys, `.venv`, or `__pycache__`.
3. Open https://share.streamlit.io/ and sign in with GitHub.
4. Choose the repository and branch; set the main file path to `app.py`.
5. Deploy the app.
6. In the app's Streamlit Cloud settings, open **Secrets** and enter the same `SUPABASE_URL` and `SUPABASE_KEY` values in TOML format.
7. Save and reboot if prompted.

## 5. Reviewer collaboration setup

Read `COLLABORATION_SETUP_GUIDE.md` before assigning doctor or Mission Control roles. Reviewer access is assigned by an administrator through Supabase. Do not grant reviewer roles to astronaut accounts unless that is intentionally required for a controlled demonstration.

## 6. Final functional checks

- [ ] App starts and sign-in works.
- [ ] Each astronaut sees their own profile and health records.
- [ ] Daily Health Log saves a record.
- [ ] Health History displays saved records.
- [ ] CSV import preview and import work with synthetic data.
- [ ] Early Warning AI and Gravity-Aware Assessment pages load.
- [ ] Gravity Health Education and Gravity Adaptation pages load.
- [ ] PDF and CSV reports download and open.
- [ ] Astronaut medical-review request is visible to the authorized doctor.
- [ ] Doctor assessment is visible to Mission Control and the astronaut.
- [ ] Mission Control decision is visible to the astronaut.
- [ ] Cross-astronaut record visibility is checked with separate demo accounts.

## 7. Security, privacy and scientific limitations

Use fictional astronaut profiles and synthetic or explicitly authorized demonstration data only. This prototype is not designed or certified for protected health information, diagnosis, treatment, fitness-for-duty decisions, or emergency response.

The gravity comparisons are educational and experimental, not validated clinical thresholds. Known microgravity observations must not be presented as proven long-duration health outcomes for Moon or Mars gravity. NASA material is research context; GravityWare does not connect to NASA systems or ingest NASA astronaut telemetry.

Application-level tests are not a substitute for independent Supabase RLS, privilege, and penetration testing. Do not describe the prototype as production-secure or clinically validated.
