"""
Parking data preprocessing
Handles feature engineering and data preparation for ML models
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib


def load_parking_data(path="../../dataset/parking_dataset.csv"):
    """Load parking dataset"""
    df = pd.read_csv(path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def engineer_features(df):
    """
    Create additional features for better prediction
    """
    df = df.copy()
    
    # Time-based features
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    
    # Parking stress level (how full is it)
    df['stress_level'] = df['occupancy_rate'] / 100.0
    
    # Time categories
    df['time_category'] = pd.cut(df['hour'], 
                                  bins=[0, 6, 12, 18, 24],
                                  labels=['night', 'morning', 'afternoon', 'evening'],
                                  include_lowest=True)
    
    # Availability category for classification
    df['availability_category'] = pd.cut(df['occupancy_rate'],
                                          bins=[0, 30, 60, 85, 100],
                                          labels=['abundant', 'available', 'limited', 'critical'])
    
    return df


def prepare_lstm_sequences(df, sequence_length=24, target_col='occupancy_rate'):
    """
    Prepare sequences for LSTM model
    Predicts next hour's occupancy based on past 24 hours
    """
    # Group by parking location
    sequences = []
    targets = []
    parking_ids = []
    
    for parking_id in df['parking_id'].unique():
        location_data = df[df['parking_id'] == parking_id].sort_values('timestamp')
        
        # Select features for sequence
        features = ['occupancy_rate', 'hour', 'day_of_week', 'is_weekend', 
                   'is_peak_hour', 'hour_sin', 'hour_cos']
        
        # Ensure all data is numeric
        data = location_data[features].astype('float32').values
        target = location_data[target_col].astype('float32').values
        
        # Create sequences
        for i in range(len(data) - sequence_length):
            seq = data[i:i + sequence_length]
            tgt = target[i + sequence_length]
            
            sequences.append(seq)
            targets.append(tgt)
            parking_ids.append(parking_id)
    
    return np.array(sequences, dtype='float32'), np.array(targets, dtype='float32'), parking_ids


def prepare_random_forest_data(df):
    """
    Prepare data for Random Forest classification
    Predicts availability category
    """
    # Select features
    feature_cols = ['hour', 'day_of_week', 'is_weekend', 'is_peak_hour',
                   'capacity', 'hourly_rate', 'hour_sin', 'hour_cos', 
                   'day_sin', 'day_cos', 'month']
    
    # Encode categorical features
    le_location = LabelEncoder()
    le_weather = LabelEncoder()
    le_availability = LabelEncoder()
    
    df = df.copy()
    df['location_encoded'] = le_location.fit_transform(df['location_type'])
    df['weather_encoded'] = le_weather.fit_transform(df['weather'])
    df['availability_encoded'] = le_availability.fit_transform(df['availability_category'])
    
    feature_cols.extend(['location_encoded', 'weather_encoded'])
    
    X = df[feature_cols].values
    y = df['availability_encoded'].values
    
    # Scale features
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    
    return X_scaled, y, scaler, le_availability, feature_cols


def save_preprocessing_objects(scaler, encoder, lstm_scaler=None, path_prefix="../../models/parking"):
    """Save preprocessing objects"""
    joblib.dump(scaler, f"{path_prefix}_rf_scaler.pkl")
    joblib.dump(encoder, f"{path_prefix}_encoder.pkl")
    if lstm_scaler:
        joblib.dump(lstm_scaler, f"{path_prefix}_lstm_scaler.pkl")
    print("✓ Preprocessing objects saved")


def load_preprocessing_objects(path_prefix="../../models/parking"):
    """Load preprocessing objects"""
    scaler = joblib.load(f"{path_prefix}_rf_scaler.pkl")
    encoder = joblib.load(f"{path_prefix}_encoder.pkl")
    return scaler, encoder


def preprocess_for_prediction(data, parking_id, scaler, feature_cols):
    """
    Preprocess single data point for prediction
    
    Args:
        data: dict with keys like hour, day_of_week, etc.
        parking_id: parking location ID
        scaler: fitted MinMaxScaler
        feature_cols: list of feature column names
    """
    # Create feature vector
    features = {}
    
    # Direct features
    for col in ['hour', 'day_of_week', 'is_weekend', 'is_peak_hour', 
                'capacity', 'hourly_rate', 'month']:
        features[col] = data.get(col, 0)
    
    # Engineered features
    features['hour_sin'] = np.sin(2 * np.pi * features['hour'] / 24)
    features['hour_cos'] = np.cos(2 * np.pi * features['hour'] / 24)
    features['day_sin'] = np.sin(2 * np.pi * features['day_of_week'] / 7)
    features['day_cos'] = np.cos(2 * np.pi * features['day_of_week'] / 7)
    
    # Encode categorical (you'll need to load encoders)
    features['location_encoded'] = data.get('location_encoded', 0)
    features['weather_encoded'] = data.get('weather_encoded', 0)
    
    # Create array in correct order
    X = np.array([[features[col] for col in feature_cols]])
    
    # Scale
    X_scaled = scaler.transform(X)
    
    return X_scaled


if __name__ == "__main__":
    print("Loading and preprocessing parking data...")
    
    # Load data
    df = load_parking_data()
    print(f"✓ Loaded {len(df)} records")
    
    # Engineer features
    df = engineer_features(df)
    print(f"✓ Engineered features. Total columns: {len(df.columns)}")
    
    # Prepare for LSTM
    X_lstm, y_lstm, parking_ids = prepare_lstm_sequences(df, sequence_length=24)
    print(f"✓ LSTM sequences: {X_lstm.shape}, Targets: {y_lstm.shape}")
    
    # Prepare for Random Forest
    X_rf, y_rf, scaler, encoder, feature_cols = prepare_random_forest_data(df)
    print(f"✓ Random Forest data: {X_rf.shape}, Targets: {y_rf.shape}")
    
    # Save objects
    save_preprocessing_objects(scaler, encoder)
    
    print("\n" + "="*60)
    print("Preprocessing complete!")
    print("="*60)
