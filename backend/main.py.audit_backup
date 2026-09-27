from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import os

app = FastAPI(title="Accessibility Navigation API")

# Configure CORS for the React frontend (running on Vite's port 5173 or 5174)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for data and model
df = None
model = None

# Input schema for ML prediction
class RouteFeatures(BaseModel):
    incline_percentage: float
    kerb_height_cm: float
    surface_type_encoded: int
    has_ramp_encoded: int
    tactile_paving_encoded: int

import joblib

@app.on_event("startup")
def load_data_and_model():
    global df, model
    
    # Load Dataset for Metrics
    csv_path = os.path.join(os.path.dirname(__file__), "..", "ready_for_training.csv")
    try:
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} records for metrics dashboard.")
    except FileNotFoundError:
        print("Warning: ready_for_training.csv not found. Metrics will be disabled.")

    # Load Pre-Trained ML Model
    model_path = os.path.join(os.path.dirname(__file__), "..", "accessibility_model.pkl")
    try:
        model = joblib.load(model_path)
        print("Pre-trained Machine Learning model loaded successfully!")
    except FileNotFoundError:
        print("Warning: accessibility_model.pkl not found. ML Prediction endpoint will be disabled.")

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Backend is running!"}

@app.get("/api/metrics/overview")
def get_metrics_overview():
    if df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    total_places = len(df)
    safe_places = int(df['is_safe'].sum())
    avg_score = float(df['accessibility_score'].mean())
    
    # Calculate % for the donut chart
    high_pct = float(len(df[df['accessibility_score'] >= 80]) / total_places * 100)
    mod_pct = float(len(df[(df['accessibility_score'] >= 50) & (df['accessibility_score'] < 80)]) / total_places * 100)
    low_pct = float(len(df[df['accessibility_score'] < 50]) / total_places * 100)

    return {
        "total_nodes_analyzed": total_places,
        "safe_nodes": safe_places,
        "average_accessibility_score": round(avg_score, 1),
        "distribution": {
            "highly_accessible_pct": round(high_pct, 1),
            "moderate_pct": round(mod_pct, 1),
            "low_pct": round(low_pct, 1)
        }
    }

@app.post("/api/routes/compare")
def compare_routes(start: str, destination: str):
    """
    Returns multiple route variations (Shortest, Safest, Most Accessible, Balanced) 
    with granular accessibility and safety metrics for each.
    """
    # Simulated coordinates for a connected functional demonstration
    # (Since OSMnx routing is blocked by Windows AppLocker DLL policy)
    
    base_coords = [
        [13.06, 80.23], [13.062, 80.235], [13.065, 80.24]
    ]
    alt_coords = [
        [13.06, 80.23], [13.055, 80.24], [13.065, 80.24]
    ]
    
    routes = [
        {
            "id": "shortest",
            "name": "Shortest Route",
            "color": "#64748B", # Slate
            "coordinates": base_coords,
            "metrics": {
                "accessibility_score": 68,
                "safety_score": 55,
                "slope_pct": 8.5,
                "obstacles": 4,
                "confidence": 92,
                "distance_m": 850,
                "time_mins": 12
            }
        },
        {
            "id": "safest",
            "name": "Safest Route",
            "color": "#3B82F6", # Blue
            "coordinates": alt_coords,
            "metrics": {
                "accessibility_score": 85,
                "safety_score": 95,
                "slope_pct": 2.1,
                "obstacles": 0,
                "confidence": 88,
                "distance_m": 1200,
                "time_mins": 18
            }
        },
        {
            "id": "balanced",
            "name": "Balanced Route (Recommended)",
            "color": "#10B981", # Emerald
            "coordinates": [[13.06, 80.23], [13.06, 80.238], [13.065, 80.24]],
            "metrics": {
                "accessibility_score": 82,
                "safety_score": 85,
                "slope_pct": 4.8,
                "obstacles": 1,
                "confidence": 95,
                "distance_m": 950,
                "time_mins": 14
            }
        }
    ]
    
    return {
        "status": "success",
        "start": start,
        "destination": destination,
        "routes": routes
    }

@app.post("/api/predict/safety")
def predict_safety(features: RouteFeatures):
    if model is None:
        raise HTTPException(status_code=500, detail="Machine Learning model is not initialized.")
    
    # Convert input to DataFrame for the model
    input_df = pd.DataFrame([features.dict()])
    
    # Predict
    prediction = int(model.predict(input_df)[0])
    probability = float(model.predict_proba(input_df)[0][1])
    
    return {
        "is_safe": bool(prediction),
        "safety_probability": round(probability * 100, 2),
        "message": "Path is deemed accessible." if prediction else "Warning: This path is unsafe for wheelchairs."
    }
