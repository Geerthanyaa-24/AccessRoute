import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

# Define output directories
artifact_dir = r"C:\Users\deebi\.gemini\antigravity\brain\07162d55-931e-4ee9-b7b1-72f37aa1245b"
report_dir = os.path.join(artifact_dir, "model_reports")
os.makedirs(report_dir, exist_ok=True)

def main():
    print("Loading prepared dataset...")
    try:
        df = pd.read_csv("ready_for_training.csv")
    except FileNotFoundError:
        print("Error: 'ready_for_training.csv' not found. Please run the data pipeline first.")
        return

    print(f"Dataset loaded. Total records: {len(df)}")

    # 1. Define Features (X) and Target (y)
    # The target is 'is_safe'. We drop 'accessibility_score' because it directly determines 'is_safe'.
    X = df[['incline_percentage', 'kerb_height_cm', 'surface_type_encoded', 'has_ramp_encoded', 'tactile_paving_encoded']]
    y = df['is_safe']

    # 2. Train/Test Split
    print("Splitting data into 80% training and 20% testing sets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # 3. Model Training
    print("Training Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    # 4. Model Evaluation
    print("Evaluating model on test data...")
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    print(f"\n--- Model Accuracy: {acc * 100:.2f}% ---")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # 5. Visualizing the Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False, 
                xticklabels=['Unsafe (0)', 'Safe (1)'], yticklabels=['Unsafe (0)', 'Safe (1)'])
    plt.title('Confusion Matrix')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.savefig(os.path.join(report_dir, "confusion_matrix.png"))
    plt.close()
    
    # 6. Visualizing Feature Importance
    importances = model.feature_importances_
    features = X.columns
    indices = np.argsort(importances)
    
    plt.figure(figsize=(8, 5))
    plt.title('Feature Importances')
    plt.barh(range(len(indices)), importances[indices], color='b', align='center')
    plt.yticks(range(len(indices)), [features[i] for i in indices])
    plt.xlabel('Relative Importance')
    plt.tight_layout()
    plt.savefig(os.path.join(report_dir, "feature_importance.png"))
    plt.close()

    # 7. Save the Model
    print("Saving trained model to 'accessibility_model.pkl'...")
    joblib.dump(model, "accessibility_model.pkl")
    
    print(f"\nTraining Complete! Model saved and evaluation reports generated in: {report_dir}")

if __name__ == "__main__":
    main()
