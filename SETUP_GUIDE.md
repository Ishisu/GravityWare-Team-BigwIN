# GravityWare v1.3 — Setup and deployment guide

This guide assumes Windows + VS Code and Streamlit Community Cloud.

## Part A — Create the Supabase database

1. Visit https://supabase.com/ and sign in.
2. Click **New project**.
3. Give it a name such as `gravityware-bigwin`.
4. Set a strong database password and save it somewhere safe.
5. Choose a region near your expected users and create the project.
6. Wait for the project to finish provisioning.
7. In the left menu, open **SQL Editor**.
8. Click **New query**.
9. Open `database/setup.sql` in VS Code, copy all its contents, paste into the SQL Editor and click **Run**.
10. Check that the query completed successfully. The `health_records` table should appear in Table Editor.

The SQL enables Row Level Security and creates policies restricting every record to its owning authenticated account.

## Part B — Get Supabase connection details

1. In Supabase, open **Project Settings** (gear icon).
2. Find **API** or **API Keys** (the exact label may vary).
3. Copy the Project URL.
4. Copy the **publishable key** (or legacy `anon` public key).
5. Do NOT copy the `service_role` key or secret key.

## Part C — Configure GravityWare locally

1. Extract the GravityWare v1.3 ZIP.
2. Open the extracted `GravityWare_v1.3` folder in VS Code.
3. Open `.streamlit/secrets.toml.example`.
4. Create a copy in the same folder named exactly `secrets.toml` (inside `.streamlit`).
5. Edit `secrets.toml` so it contains:
   ```
   SUPABASE_URL = "https://YOUR-PROJECT-REF.supabase.co"
   SUPABASE_KEY = "YOUR-PUBLISHABLE-OR-ANON-KEY"
   ```
6. Replace both placeholders with your real values. Do not add the real values to GitHub.
7. Open VS Code Terminal > New Terminal. Make sure terminal is in the `GravityWare_v1.3` project folder.
8. Run:
   ```
   python -m venv .venv
   .venv\Scripts\python.exe -m pip install --upgrade pip
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   .venv\Scripts\python.exe -m streamlit run app.py
   ```
   If `python` is not recognized, use `py -m venv .venv` for the first command.
9. Open the local address shown, usually http://localhost:8501.
10. Use **Create account** to register a test astronaut account. If Supabase email confirmation is enabled, confirm the email before signing in.
11. Add a daily record, then open Health History and Reports to test persistence and exports.
12. Sign out and create a second test account. Confirm it cannot see the first account's records.

## Part D — Upload to GitHub

1. Open your existing GitHub repository or create a new one.
2. Upload the contents of the extracted `GravityWare_v1.3` folder to the repository root.
3. Upload `app.py`, the complete `assets` folder (including `gravityware_logo.png`), `requirements.txt`, `README.md`, `SETUP_GUIDE.md`, `.gitignore`, `database/setup.sql`, `.streamlit/secrets.toml.example`, and `data/sample_astronaut_data.csv`.
4. Do NOT upload `.venv` or `.streamlit/secrets.toml`.
5. Commit the files to your deployment branch (usually `main`).

If you are replacing the earlier v1.2 project, ensure `app.py` and `requirements.txt` at the repository root are the v1.3 versions. Keep the SQL setup file in `database/setup.sql`.

## Part E — Deploy on Streamlit Community Cloud

1. Visit https://share.streamlit.io/ and sign in with GitHub.
2. Choose **Deploy an app** → **Deploy now**.
3. Select your GitHub repository.
4. Branch: `main` (or the actual branch name shown on GitHub).
5. Main file path: `app.py`.
6. Choose an app URL if available.
7. Open **Advanced settings** if needed and leave Python version on the supported default.
8. Click **Deploy**.
9. When the app starts, open its app menu / settings and choose **Edit secrets**.
10. Paste the following, using the same actual values as your local secrets:
    ```
    SUPABASE_URL = "https://YOUR-PROJECT-REF.supabase.co"
    SUPABASE_KEY = "YOUR-PUBLISHABLE-OR-ANON-KEY"
    ```
11. Save secrets and reboot the app if prompted.

The app cannot connect to Supabase until cloud secrets are configured.

## Part F — Final test checklist

- [ ] App opens on its Streamlit URL.
- [ ] New astronaut account can be created.
- [ ] Email confirmation works if enabled.
- [ ] User can sign in and sign out.
- [ ] Daily health record saves.
- [ ] Refreshing/reopening the app does not erase the record.
- [ ] Health History displays the saved record.
- [ ] PDF download opens.
- [ ] CSV download opens.
- [ ] A second account cannot see the first account's records.

## Troubleshooting

**"Supabase is not configured"**
- Check that `.streamlit/secrets.toml` exists locally or Streamlit Cloud > Edit secrets is configured.
- Check spelling and quotes around both values.

**"Invalid API key" / connection errors**
- Use the Project URL and publishable key (or legacy anon key), not service_role.
- Make sure there are no extra spaces or line breaks.

**Account created but cannot sign in**
- Check the email confirmation message. Supabase may require email confirmation before login.
- For a quick competition test, review Supabase Authentication > Providers > Email settings. Disabling confirmation makes test signups immediate but reduces account verification; enable it again for a public deployment.

**"relation health_records does not exist"**
- Run all of `database/setup.sql` in the Supabase SQL Editor.

**"permission denied" / RLS error**
- Confirm the SQL ran successfully and RLS policies exist.
- Do not turn RLS off. The signed-in user token is required for access.

**Duplicate record**
- The database allows one record per user ID + astronaut ID + date. Choose another date or review the existing entry.

## Important privacy and safety statement
This is an educational competition prototype. Do not enter real astronaut medical data or other sensitive health information. Do not rely on the app for medical decisions, diagnosis or emergency response. Use simulated or specifically authorized demonstration data only.
