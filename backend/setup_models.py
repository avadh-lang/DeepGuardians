"""
Setup script to initialize and save preprocessing objects (scaler, encoder)
Run this once before starting the live prediction server
"""
import joblib
from src.preprocess import load_and_preprocess

print("Loading dataset and preprocessing...")
X, y, scaler, encoder = load_and_preprocess("dataset/traffic_dataset.csv")

print("Saving scaler and encoder...")
joblib.dump(scaler, "models/scaler.pkl")
joblib.dump(encoder, "models/encoder.pkl")

print("✓ Setup complete!")
print("Run: uvicorn backend.app:app --reload")
