import joblib
import pandas as pd
import os

# 1. Load ML Pipeline at Module Level
_ml_pipeline = None
try:
    model_path = os.path.join(os.path.dirname(__file__), "..", "accessibility_model.pkl")
    _ml_pipeline = joblib.load(model_path)
except Exception:
    pass

def assess_ml_safety(features: dict) -> dict:
    """Predicts safety using the trained RandomForest Pipeline."""
    if not _ml_pipeline:
        return {"prediction": "Unknown", "class": -1, "confidence": 0.0}
        
    input_df = pd.DataFrame([{
        'incline_percentage': float(features.get('incline', 0.0)),
        'kerb_height_cm': float(features.get('kerb_height', 0.0)),
        'original_surface': str(features.get('surface', 'unknown')).lower(),
        'ramp_available': 1 if features.get('has_ramp') else 0,
        'tactile_paving_encoded': 1 if features.get('tactile_paving') else 0
    }])
    
    pred_class = _ml_pipeline.predict(input_df)[0]
    proba = _ml_pipeline.predict_proba(input_df)[0]
    
    return {
        "prediction": "Safe" if pred_class == 1 else "Unsafe",
        "class": int(pred_class),
        "confidence": round(float(max(proba)), 2)
    }

def calculate_accessibility_score(features: dict) -> dict:
    """
    Transparent scoring engine for accessibility incorporating ML & CV signals.
    """
    # Base Weights (Configurable)
    WEIGHT_SURFACE = 20
    WEIGHT_SLOPE = 30
    WEIGHT_OBSTACLE = 30
    WEIGHT_INFRA = 20
    
    # 1. Surface Score
    surface = features.get('surface', 'unknown').lower()
    surface_scores = {
        'asphalt': WEIGHT_SURFACE, 'concrete': WEIGHT_SURFACE, 
        'paving_stones': 15, 'cobblestone': 5, 
        'dirt': 2, 'gravel': 2, 'unknown': 10
    }
    surface_score = surface_scores.get(surface, 10)
    
    # 2. Slope Score
    slope = abs(features.get('incline', 0.0))
    if slope <= 2.0: slope_score = WEIGHT_SLOPE
    elif slope <= 5.0: slope_score = 20
    elif slope <= 8.0: slope_score = 10
    else: slope_score = 0
        
    # 3. Obstacle Score (Includes CV Detection / Community Reports)
    obstacles = int(features.get('obstacle_count', 0))
    if obstacles == 0: obstacle_score = WEIGHT_OBSTACLE
    elif obstacles == 1: obstacle_score = 15
    elif obstacles == 2: obstacle_score = 5
    else: obstacle_score = 0
        
    # 4. Infrastructure
    ramp_score = 10 if features.get('has_ramp', False) else 0
    tactile_score = 10 if features.get('tactile_paving', False) else 0
    infra_score = ramp_score + tactile_score
    
    # 5. ML SAFETY PREDICTION INTEGRATION
    ml_assessment = assess_ml_safety(features)
    
    # Calculate Total Score
    total_score = surface_score + slope_score + obstacle_score + infra_score
    
    # Apply ML Penalty if explicitly Unsafe
    if ml_assessment["class"] == 0 and ml_assessment["confidence"] > 0.70:
        total_score = max(0, total_score - 20) # Apply 20pt penalty for unsafe ML prediction
        
    return {
        "overall_score": total_score,
        "ml_assessment": ml_assessment,
        "components": {
            "surface_score": surface_score,
            "slope_score": slope_score,
            "obstacle_score": obstacle_score,
            "infrastructure_score": infra_score,
            "ramp_score": ramp_score,
            "tactile_score": tactile_score
        }
    }

def calculate_safety_score(features: dict) -> dict:
    """
    Separate safety score focusing purely on danger levels + ML/CV input.
    """
    score = 100
    penalties = []
    
    # Physical/CV Obstacles
    obstacles = int(features.get('obstacle_count', 0))
    if obstacles > 0:
        score -= (obstacles * 15)
        penalties.append(f"{obstacles} physical obstacles detected.")
        
    # Slope Danger
    slope = abs(features.get('incline', 0.0))
    if slope > 8.0:
        score -= 30
        penalties.append(f"Dangerously steep slope ({slope}%).")
        
    # Surface Danger
    surface = features.get('surface', 'unknown').lower()
    if surface in ['cobblestone', 'dirt', 'gravel']:
        score -= 20
        penalties.append(f"Unsafe surface type: {surface}.")
        
    # ML Prediction penalty
    ml_assessment = assess_ml_safety(features)
    if ml_assessment["class"] == 0:
        penalty = int(25 * ml_assessment["confidence"])
        score -= penalty
        penalties.append(f"ML Model predicts Unsafe path (Confidence: {ml_assessment['confidence']}).")
        
    score = max(0, score) # Clamp at 0
    
    return {
        "safety_score": score,
        "penalties": penalties,
        "ml_confidence": ml_assessment["confidence"]
    }
