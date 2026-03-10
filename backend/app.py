from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from tensorflow.keras.models import load_model

from src.preprocess import load_and_preprocess
from src.sequence import create_sequences

app = Flask(__name__)
CORS(app)   # <-- ADD THIS

model = load_model("models/lstm_model.h5", compile=False)

X, y, scaler, encoder = load_and_preprocess("dataset/traffic_dataset.csv")
X_seq, y_seq = create_sequences(X, y)


@app.route("/predict", methods=["POST"])
def predict():

    try:
        data = request.get_json()

        print("Received data:", data)

        features = np.array([
            data["vehicle_count"],
            data["average_speed"],
            data["lane_occupancy"],
            data["flow_rate"],
            data["waiting_time"],
            data["density_veh_per_km"],
            data["queue_length_veh"],
            data["avg_accel_ms2"]
        ])

        features = features.reshape(1, -1)

        features_scaled = scaler.transform(features)

        sequence = np.repeat(features_scaled, 10, axis=0)
        sequence = sequence.reshape(1, 10, features_scaled.shape[1])

        prediction = model.predict(sequence)

        predicted_class = round(prediction[0][0])

        label = encoder.inverse_transform([predicted_class])[0]

        return jsonify({
            "congestion_level": label
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)