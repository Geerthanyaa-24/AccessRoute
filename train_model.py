import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import joblib
import os

def main():
    print("1. Loading the 419 real OSM data points...")
    df = pd.read_csv("real_osm_accessibility_data.csv")
    
    print("\n2. Cleaning and Preprocessing...")
    # Map raw features to the requested features
    # Input features required: incline percentage, kerb height, surface type, ramp availability, tactile paving
    
    # 2.1 Handle Target Column (Safe/Unsafe)
    # The current 'is_safe' in the CSV is all 0 because the previous rule required surface_score >= 2, but all OSM data in Chennai lacked surface tags (unknown).
    # We will redefine 'is_safe' strictly based on the OSM 'wheelchair' tag which is the ground truth.
    # Safe = 1 (if wheelchair='yes' or 'designated'), Unsafe = 0 (if 'no', 'limited', or 'unknown')
    df['Safe'] = df['original_wheelchair'].apply(lambda x: 1 if x in ['yes', 'designated'] else 0)
    
    print("Class distribution of derived Safe (1) / Unsafe (0):")
    print(df['Safe'].value_counts())
    
    # 2.2 Encode Categorical Features
    # Surface type is 'unknown' for all, but we'll encode it using pandas get_dummies or a mapping for consistency.
    surface_mapping = {'unknown': 1, 'dirt': 0, 'paved': 2, 'asphalt': 3}
    df['surface_type_encoded'] = df['original_surface'].map(surface_mapping).fillna(1)
    
    # Ramp availability (from original_wheelchair)
    df['ramp_available'] = df['original_wheelchair'].apply(lambda x: 1 if x in ['yes', 'designated'] else 0)
    
    # Features X and Target y
    X = df[['incline_percentage', 'kerb_height_cm', 'surface_type_encoded', 'ramp_available', 'tactile_paving_encoded']]
    y = df['Safe']
    
    # 3. Train/Test Split
    print("\n3. Splitting dataset (80/20, stratify=y)...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 4. Train RandomForestClassifier
    print("\n4. Training RandomForestClassifier...")
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    
    # 5. Evaluate
    print("\n5. Evaluation Results:")
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1-score:  {f1:.4f}")
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # 6. Feature Importance
    print("\n6. Feature Importance:")
    importances = model.feature_importances_
    for feature, imp in zip(X.columns, importances):
        print(f" - {feature}: {imp:.4f}")
        
    # 7. Save Pipeline
    print("\n7. Saving model pipeline...")
    joblib.dump(model, "accessibility_model.pkl")
    print("Saved to accessibility_model.pkl")

if __name__ == "__main__":
    main()
