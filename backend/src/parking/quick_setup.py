"""
Quick setup script for parking module
Trains lightweight models with subset of data for demo purposes
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import sys
sys.path.append('.')

from parking_preprocess import (
    load_parking_data,
    engineer_features,
    prepare_random_forest_data,
    save_preprocessing_objects
)
from parking_rf_model import save_rf_model


def quick_train():
    """Quick training with subset of data"""
    print("="*60)
    print("QUICK PARKING MODEL SETUP")
    print("="*60)
    
    # Load data
    print("\n1. Loading data...")
    df = load_parking_data()
    print(f"   ✓ Total records: {len(df)}")
    
    # Use subset (last 30 days only for speed)
    df = df.sort_values('timestamp')
    df = df.tail(len(df) // 6)  # Use ~17% of data
    print(f"   ✓ Using subset: {len(df)} records")
    
    # Engineer features
    print("\n2. Engineering features...")
    df = engineer_features(df)
    print("   ✓ Features engineered")
    
    # Prepare for Random Forest only (skip LSTM for speed)
    print("\n3. Preparing Random Forest data...")
    X, y, scaler, encoder, feature_cols = prepare_random_forest_data(df)
    print(f"   ✓ Features: {X.shape}, Targets: {y.shape}")
    
    # Split
    print("\n4. Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"   ✓ Train: {len(X_train)}, Test: {len(X_test)}")
    
    # Train Random Forest (smaller, faster)
    print("\n5. Training Random Forest (simplified)...")
    model = RandomForestClassifier(
        n_estimators=100,  # Reduced from 200
        max_depth=15,       # Reduced from 20
        min_samples_split=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    print("   ✓ Training complete")
    
    # Evaluate
    print("\n6. Evaluating...")
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    print(f"   ✓ Train Accuracy: {train_score*100:.2f}%")
    print(f"   ✓ Test Accuracy: {test_score*100:.2f}%")
    
    # Save
    print("\n7. Saving models...")
    save_rf_model(model, "../../models/parking_rf_model.pkl")
    save_preprocessing_objects(scaler, encoder)
    joblib.dump(feature_cols, "../../models/parking_feature_cols.pkl")
    print("   ✓ All models saved")
    
    # Create dummy LSTM model marker
    with open("../../models/parking_lstm_model.h5", 'w') as f:
        f.write("# LSTM model placeholder - using RF only for demo\n")
    
    print("\n" + "="*60)
    print("✓ QUICK SETUP COMPLETE!")
    print("="*60)
    print("\nModels saved:")
    print("  - models/parking_rf_model.pkl")
    print("  - models/parking_rf_scaler.pkl")
    print("  - models/parking_encoder.pkl")
    print("  - models/parking_feature_cols.pkl")
    print("\nReady for API testing!")


if __name__ == "__main__":
    quick_train()
