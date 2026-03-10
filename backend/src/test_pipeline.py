from data_pipleline import pipeline

X_train, X_test, y_train, y_test = pipeline("../dataset/traffic_dataset.csv")

print(X_train.shape)