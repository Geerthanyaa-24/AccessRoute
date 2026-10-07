import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder
from sklearn.impute import SimpleImputer

def main():
    print("==================================================")
    print("PHASE 2 - MACHINE LEARNING MODEL PIPELINE")
    print("==================================================")
    print("\n1. Loading the real OSM dataset (real_osm_accessibility_data.csv)...")
    try:
        df = pd.read_csv("real_osm_accessibility_data.csv")
    except FileNotFoundError:
        print("Error: 'real_osm_accessibility_data.csv' not found.")
        return

    # 2. TARGET VALIDATION & GENERATION
    print("\n2. Target Validation & Generation...")
    df['Safe'] = df['original_wheelchair'].apply(lambda x: 1 if x in ['yes', 'designated'] else 0)
    df['ramp_available'] = df['original_wheelchair'].apply(lambda x: 1 if x in ['yes', 'designated'] else 0)
    
    # 3. FEATURES AND TARGET
    X = df[['incline_percentage', 'kerb_height_cm', 'original_surface', 'ramp_available', 'tactile_paving_encoded']]
    y = df['Safe']
    
    # Fill NaN strings for OrdinalEncoder
    X = X.copy()
    X['original_surface'] = X['original_surface'].fillna('unknown').astype(str).str.lower()
    
    # 4. TRAIN / TEST SPLIT
    print("\n3. Splitting dataset (80/20, stratify=y)...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
    
    # 5. PREPROCESSING PIPELINE
    num_features = ['incline_percentage', 'kerb_height_cm', 'ramp_available', 'tactile_paving_encoded']
    num_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median'))
    ])
    
    cat_features = ['original_surface']
    
    # Ordinal encoding: mapping categories to specific numbers. Unknown category handles unexpected values.
    # We define the order so it matches our previous logic: dirt=0, unknown=1, paved=2, asphalt=3
    # Any new value gets encoded as -1 (which we can then handle, but here we just map it)
    surface_cats = [['dirt', 'unknown', 'paved', 'asphalt']]
    cat_transformer = Pipeline(steps=[
        ('encoder', OrdinalEncoder(categories=surface_cats, handle_unknown='use_encoded_value', unknown_value=-1))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_transformer, num_features),
            ('cat', cat_transformer, cat_features)
        ])
    
    clf = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42))
    ])
    
    # 6. TRAINING
    print("\n5. Training RandomForestClassifier...")
    clf.fit(X_train, y_train)
    
    # 7. EVALUATION
    y_pred = clf.predict(X_test)
    
    print("\n6. Model Evaluation (Actual Metrics from test set):")
    print(f"Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred, zero_division=0):.4f}")
    print(f"Recall:    {recall_score(y_test, y_pred, zero_division=0):.4f}")
    print(f"F1-score:  {f1_score(y_test, y_pred, zero_division=0):.4f}")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    
    # 8. SERIALIZATION
    print("\n8. Saving complete pipeline (preprocessing + model)...")
    joblib.dump(clf, "accessibility_model.pkl")
    print("Successfully saved to accessibility_model.pkl")

if __name__ == "__main__":
    main()
