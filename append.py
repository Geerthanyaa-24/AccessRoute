with open('backend/main.py', 'a') as f:
    f.write('''

# --- MACHINE LEARNING ENDPOINT ---

import joblib
import pandas as pd
from pydantic import BaseModel
from fastapi import HTTPException

class AccessibilityFeatures(BaseModel):
    incline: float
    kerb_height: float
    surface_type: str
    ramp_available: int
    tactile_paving: int

@app.post("/predict-accessibility")
def predict_accessibility_endpoint(features: AccessibilityFeatures):
    try:
        # Load from parent directory
        import os
        model_path = os.path.join(os.path.dirname(__file__), "..", "accessibility_model.pkl")
        model = joblib.load(model_path)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="ML Model not found.")
        
    surface_mapping = {'unknown': 1, 'dirt': 0, 'paved': 2, 'asphalt': 3}
    surface_encoded = surface_mapping.get(features.surface_type.lower(), 1)
    
    input_df = pd.DataFrame([{
        'incline_percentage': features.incline,
        'kerb_height_cm': features.kerb_height,
        'surface_type_encoded': surface_encoded,
        'ramp_available': features.ramp_available,
        'tactile_paving_encoded': features.tactile_paving
    }])
    
    pred_class = model.predict(input_df)[0]
    proba = model.predict_proba(input_df)[0]
    
    return {
        "prediction": "Safe" if pred_class == 1 else "Unsafe",
        "class": int(pred_class),
        "confidence": round(float(max(proba)), 2)
    }
''')
