from data_pipleline import pipeline

# correct dataset path
DATA_PATH = "../dataset/traffic_dataset.csv"

X_train, X_test, y_train, y_test = pipeline(DATA_PATH)

print("X_train shape:", X_train.shape)
print("X_test shape:", X_test.shape)
print("y_train shape:", y_train.shape)
print("y_test shape:", y_test.shape)