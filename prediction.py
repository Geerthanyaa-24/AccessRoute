import joblib
import pandas as pd

def predict_accessibility(incline, kerb_height, surface_type, ramp_available, tactile_paving):
    """
    Predicts if a route segment is Safe or Unsafe for wheelchair users.
    """
    try:
        pipeline = joblib.load("accessibility_model.pkl")
    except FileNotFoundError:
        return {"error": "Model not found. Please train the model first."}
    
    # Create feature dataframe EXACTLY as expected by the pipeline
    features = pd.DataFrame([{
        'incline_percentage': float(incline),
        'kerb_height_cm': float(kerb_height),
        'original_surface': str(surface_type).lower(),
        'ramp_available': int(ramp_available),
        'tactile_paving_encoded': int(tactile_paving)
    }])
    
    prediction_class = pipeline.predict(features)[0]
    probabilities = pipeline.predict_proba(features)[0]
    confidence = float(max(probabilities))
    
    return {
        "prediction": "Safe" if prediction_class == 1 else "Unsafe",
        "class": int(prediction_class),
        "confidence": round(confidence, 2)
    }

if __name__ == "__main__":
    # Test the prediction function
    print("Testing Safe Prediction (Ramp Available, Low Incline):")
    result = predict_accessibility(4.5, 2, "paved", 1, 1)
    print(result)
    
    print("\nTesting Unsafe Prediction (No Ramp, High Kerb):")
    result = predict_accessibility(12.0, 15.0, "dirt", 0, 0)
    print(result)
