# GravityWare v1.3 — Team BigwIN

**Understanding Health Beyond Earth**

GravityWare v1.3 is a Streamlit educational prototype for astronaut daily health logging, personal trend review and gravity-adaptation comparisons.

## What's new in v1.3
- Individual email/password account registration and sign-in using Supabase Auth
- Permanent PostgreSQL health records in Supabase
- Row Level Security (RLS): each signed-in user can only read/write their own records
- One daily record per astronaut ID per date
- Daily entry, health history, dashboard charts and baseline comparison
- Date-range PDF and CSV report downloads

## Project structure
```
GravityWare_v1.3/
├── app.py
├── assets/
│   └── gravityware_logo.png
├── requirements.txt
├── README.md
├── SETUP_GUIDE.md
├── .gitignore
├── .streamlit/
│   └── secrets.toml.example
├── database/
│   └── setup.sql
└── data/
    └── sample_astronaut_data.csv
```

## Quick start
1. Create a Supabase project.
2. Run `database/setup.sql` in Supabase SQL Editor.
3. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
4. Put your Supabase Project URL and **publishable/anon key** in the secrets file.
5. In the project terminal run:
   ```
   python -m venv .venv
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   .venv\Scripts\python.exe -m streamlit run app.py
   ```
6. Create an astronaut account in the app and sign in.

See `SETUP_GUIDE.md` for full local and Streamlit Community Cloud deployment instructions.

## Security notes
- Do not commit `.streamlit/secrets.toml`.
- Use the Supabase publishable/anon key with RLS policies enabled. Never use the Supabase `service_role` or secret key in this Streamlit app.
- Do not collect real astronaut medical data. This competition prototype is not designed or certified for protected health information.
- Email confirmation may be enabled by default in Supabase Auth. If enabled, users must confirm their email before signing in.
- Use a strong, unique password. For a real production service, add stronger account lifecycle, audit, operational and security controls.

## Scientific limitations
Gravity Adaptation comparisons are descriptive and experimental, not a validated clinical score. They cannot prove gravity caused an observed change. Sample records are simulated. This app is not a medical device, diagnostic system or substitute for qualified medical/mission protocols.
