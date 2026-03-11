"""
Train both LSTM and Random Forest models for parking prediction
"""
import numpy as np
from sklearn.model_selection import train_test_split
import joblib

from parking_preprocess import (
    load_parking_data,
    engineer_features,
    prepare_lstm_sequences,
    prepare_random_forest_data,
    save_preprocessing_objects
)
from parking_lstm_model import build_parking_lstm, get_callbacks
from parking_rf_model import build_parking_rf, save_rf_model, get_feature_importance


def train_lstm_model():
    """Train LSTM model for occupancy prediction"""
    print("\n" + "=" * 60)
    print("TRAINING LSTM MODEL")
    print("=" * 60)
    
    # Load and preprocess data
    print("\n1. Loading data...")
    df = load_parking_data()
    df = engineer_features(df)
    print(f"   ✓ Loaded {len(df)} records")
    
    # Prepare sequences
    print("\n2. Preparing sequences...")
    X, y, parking_ids = prepare_lstm_sequences(df, sequence_length=24)
    print(f"   ✓ Sequences shape: {X.shape}")
    print(f"   ✓ Targets shape: {y.shape}")
    
    # Normalize targets (0-100 scale)
    y_normalized = y / 100.0
    
    # Split data
    print("\n3. Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_normalized, test_size=0.2, random_state=42
    )
    print(f"   ✓ Train: {len(X_train)}, Test: {len(X_test)}")
    
    # Build model
    print("\n4. Building LSTM model...")
    model = build_parking_lstm(sequence_length=24, n_features=X.shape[2])
    print(f"   ✓ Model created")
    
    # Train model
    print("\n5. Training...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=50,
        batch_size=64,
        callbacks=get_callbacks(),
        verbose=1
    )
    
    # Evaluate
    print("\n6. Evaluating...")
    loss, mae, mse = model.evaluate(X_test, y_test, verbose=0)
    print(f"   ✓ Test Loss: {loss:.4f}")
    print(f"   ✓ Test MAE: {mae*100:.2f}% (occupancy points)")
    print(f"   ✓ Test MSE: {mse:.4f}")
    
    # Save model
    print("\n7. Saving model...")
    model.save("../../models/parking_lstm_model.h5")
    print("   ✓ Saved to models/parking_lstm_model.h5")
    
    return model, history


def train_random_forest():
    """Train Random Forest model for availability classification"""
    print("\n" + "=" * 60)
    print("TRAINING RANDOM FOREST MODEL")
    print("=" * 60)
    
    # Load and preprocess data
    print("\n1. Loading data...")
    df = load_parking_data()
    df = engineer_features(df)
    print(f"   ✓ Loaded {len(df)} records")
    
    # Prepare data
    print("\n2. Preparing features...")
    X, y, scaler, encoder, feature_cols = prepare_random_forest_data(df)
    print(f"   ✓ Features shape: {X.shape}")
    print(f"   ✓ Targets shape: {y.shape}")
    print(f"   ✓ Classes: {encoder.classes_}")
    
    # Split data
    print("\n3. Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"   ✓ Train: {len(X_train)}, Test: {len(X_test)}")
    
    # Build model
    print("\n4. Building Random Forest...")
    model = build_parking_rf(n_estimators=200, max_depth=20)
    print(f"   ✓ Model created")
    
    # Train model
    print("\n5. Training...")
    model.fit(X_train, y_train)
    print("   ✓ Training complete")
    
    # Evaluate
    print("\n6. Evaluating...")
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    print(f"   ✓ Train Accuracy: {train_score*100:.2f}%")
    print(f"   ✓ Test Accuracy: {test_score*100:.2f}%")
    
    # Predictions
    y_pred = model.predict(X_test)
    
    # Classification report
    from sklearn.metrics import classification_report
    print("\n   Classification Report:")
    print(classification_report(y_test, y_pred, target_names=encoder.classes_))
    
    # Feature importance
    get_feature_importance(model, feature_cols)
    
    # Save model and preprocessing objects
    print("\n7. Saving model and preprocessors...")
    save_rf_model(model, "../../models/parking_rf_model.pkl")
    save_preprocessing_objects(scaler, encoder)
    
    # Save feature columns
    joblib.dump(feature_cols, "../../models/parking_feature_cols.pkl")
    print("   ✓ All objects saved")
    
    return model, scaler, encoder


def main():
    """Train both models"""
    print("=" * 60)
    print("PARKING PREDICTION MODEL TRAINING")
    print("=" * 60)
    
    # Train LSTM
    lstm_model, lstm_history = train_lstm_model()
    
    # Train Random Forest
    rf_model, scaler, encoder = train_random_forest()
    
    print("\n" + "=" * 60)
    print("✓ TRAINING COMPLETE!")
    print("=" * 60)
    print("\nModels saved:")
    print("  - models/parking_lstm_model.h5")
    print("  - models/parking_rf_model.pkl")
    print("  - models/parking_rf_scaler.pkl")
    print("  - models/parking_encoder.pkl")
    print("  - models/parking_feature_cols.pkl")
    print("\nReady for predictions!")


if __name__ == "__main__":
    main()
