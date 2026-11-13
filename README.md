# GravityWare v1.2 — Team BigwIN

**GravityWare** is an educational astronaut health and gravity-adaptation monitoring prototype.

## Features
- Dark Streamlit dashboard
- Simulated astronaut health history
- Manual health readings
- Explainable rule-based health alerts
- Gravity Adaptation Monitor (GAM)
- Selectable comparison baseline
- Earth, orbital microgravity, Moon and Mars gravity profiles
- Gravity-related symptom tracking
- Body-system information explorer
- CSV health history and TXT mission report downloads

## Requirements
- Windows, macOS or Linux
- Python 3.10 or newer (Python 3.12/3.13 recommended)

## Run on Windows

1. Extract the ZIP.
2. Open the `GravityWare` folder in VS Code.
3. Open Terminal → New Terminal.
4. Create a virtual environment:

   ```powershell
   python -m venv .venv
   ```

5. Activate it:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use the environment's Python directly:

   ```powershell
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   .venv\Scripts\python.exe -m streamlit run app.py
   ```

6. Install packages:

   ```powershell
   python -m pip install -r requirements.txt
   ```

7. Start the application:

   ```powershell
   python -m streamlit run app.py
   ```

8. Open the local address shown in the terminal, usually http://localhost:8501.

## Project files
- `app.py` — complete Streamlit application
- `requirements.txt` — Python dependencies
- `data/sample_astronaut_data.csv` — example simulated dataset
- `.gitignore` — excludes local environment and cache files

## Demo walkthrough
1. Open Mission Dashboard.
2. View the simulated health summary and GAM indicators.
3. Open Gravity Adaptation and compare the baseline with the latest reading.
4. Select Health Monitoring and add a new reading with symptoms such as dizziness.
5. Open Mission Report and download the CSV/TXT reports.

## Important limitations
- All included sample records are simulated.
- New records are held in Streamlit session state; they are not a permanent database and may be lost when the session restarts.
- Health alerts use simple demonstration rules, not a trained or clinically validated AI model.
- GAM counts selected changes in entered data. It is not a validated medical score and cannot establish that gravity caused a change.
- This software is an educational competition prototype, not a medical device, diagnosis or treatment recommendation. Real emergencies must be handled using qualified medical and mission protocols.

## Research direction
The project is motivated by human spaceflight research topics such as altered gravity, fluid shifts, cardiovascular adaptation, sensorimotor changes, muscle and bone deconditioning, sleep and behavioral health. Cite and verify NASA research sources in the competition submission.
