import numpy as np
from tensorflow.keras.models import load_model
import joblib

# Load model and preprocessing objects
model = load_model("models/lstm_model.h5", compile=False)
scaler = joblib.load("models/scaler.pkl")
encoder = joblib.load("models/encoder.pkl")

# Sequence buffer to maintain sliding window
sequence_buffer = []
WINDOW_SIZE = 10


def predict_live(data):
    """
    Predict congestion level from live traffic data.
    
    Args:
        data: List of feature values [vehicle_count, avg_speed, lane_occupancy, 
              queue_length, time_of_day, day_of_week, ...]
    
    Returns:
        dict: Result containing congestion_level or status
    """
    global sequence_buffer
    
    # Convert input to numpy array and reshape
    features = np.array(data).reshape(1, -1)
    
    # Scale features using the loaded scaler
    features_scaled = scaler.transform(features)
    
    # Add to buffer
    sequence_buffer.append(features_scaled[0])
    
    # Check if we have enough data
    if len(sequence_buffer) < WINDOW_SIZE:
        return {
            "status": "collecting_data",
            "samples_collected": len(sequence_buffer),
            "samples_needed": WINDOW_SIZE
        }
    
    # Keep only the last WINDOW_SIZE samples
    if len(sequence_buffer) > WINDOW_SIZE:
        sequence_buffer.pop(0)
    
    # Prepare sequence for LSTM
    X = np.array(sequence_buffer).reshape(1, WINDOW_SIZE, -1)
    
    # Make prediction
    prediction = model.predict(X, verbose=0)
    
    # Convert prediction to class
    pred_class = int(np.round(prediction[0][0]))
    
    # Convert class to label
    congestion_label = encoder.inverse_transform([pred_class])[0]
    
    return {
        "status": "success",
        "congestion_level": congestion_label,
        "confidence": float(prediction[0][0])
    }


def reset_buffer():
    """Reset the sequence buffer for new prediction session."""
    global sequence_buffer
    sequence_buffer = []
