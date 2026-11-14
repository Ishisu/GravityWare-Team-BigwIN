"""Experimental personal-baseline and unsupervised anomaly screening.

This module is not a diagnostic model and has not been clinically validated.
It intentionally uses only the current signed-in user's saved records.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

MIN_ML_RECORDS = 14
MODEL_FEATURES = ["heart_rate", "systolic_bp", "diastolic_bp", "spo2", "temperature_c", "sleep_hours", "stress_level", "fatigue_level"]
INDICATOR_LABELS = {
    "heart_rate": "Heart rate (bpm)", "systolic_bp": "Systolic blood pressure", "diastolic_bp": "Diastolic blood pressure",
    "spo2": "Blood oxygen (SpO₂)", "temperature_c": "Temperature (°C)", "sleep_hours": "Sleep duration (hours)",
    "stress_level": "Stress self-rating", "fatigue_level": "Fatigue self-rating",
}


def _clean_records(records: pd.DataFrame) -> pd.DataFrame:
    df = records.copy()
    if "record_date" in df:
        df["record_date"] = pd.to_datetime(df["record_date"], errors="coerce")
        df = df.sort_values("record_date").dropna(subset=["record_date"])
    for col in MODEL_FEATURES:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.reset_index(drop=True)


def _robust_change(series: pd.Series, latest: float):
    prior = pd.to_numeric(series, errors="coerce").dropna().astype(float)
    if len(prior) < 3 or not np.isfinite(latest):
        return None
    median = float(prior.median())
    mad = float((prior - median).abs().median())
    # MAD-based scale is robust to a few unusual historic entries.
    scale = 1.4826 * mad
    if scale < 1e-6:
        scale = max(abs(median) * 0.03, 0.5)
    score = (float(latest) - median) / scale
    return {"median": median, "score": score, "prior_count": len(prior)}


def analyze_health_records(records: pd.DataFrame) -> dict:
    df = _clean_records(records)
    if df.empty:
        return {"record_count": 0, "latest": {}, "indicators": [], "findings": [], "ml_available": False, "ml_flag": False, "training_records": 0, "model_features": []}
    latest = df.iloc[-1].to_dict()
    indicators, findings = [], []
    available = [c for c in MODEL_FEATURES if c in df.columns]
    for col in available:
        value = latest.get(col)
        if pd.isna(value):
            continue
        change = _robust_change(df[col].iloc[:-1], float(value))
        if change is None:
            continue
        entry = {"key": col, "label": INDICATOR_LABELS.get(col, col), "latest": float(value), **change}
        indicators.append(entry)
        magnitude = abs(change["score"])
        if magnitude >= 4.0:
            level = "High review priority"
            message = f"Latest value ({value:g}) differs substantially from the personal historical median ({change['median']:g}). Review the entry, context and trend."
        elif magnitude >= 2.8:
            level = "Monitor"
            message = f"Latest value ({value:g}) is noticeably different from the personal historical median ({change['median']:g}). Consider a repeat entry and review recent context."
        elif magnitude >= 2.0:
            level = "Small change"
            message = f"A change from the personal historical median ({change['median']:g}) was detected. Continue observing the trend."
        else:
            continue
        findings.append({"indicator": INDICATOR_LABELS.get(col, col), "level": level, "message": message, "score": round(change["score"], 2)})
    # A combined change is highlighted only when at least two separate indicators
    # have robust deviations; this remains a statistical observation, not triage.
    strong = [x for x in indicators if abs(x["score"]) >= 2.8]
    if len(strong) >= 2:
        findings.insert(0, {"indicator": "Multiple-indicator pattern", "level": "High review priority", "message": f"{len(strong)} indicators differ from their personal historical patterns. Review the combined entries and mission context; this is not a diagnosis."})

    # Isolation Forest is an unsupervised anomaly screen, not a disease classifier.
    # Require 14 usable rows and at least 3 varying features. Latest row is held out.
    usable_cols = [c for c in available if df[c].notna().sum() >= MIN_ML_RECORDS]
    model_frame = df[usable_cols].replace([np.inf, -np.inf], np.nan) if usable_cols else pd.DataFrame()
    ml_available, ml_flag, training_n, model_features = False, False, 0, []
    if len(df) >= MIN_ML_RECORDS and len(usable_cols) >= 3:
        model_frame = model_frame.dropna(axis=0, how="any")
        if len(model_frame) >= MIN_ML_RECORDS and model_frame.iloc[:-1].nunique().ge(2).sum() >= 3:
            try:
                from sklearn.ensemble import IsolationForest
                from sklearn.impute import SimpleImputer
                from sklearn.preprocessing import StandardScaler
                train = model_frame.iloc[:-1]
                test = model_frame.iloc[[-1]]
                imputer = SimpleImputer(strategy="median")
                train_i = imputer.fit_transform(train)
                test_i = imputer.transform(test)
                scaler = StandardScaler()
                train_s = scaler.fit_transform(train_i)
                test_s = scaler.transform(test_i)
                model = IsolationForest(n_estimators=200, contamination=0.10, random_state=42)
                model.fit(train_s)
                ml_flag = bool(model.predict(test_s)[0] == -1)
                ml_available, training_n, model_features = True, len(train), usable_cols
            except Exception:
                # Keep the baseline feature available if ML dependencies or data fail.
                pass
    return {"record_count": len(df), "latest": latest, "indicators": indicators, "findings": findings,
            "ml_available": ml_available, "ml_flag": ml_flag, "training_records": training_n,
            "model_features": model_features}
