import joblib
import pandas as pd

def predict_accessibility(incline, kerb_height, surface_type, ramp_available, tactile_paving):
    """
    Predicts if a route segment is Safe or Unsafe for wheelchair users.
    """
    try:
        model = joblib.load("accessibility_model.pkl")
    except FileNotFoundError:
        return {"error": "Model not found. Please train the model first."}
    
    # Encode surface type similar to training phase
    surface_mapping = {'unknown': 1, 'dirt': 0, 'paved': 2, 'asphalt': 3}
    surface_encoded = surface_mapping.get(str(surface_type).lower(), 1)
    
    # Create feature dataframe
    features = pd.DataFrame([{
        'incline_percentage': float(incline),
        'kerb_height_cm': float(kerb_height),
        'surface_type_encoded': surface_encoded,
        'ramp_available': int(ramp_available),
        'tactile_paving_encoded': int(tactile_paving)
    }])
    
    prediction_class = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    confidence = float(max(probabilities))
    
    return {
        "prediction": "Safe" if prediction_class == 1 else "Unsafe",
        "class": int(prediction_class),
        "confidence": round(confidence, 2)
    }

if __name__ == "__main__":
    # Test the prediction function
    result = predict_accessibility(4.5, 2, "paved", 1, 1)
    print("Test Prediction:")
    print(result)
