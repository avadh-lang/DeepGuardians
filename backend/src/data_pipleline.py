import pandas as pd
import numpy as np
import warnings

from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split


# suppress sklearn NaN warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


def load_dataset(path):
    """
    Load dataset from CSV
    """
    df = pd.read_csv(path)

    # remove unnecessary index column
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    return df


def convert_time_of_day(df):
    """
    Convert time_of_day column to numeric values
    """

    if "time_of_day" in df.columns:

        time_map = {
            "Morning": 0,
            "Afternoon": 1,
            "Evening": 2,
            "Night": 3
        }

        df["time_of_day"] = df["time_of_day"].map(time_map)

    return df


def encode_target(df):
    """
    Encode Degree_of_congestion labels
    """

    if "Degree_of_congestion" in df.columns:
        le = LabelEncoder()
        df["Degree_of_congestion"] = le.fit_transform(df["Degree_of_congestion"])

    return df


def handle_missing_values(df):
    """
    Clean dataset and handle invalid values
    """

    # replace Excel errors
    df.replace(["#NAME?", "#VALUE!", "?", "NA", "N/A"], np.nan, inplace=True)

    # convert columns to numeric safely
    df = df.apply(pd.to_numeric, errors="coerce")

    # remove columns that become completely NaN
    df = df.dropna(axis=1, how="all")

    # fill missing numeric values with column mean
    df = df.fillna(df.mean())

    return df


def normalize_features(X):
    """
    Normalize features using MinMaxScaler
    """

    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled


def create_sequences(X, y, time_steps=10):
    """
    Convert dataset into LSTM sequences
    """

    X_seq = []
    y_seq = []

    for i in range(len(X) - time_steps):
        X_seq.append(X[i:i + time_steps])
        y_seq.append(y[i + time_steps])

    return np.array(X_seq), np.array(y_seq)


def pipeline(data_path):

    # 1 Load dataset
    df = load_dataset(data_path)

    # 2 Convert categorical feature
    df = convert_time_of_day(df)

    # 3 Encode target
    df = encode_target(df)

    # 4 Clean dataset
    df = handle_missing_values(df)

    print("Dataset shape after cleaning:", df.shape)

    # 5 Split features and target
    X = df.drop(columns=["Degree_of_congestion"])
    y = df["Degree_of_congestion"]

    # 6 Normalize features
    X_scaled = normalize_features(X)

    # 7 Create LSTM sequences
    X_seq, y_seq = create_sequences(X_scaled, y.values)

    print("LSTM sequence shape:", X_seq.shape)

    # 8 Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_seq,
        y_seq,
        test_size=0.2,
        random_state=42
    )

    return X_train, X_test, y_train, y_test


if __name__ == "__main__":

    DATA_PATH = "../dataset/traffic_dataset.csv"

    X_train, X_test, y_train, y_test = pipeline(DATA_PATH)

    print("\nPipeline executed successfully\n")

    print("X_train shape:", X_train.shape)
    print("X_test shape:", X_test.shape)

    print("y_train shape:", y_train.shape)
    print("y_test shape:", y_test.shape)