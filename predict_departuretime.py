import sys
import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import to_categorical

# Fix import path so Python can find data_pipeline.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import data_pipleline  # your pipeline module

# -----------------------------
# Load Trained Model
# -----------------------------
model = load_model("traffic_lstm_model.h5")
print("Model loaded successfully!")

# -----------------------------
# Prepare Dynamic Label Mapping
# -----------------------------
# Get training labels to dynamically map class indices to actual departure times
_, _, y_train, _ = data_pipleline.pipeline("../dataset/traffic_dataset.csv")
unique_labels = np.unique(y_train)

# Map model class indices to original departure times
label_to_time = {i: unique_labels[i] for i in range(len(unique_labels))}

# -----------------------------
# Predict Departure Time Function
# -----------------------------
def predict_departure_time(sample):
    """
    Predicts departure time for a single sample.
    sample: numpy array of shape (timesteps, features)
    Returns the human-readable departure time.
    """
    if sample.ndim == 2:
        sample = sample.reshape(1, sample.shape[0], sample.shape[1])  # batch dim
    y_pred_prob = model.predict(sample)
    y_pred_class = np.argmax(y_pred_prob, axis=1)[0]
    predicted_time = label_to_time[y_pred_class]
    return predicted_time

# -----------------------------
# Fetch Input from UI / API
# -----------------------------
# Example: replace this function to fetch real-time traffic features from your UI
# Must return a numpy array of shape (timesteps, features)
def fetch_ui_input():
    # Example placeholder: 10 timesteps, 13 features
    timesteps = 10
    features = 13
    return np.random.rand(timesteps, features)  # replace with actual UI input

# -----------------------------
# Predict in Real-Time
# -----------------------------
new_input = fetch_ui_input()
predicted_time = predict_departure_time(new_input)
print(f"Predicted departure time from UI input: {predicted_time}")