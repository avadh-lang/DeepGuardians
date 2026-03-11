"""
LSTM Model for Parking Occupancy Prediction
Predicts future parking occupancy based on historical patterns
"""
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau


def build_parking_lstm(sequence_length=24, n_features=7):
    """
    Build LSTM model for parking occupancy prediction
    
    Args:
        sequence_length: number of time steps to look back
        n_features: number of features per time step
    
    Returns:
        Compiled Keras model
    """
    model = Sequential([
        # First LSTM layer
        LSTM(128, return_sequences=True, input_shape=(sequence_length, n_features)),
        Dropout(0.3),
        BatchNormalization(),
        
        # Second LSTM layer
        LSTM(64, return_sequences=True),
        Dropout(0.3),
        BatchNormalization(),
        
        # Third LSTM layer
        LSTM(32, return_sequences=False),
        Dropout(0.2),
        
        # Dense layers
        Dense(16, activation='relu'),
        Dropout(0.2),
        
        # Output layer (predicts occupancy rate 0-100)
        Dense(1, activation='linear')
    ])
    
    model.compile(
        optimizer='adam',
        loss='huber',  # Robust to outliers
        metrics=['mae', 'mse']
    )
    
    return model


def get_callbacks():
    """Get training callbacks"""
    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True,
        verbose=1
    )
    
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-7,
        verbose=1
    )
    
    return [early_stop, reduce_lr]


if __name__ == "__main__":
    # Test model architecture
    model = build_parking_lstm(sequence_length=24, n_features=7)
    model.summary()
    
    print("\n✓ LSTM model architecture created successfully")
