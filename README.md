# 🚦 DeepGuardians - Real-Time Traffic Congestion Predictor

A complete ML pipeline for predicting traffic congestion using LSTM neural networks with live data streaming.

## 📊 Architecture

```
Traffic Camera/Sensor
        ↓
Vehicle Detection (YOLO)
        ↓
Feature Extraction
        ↓
FastAPI Prediction API
        ↓
React Dashboard
```

## 🚀 Quick Start

### 1️⃣ Install Dependencies

```bash
cd backend
pip install -r ../requirements.txt
```

### 2️⃣ Setup Models (One-time)

```bash
cd backend
python setup_models.py
```

This will:
- Load the traffic dataset
- Extract and save the scaler (`models/scaler.pkl`)
- Extract and save the encoder (`models/encoder.pkl`)

### 3️⃣ Start FastAPI Backend

```bash
cd backend
uvicorn app:app --reload --port 8000
```

Server runs at: `http://127.0.0.1:8000`

### 4️⃣ Start React Dashboard

In a new terminal:

```bash
cd traffic-dashboard
npm start
```

Dashboard runs at: `http://localhost:3000`

## 📡 API Endpoints

### POST `/predict`
Send live traffic data and get congestion prediction.

**Request:**
```json
{
  "vehicle_count": 45.5,
  "average_speed": 32.1,
  "lane_occupancy": 0.65,
  "flow_rate": 85.2,
  "waiting_time": 18.5,
  "density_veh_per_km": 28.3,
  "queue_length_veh": 12,
  "avg_accel_ms2": 1.5
}
```

**Response (Collecting):**
```json
{
  "status": "collecting_data",
  "samples_collected": 5,
  "samples_needed": 10
}
```

**Response (Prediction):**
```json
{
  "status": "success",
  "congestion_level": "Moderate",
  "confidence": 0.72
}
```

### POST `/reset`
Reset the prediction buffer for a new session.

### GET `/health`
Health check endpoint.

## 🔄 How It Works

### Sequence Buffering
The LSTM model requires a sequence of 10 consecutive time steps to make predictions. The backend maintains a sliding window buffer:

```
Time 1 → Add to buffer
Time 2 → Add to buffer
...
Time 10 → Buffer full → First prediction available
Time 11 → Remove oldest, add newest → Prediction updated
```

### Model Pipeline

1. **Input Data**: 8 traffic features
2. **Scaling**: MinMax normalization using saved scaler
3. **Sequence**: Stack last 10 samples → Shape (1, 10, 8)
4. **LSTM Model**: 2 LSTM layers with dropout
5. **Output**: Congestion class
6. **Label**: Convert class to human-readable label (e.g., "High", "Moderate", "Low")

## 📁 Project Structure

```
horizon/
├── backend/
│   ├── app.py                 # FastAPI server
│   ├── setup_models.py        # Initialize scaler & encoder
│   ├── models/
│   │   ├── lstm_model.h5      # Trained LSTM model
│   │   ├── scaler.pkl         # MinMax scaler
│   │   └── encoder.pkl        # Label encoder
│   ├── dataset/
│   │   └── traffic_dataset.csv
│   └── src/
│       ├── live_predict.py    # Real-time prediction logic
│       ├── preprocess.py      # Data preprocessing
│       └── sequence.py        # Sequence creation
│
├── traffic-dashboard/         # React UI
│   ├── public/
│   ├── src/
│   │   ├── App.js
│   │   └── TrafficPredictor.js
│   └── package.json
│
└── requirements.txt
```

## 🎯 Features

✅ **Real-time Prediction**: Live traffic congestion forecasting  
✅ **Sequence Buffering**: Maintains 10-step window for LSTM  
✅ **CORS Enabled**: Works with any frontend  
✅ **Error Handling**: Graceful degradation  
✅ **Health Checks**: Monitor server status  
✅ **React Dashboard**: Visual interface for predictions  

## 🔧 Troubleshooting

### Model not found
```bash
cd backend
python setup_models.py
```

### Port already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### CORS errors
The FastAPI server has CORS enabled for all origins. If issues persist, verify the proxy in `traffic-dashboard/package.json`:
```json
"proxy": "http://localhost:8000"
```

## 📈 Performance

- **Inference Time**: ~100-200ms per prediction
- **Window Size**: 10 samples
- **Model Size**: ~500KB (LSTM with 64→32 units)
- **Throughput**: Up to 10 predictions/sec

## 🚀 Next Steps (Advanced)

1. **WebSocket Integration**: Real-time streaming updates
2. **Batch Predictions**: Process multiple locations simultaneously
3. **Model Retraining**: Automatic updates with new data
4. **GPU Acceleration**: Use CUDA for faster inference
5. **Kubernetes Deployment**: Scale to production

## 📝 Dataset Features

The model trains on 10,000 traffic observations with 16 features:

- `vehicle_count`: Number of vehicles
- `average_speed`: Average vehicle speed (km/h)
- `lane_occupancy`: % of lane occupied
- `flow_rate`: Vehicles per minute
- `waiting_time`: Average wait time (seconds)
- `density_veh_per_km`: Vehicle density
- `queue_length_veh`: Length of vehicle queue
- `avg_accel_ms2`: Average acceleration
- `SRI`: Speed Reduction Index
- `Degree_of_congestion`: Target (Low/Moderate/High)

## 📚 References

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [TensorFlow LSTM](https://www.tensorflow.org/api_docs/python/tf/keras/layers/LSTM)
- [React Docs](https://react.dev/)

---

**Built for**: Hackathon  
**Last Updated**: March 2026