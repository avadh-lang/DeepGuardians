import numpy as np
from tensorflow.keras.models import load_model

from src.preprocess import load_and_preprocess
from src.sequence import create_sequences
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import pandas as pd


def predict():

    X, y, scaler, encoder = load_and_preprocess("dataset/traffic_dataset.csv")

    X_seq, y_seq = create_sequences(X, y)

    model = load_model("models/lstm_model.h5", compile=False)

    predictions = model.predict(X_seq)

    predicted_classes = np.round(predictions).astype(int)

    predicted_labels = encoder.inverse_transform(predicted_classes.flatten())

    print(predicted_labels[:10])
    
    mse = mean_squared_error(y_seq, predicted_classes)

    print("Model MSE:", mse)
    
    plt.plot(y_seq[:100], label="Actual")
    plt.plot(predicted_classes[:100], label="Predicted")

    plt.title("Traffic Congestion Prediction")
    plt.xlabel("Time")
    plt.ylabel("Congestion Level")
    plt.legend()

    plt.show()
    
    results = pd.DataFrame({
    "Actual": y_seq.flatten(),
    "Predicted": predicted_classes.flatten()
})

    results.to_csv("predictions.csv", index=False)

    print("Predictions saved to predictions.csv")


if __name__ == "__main__":
    predict()