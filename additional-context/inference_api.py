"""FastAPI service for cardio disease prediction using pre-trained model artifacts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, PositiveInt

MODEL_PATH = Path("rf_cardio_model.joblib")
SCALER_PATH = Path("scaler_cardio.joblib")
FEATURES_PATH = Path("features.json")

if not MODEL_PATH.exists() or not SCALER_PATH.exists() or not FEATURES_PATH.exists():
    missing = [
        str(path)
        for path in (MODEL_PATH, SCALER_PATH, FEATURES_PATH)
        if not path.exists()
    ]
    raise RuntimeError(
        "Missing required artifact(s): " + ", ".join(missing)
    )

rf_model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
with FEATURES_PATH.open("r", encoding="utf-8") as fh:
    FEATURE_ORDER = json.load(fh)


class PredictionRequest(BaseModel):
    age: PositiveInt = Field(..., le=120, description="Age in years")
    gender: int = Field(2, ge=1, le=2, description="1 = female, 2 = male")
    height: PositiveInt = Field(..., ge=120, le=230, description="Height in centimeters")
    weight: float = Field(..., ge=25, le=250, description="Weight in kilograms")
    ap_hi: PositiveInt = Field(..., ge=60, le=250, description="Systolic blood pressure")
    ap_lo: PositiveInt = Field(..., ge=40, le=180, description="Diastolic blood pressure")
    cholesterol: int = Field(1, ge=1, le=3, description="1=normal, 2=above normal, 3=well above")
    gluc: int = Field(1, ge=1, le=3, description="1=normal, 2=above normal, 3=well above")
    smoke: int = Field(0, ge=0, le=1)
    alco: int = Field(0, ge=0, le=1)
    active: int = Field(1, ge=0, le=1)

    class Config:
        json_schema_extra = {
            "example": {
                "age": 45,
                "gender": 2,
                "height": 170,
                "weight": 72.5,
                "ap_hi": 130,
                "ap_lo": 85,
                "cholesterol": 2,
                "gluc": 1,
                "smoke": 0,
                "alco": 0,
                "active": 1,
            }
        }


app = FastAPI(
    title="Cardio Disease Prediction API",
    description="Serve predictions from the rf_cardio_model.joblib artifact",
    version="1.0.0",
)


def _prepare_features(payload: PredictionRequest) -> pd.DataFrame:
    data: Dict[str, Any] = payload.dict()
    df = pd.DataFrame([data])

    # Feature engineering identical to training pipeline
    df["age_years"] = df["age"].astype(int)
    df["bmi"] = df["weight"] / ((df["height"] / 100) ** 2)
    df["bp_diff"] = df["ap_hi"] - df["ap_lo"]
    df["age_cat"] = pd.cut(
        df["age_years"],
        bins=[0, 30, 45, 60, 200],
        labels=["<30", "30-45", "45-60", "60+"],
        include_lowest=True,
        right=True,
    )

    # Encoding
    df["gender"] = df["gender"].astype(int)
    df["gender_male"] = (df["gender"] == 2).astype(int)
    df = pd.get_dummies(df, columns=["cholesterol", "gluc", "age_cat"], drop_first=True)

    # Drop columns not used during training
    df = df.drop(columns=["age", "gender"], errors="ignore")

    # Ensure all expected columns exist
    for col in FEATURE_ORDER:
        if col not in df.columns:
            df[col] = 0

    df = df[FEATURE_ORDER].astype(float)
    return df


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok", "model": str(MODEL_PATH.name)}


@app.post("/predict")
def predict(payload: PredictionRequest) -> Dict[str, Any]:
    try:
        features = _prepare_features(payload)
        scaled = scaler.transform(features)
        preds = rf_model.predict(scaled)
        proba = rf_model.predict_proba(scaled)[0, 1]
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "prediction": int(preds[0]),
        "probability": float(proba),
        "features": {
            "ordered": FEATURE_ORDER,
            "scaled": dict(zip(FEATURE_ORDER, np.round(scaled[0], 6))),
        },
    }


@app.get("/")
def root() -> Dict[str, str]:
    return {
        "message": "Cardio disease prediction service",
        "docs": "/docs",
        "health": "/health",
    }
