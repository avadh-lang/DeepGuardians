from sklearn.model_selection import train_test_split
from tensorflow.keras.models import save_model

from src.preprocess import load_and_preprocess
from src.sequence import create_sequences
from src.model import build_model


def train_model():

    X, y, scaler, encoder = load_and_preprocess("dataset/traffic_dataset.csv")

    X_seq, y_seq = create_sequences(X, y)

    X_train, X_test, y_train, y_test = train_test_split(
        X_seq, y_seq, test_size=0.2, random_state=42
    )

    model = build_model((X_train.shape[1], X_train.shape[2]))

    model.fit(
        X_train,
        y_train,
        epochs=20,
        batch_size=32,
        validation_data=(X_test, y_test)
    )

    model.save("models/lstm_model.h5")

    print("Model Saved!")


if __name__ == "__main__":
    train_model()