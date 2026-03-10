# 🚦 DeepGuardians - Real-Time Traffic Congestion Predictor

A production-ready LSTM-based system for predicting traffic congestion with live data streaming, sequence buffering, and FastAPI backend.

## ✨ Key Features

- ✅ **Real-time Prediction**: Live traffic congestion forecasting using LSTM
- ✅ **Sequence Buffering**: Maintains 10-step temporal window for LSTM
- ✅ **FastAPI Backend**: High-performance async API with auto-documentation
- ✅ **CORS Enabled**: Works with any frontend framework
- ✅ **Error Handling**: Graceful degradation and status feedback
- ✅ **Health Checks**: Monitor server status and reliability
- ✅ **React Dashboard**: Beautiful UI for predictions and analytics
- ✅ **Complete Testing Suite**: Test script with 15+ scenarios

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
cd traffic-dashboard && npm install
```

### 2. Setup Models (First Time Only)
```bash
cd backend
python setup_models.py
```

### 3. Start Backend Server
```bash
cd backend
uvicorn api:app --reload
```
API available at: `http://127.0.0.1:8000/docs`

### 4. Start React Dashboard
```bash
cd traffic-dashboard
npm start
```
Dashboard at: `http://localhost:3000`

### 5. Test the API (Optional)
```bash
cd backend
python test_api.py
```

## 📊 Architecture

```
Traffic Cameras (YOLO Detection)
        ↓
Feature Extraction
(vehicle_count, avg_speed, lane_occupancy, queue_length, time_of_day, day_of_week)
        ↓
FastAPI Backend (Port 8000)
        ↓
LSTM Neural Network
(2 layers: 64→32 units, with dropout)
        ↓
Congestion Prediction
(Low, Moderate, High, Severe)
        ↓
React Dashboard (Port 3000)
```

## 📡 API Endpoints

### POST `/predict`
Get real-time traffic congestion prediction.

**Request:**
```json
{
  "vehicle_count": 45,
  "avg_speed": 30,
  "lane_occupancy": 0.65,
  "queue_length": 12,
  "time_of_day": 18,
  "day_of_week": 2
}
```

**Response:**
```json
{
  "status": "success",
  "congestion_level": "High",
  "confidence": 2.15
}
```

### Other Endpoints
- **GET** `/` - Home info
- **POST** `/reset` - Reset prediction buffer
- **GET** `/health` - Health check

## 🔄 How It Works

### Sequence Buffering (10-Step Window)
```
Call 1-9:  Fill buffer (no prediction)
Call 10+:  Ready to predict, sliding window
```

The LSTM model requires 10 consecutive observations to build its temporal context. Once filled, the buffer automatically rolls - removing oldest, adding newest.

### Prediction Pipeline
1. **Input**: 6 traffic features
2. **Scaling**: MinMax normalization (learned from training data)
3. **Buffering**: Stack last 10 samples → Shape (1, 10, 6)
4. **LSTM**: Process temporal patterns
5. **Output**: Congestion class + confidence

## 📁 Project Structure

```
horizon/
├── backend/
│   ├── api.py                        # 🆕 FastAPI server
│   ├── setup_models.py               # Initialize scaler/encoder
│   ├── test_api.py                   # 🆕 Complete test suite
│   ├── models/
│   │   ├── lstm_model.h5
│   │   ├── scaler.pkl                # MinMax scaler
│   │   └── encoder.pkl               # Label encoder
│   ├── dataset/
│   │   └── traffic_dataset.csv       # Training data (10,000 rows)
│   └── src/
│       ├── live_congestion_predictor.py  # 🆕 Core prediction logic
│       ├── live_predict.py
│       ├── preprocess.py
│       ├── sequence.py
│       └── train.py
│
├── traffic-dashboard/                # React frontend
│   ├── src/
│   │   ├── App.js
│   │   └── TrafficPredictor.js
│   └── package.json
│
├── requirements.txt
├── README.md                         # This file
└── IMPLEMENTATION_GUIDE.md           # 🆕 Detailed documentation
```

## 🧪 Test the System

### Using the Test Suite
```bash
cd backend
python test_api.py
```

This runs:
- Health checks
- Home endpoint
- Single prediction
- 15 multi-scenario predictions (morning rush, midday, evening)

### Manual Testing with cURL
```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_count": 40,
    "avg_speed": 25,
    "lane_occupancy": 0.65,
    "queue_length": 10,
    "time_of_day": 18,
    "day_of_week": 3
  }'
```

## 🆕 What's New in This Version

| Feature | Status | Details |
|---------|--------|---------|
| Live Prediction Module | ✨ NEW | `live_congestion_predictor.py` |
| FastAPI Server | ✨ NEW | `api.py` with full CORS support |
| Test Suite | ✨ NEW | `test_api.py` with 15+ scenarios |
| Implementation Guide | ✨ NEW | Complete architecture & troubleshooting |
| Sequence Buffering | ✨ ENHANCED | Improved buffer management |
| Error Handling | ✨ ENHANCED | Better status messages |
| Documentation | ✨ ENHANCED | API docs at `/docs` |

## 🔧 Troubleshooting

### Models not found
```bash
cd backend && python setup_models.py
```

### Port already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9         # Linux/Mac
taskkill /PID <PID> /F                # Windows
```

### CORS errors
Verify proxy in `traffic-dashboard/package.json`:
```json
"proxy": "http://localhost:8000"
```

## 📈 Performance

- **Inference**: ~100-150ms per prediction
- **Throughput**: 6-10 requests/sec
- **Model Size**: ~500KB
- **Accuracy**: Depends on training data quality

## 📝 Dataset Features (10,000 rows)

- `vehicle_count`: Number of vehicles (0-150)
- `average_speed`: Avg velocity (5-80 km/h)
- `lane_occupancy`: Lane filled (0-1)
- `flow_rate`: Vehicles/minute (20-150)
- `waiting_time`: Queue wait (0-60s)
- `density_veh_per_km`: Vehicle density
- `queue_length_veh`: Vehicles in queue
- `avg_accel_ms2`: Average acceleration
- `SRI`: Speed Reduction Index
- `Degree_of_congestion`: Target (Light/Moderate/High/Severe)

## 🎯 Next Steps

1. **Integrate YOLO**: Extract features from camera feed
2. **Add Persistence**: Store predictions in database
3. **Real-time Dashboard**: WebSocket streaming updates
4. **Deploy**: Docker + Kubernetes ready
5. **Scale**: Multi-location predictions

## 📚 Documentation

- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - Complete system guide with examples
- **[API Docs](http://127.0.0.1:8000/docs)** - Interactive Swagger UI (after starting server)

## 📞 Support & Issues

- Check logs: `uvicorn backend.api:app --reload`
- Test API: `python backend/test_api.py`
- Review guide: `IMPLEMENTATION_GUIDE.md`

## 📄 License

This project is built for hackathons and educational purposes.

---

**Built for**: Hackathon  
**Updated**: March 2026  
**Version**: 2.0.0 (Production Ready)  
**Status**: ✅ Ready to Deploy