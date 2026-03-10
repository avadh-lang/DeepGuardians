import pandas as pd
from sklearn.preprocessing import MinMaxScaler, LabelEncoder


def load_and_preprocess(path):

    df = pd.read_csv(path)

    # Drop unnecessary column if present
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # Separate target
    target = "Degree_of_congestion"

    # Encode categorical columns
    label_encoders = {}

    for column in df.columns:
        if df[column].dtype == "object":
            le = LabelEncoder()
            df[column] = le.fit_transform(df[column])
            label_encoders[column] = le

    # Split features and target
    X = df.drop(columns=[target])
    y = df[target]

    # Scale features
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, y, scaler, label_encoders[target]