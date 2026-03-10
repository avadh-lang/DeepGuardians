import sys
import os
import numpy as np
# Fix import path so Python can find data_pipeline.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import data_pipleline

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.utils import to_categorical


# -----------------------------
# Load Dataset Using Pipeline
# -----------------------------

DATA_PATH = "../dataset/traffic_dataset.csv"

X_train, X_test, y_train, y_test = data_pipleline.pipeline(DATA_PATH)

print("\nData Loaded Successfully")
print("X_train:", X_train.shape)
print("X_test:", X_test.shape)


# -----------------------------
# Convert Labels to Categorical
# -----------------------------

num_classes = len(np.unique(y_train))

y_train = to_categorical(y_train, num_classes)
y_test = to_categorical(y_test, num_classes)


# -----------------------------
# Build LSTM Model
# -----------------------------

model = Sequential()

model.add(LSTM(
    64,
    return_sequences=True,
    input_shape=(X_train.shape[1], X_train.shape[2])
))

model.add(Dropout(0.2))

model.add(LSTM(32))

model.add(Dropout(0.2))

model.add(Dense(32, activation="relu"))

model.add(Dense(num_classes, activation="softmax"))


# -----------------------------
# Compile Model
# -----------------------------

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

print("\nModel Compiled Successfully")


# -----------------------------
# Train Model
# -----------------------------

history = model.fit(
    X_train,
    y_train,
    epochs=10,
    batch_size=32,
    validation_data=(X_test, y_test)
)


# -----------------------------
# Evaluate Model
# -----------------------------

loss, accuracy = model.evaluate(X_test, y_test)

print("\nTest Accuracy:", accuracy)


# -----------------------------
# Save Model
# -----------------------------

model.save("traffic_lstm_model.h5")

print("\nModel saved successfully as traffic_lstm_model.h5")