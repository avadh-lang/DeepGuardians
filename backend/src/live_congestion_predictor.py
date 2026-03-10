import numpy as np
import joblib
from tensorflow.keras.models import load_model

# Load trained components
model = load_model("models/lstm_model.h5", compile=False)

scaler = joblib.load("models/scaler.pkl")
encoder = joblib.load("models/encoder.pkl")

# LSTM needs sequence input
WINDOW_SIZE = 10

# Buffer to store recent traffic states
sequence_buffer = []


def predict_congestion_live(features):
    """
    Predict congestion using live traffic features
    
    Args:
        features: List of 6 traffic features
                 [vehicle_count, avg_speed, lane_occupancy, queue_length, time_of_day, day_of_week]
    
    Returns:
        dict: Prediction result with congestion_level or status message
    
    Example:
        >>> predict_congestion_live([40, 25, 0.65, 10, 18, 3])
        {'congestion_level': 'High', 'confidence': 2.1}
    """

    global sequence_buffer

    features = np.array(features).reshape(1, -1)

    # Scale features
    scaled_features = scaler.transform(features)

    # Add to sequence
    sequence_buffer.append(scaled_features[0])

    # Wait until sequence window fills
    if len(sequence_buffer) < WINDOW_SIZE:
        return {
            "status": "collecting_data",
            "samples_collected": len(sequence_buffer),
            "required_points": WINDOW_SIZE - len(sequence_buffer)
        }

    # Maintain window size
    if len(sequence_buffer) > WINDOW_SIZE:
        sequence_buffer.pop(0)

    # Create LSTM input: (1, WINDOW_SIZE, num_features)
    X = np.array(sequence_buffer).reshape(1, WINDOW_SIZE, -1)

    # Get prediction
    prediction = model.predict(X, verbose=0)

    # Convert to class
    predicted_class = int(np.round(prediction[0][0]))

    # Convert class to label
    congestion_label = encoder.inverse_transform([predicted_class])[0]

    # Include confidence score
    confidence = float(prediction[0][0])

    return {
        "status": "success",
        "congestion_level": congestion_label,
        "confidence": confidence
    }


def reset_buffer():
    """Reset the sequence buffer for a new prediction session."""
    global sequence_buffer
    sequence_buffer = []
    return {"status": "buffer_reset"}
