import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import os

# Define output directories
artifact_dir = r"C:\Users\deebi\.gemini\antigravity\brain\07162d55-931e-4ee9-b7b1-72f37aa1245b"
eda_dir = os.path.join(artifact_dir, "eda_reports")
os.makedirs(eda_dir, exist_ok=True)

def main():
    print("Loading data...")
    try:
        df = pd.read_csv("accessibility_routing_data.csv")
    except FileNotFoundError:
        print("Dataset not found. Please ensure 'accessibility_routing_data.csv' is in the current directory.")
        return

    # --- 1. DATA CLEANING ---
    print("Performing Data Cleaning...")
    # Cap extreme inclines at 20% (assuming anything above is either an error or treated uniformly as a cliff)
    df['incline_percentage'] = df['incline_percentage'].clip(upper=20.0)
    
    # Handle missing values (if any)
    df.fillna({'kerb_height_cm': 0.0}, inplace=True)
    
    # --- 2. EXPLORATORY DATA ANALYSIS (EDA) ---
    print("Generating EDA Reports...")
    sns.set_theme(style="whitegrid")
    
    # Plot 1: Accessibility Score Distribution
    plt.figure(figsize=(8, 5))
    sns.histplot(df['accessibility_score'], bins=20, kde=True, color='#3182CE')
    plt.title('Distribution of Accessibility Scores', fontsize=14)
    plt.xlabel('Accessibility Score (0-100)')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(os.path.join(eda_dir, "score_distribution.png"))
    plt.close()

    # Plot 2: Correlation Heatmap
    # We only correlate numerical/boolean features
    corr_cols = ['incline_percentage', 'has_ramp', 'kerb_height_cm', 'tactile_paving', 'accessibility_score']
    corr_df = df[corr_cols].copy()
    corr_df['has_ramp'] = corr_df['has_ramp'].astype(int)
    corr_df['tactile_paving'] = corr_df['tactile_paving'].astype(int)
    
    plt.figure(figsize=(8, 6))
    correlation = corr_df.corr()
    sns.heatmap(correlation, annot=True, cmap="coolwarm", fmt=".2f", linewidths=.5)
    plt.title('Feature Correlation Heatmap', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(eda_dir, "correlation_heatmap.png"))
    plt.close()

    # Plot 3: Surface Type vs Accessibility Score
    plt.figure(figsize=(10, 5))
    sns.boxplot(data=df, x='surface_type', y='accessibility_score', palette='Set2')
    plt.title('Accessibility Score by Surface Type', fontsize=14)
    plt.xlabel('Surface Type')
    plt.ylabel('Accessibility Score')
    plt.tight_layout()
    plt.savefig(os.path.join(eda_dir, "surface_vs_score.png"))
    plt.close()

    # --- 3. DATA PREPARATION (Ready for Training) ---
    print("Preparing data for model training...")
    
    # Feature Engineering: Create binary target 'is_safe' (Score >= 60 is Safe)
    df['is_safe'] = (df['accessibility_score'] >= 60).astype(int)
    
    # Encoding Categorical Variables
    le = LabelEncoder()
    df['surface_type_encoded'] = le.fit_transform(df['surface_type'])
    df['has_ramp_encoded'] = df['has_ramp'].astype(int)
    df['tactile_paving_encoded'] = df['tactile_paving'].astype(int)
    
    # Drop non-predictive or redundant columns for the final training set
    features_to_drop = ['node_id', 'surface_type', 'has_ramp', 'tactile_paving']
    model_df = df.drop(columns=features_to_drop)
    
    # Split into features (X) and target (y)
    # If the user wants to train a model to predict 'accessibility_score' or 'is_safe'
    X = model_df.drop(columns=['accessibility_score', 'is_safe'])
    y_reg = model_df['accessibility_score']  # Target for Regression
    y_cls = model_df['is_safe']              # Target for Classification
    
    # Train/Test Split (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y_cls, test_size=0.2, random_state=42)
    
    # Save the processed, ready-to-train dataset
    model_df.to_csv("ready_for_training.csv", index=False)
    
    print(f"Data Pipeline Complete!")
    print(f"- Saved {len(model_df)} cleaned records to 'ready_for_training.csv'")
    print(f"- EDA visual reports saved in {eda_dir}")
    print(f"- Split dataset: {len(X_train)} training samples, {len(X_test)} testing samples.")

if __name__ == "__main__":
    main()
