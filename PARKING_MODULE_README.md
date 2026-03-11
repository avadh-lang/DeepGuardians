# 🅿️ Parking Intelligence Module

## Overview

AI-powered parking availability prediction system that helps users find optimal parking spots at their destination. Uses hybrid ML approach combining **Random Forest** for availability classification and **LSTM** for occupancy forecasting.

## Features

✅ **Predict parking availability** at destination  
✅ **Show nearby parking options** within custom radius  
✅ **Optimal parking time recommendations**  
✅ **Traffic-integrated route planning**  
✅ **Real-time availability classification**  
✅ **26 parking locations across Mumbai**  

---

## Architecture

```
Input: Destination + Arrival Time
           ↓
Find Nearby Parking (radius search)
           ↓
Random Forest Classifier
   (abundant/available/limited/critical)
           ↓
LSTM Occupancy Predictor
   (future occupancy %)
           ↓
Optimal Time Recommendations
           ↓
Best Parking Spot + Alternative Options
```

---

## Dataset

### Synthetic Parking Dataset
- **343,200 records** (26 locations × 24 hours × 549 days)
- **Time Range**: July 2023 - December 2024
- **26 Parking Locations**: Commercial, Shopping, Transit, Tourist, Residential, Hospital, Educational, Airport

### Mumbai Parking Locations

| ID | Name | Type | Capacity | Rate/Hr |
|----|------|------|----------|---------|
| P001 | BKC Corporate Park | Commercial | 500 | ₹50 |
| P005 | Phoenix Palladium Mall | Shopping | 800 | ₹30 |
| P009 | Chhatrapati Shivaji Terminus | Transit | 450 | ₹20 |
| P013 | Gateway of India Plaza | Tourist | 200 | ₹70 |
| P017 | Powai Lake Residential | Residential | 250 | ₹30 |
| P021 | Lilavati Hospital | Hospital | 300 | ₹25 |
| P023 | IIT Bombay Campus | Educational | 500 | ₹10 |
| P025 | Airport T1 Parking | Airport | 1200 | ₹100 |

*... and 18 more locations*

---

## Quick Start

### 1. Generate Dataset (First Time)
```bash
cd backend
python generate_parking_dataset.py
```

### 2. Train Models
```bash
cd backend/src/parking
python quick_setup.py
```

**Output:**
```
✓ Random Forest model: 83.71% accuracy
✓ Models saved to backend/models/
```

### 3. Start API Server
```bash
cd backend
uvicorn api:app --reload
```

**API Docs:** `http://127.0.0.1:8000/docs`

---

## API Endpoints

### 1. Predict Parking Availability

**POST** `/parking/predict`

Predict availability for a specific parking lot.

```json
{
  "parking_id": "P013",
  "arrival_datetime": "2024-03-15T14:30:00",
  "weather": "Clear"
}
```

**Response:**
```json
{
  "status": "success",
  "parking_name": "Gateway of India Plaza",
  "availability": "available",
  "confidence": 0.74,
  "probabilities": {
    "abundant": 0.15,
    "available": 0.74,
    "limited": 0.09,
    "critical": 0.02
  },
  "location": {
    "latitude": 18.9220,
    "longitude": 72.8347,
    "capacity": 200,
    "hourly_rate": 70
  }
}
```

---

### 2. Find Nearby Parking

**POST** `/parking/nearby`

Find parking options near your destination.

```json
{
  "destination_lat": 18.9220,
  "destination_lon": 72.8347,
  "arrival_datetime": "2024-03-15T14:30:00",
  "radius_km": 2.0
}
```

**Response:**
```json
{
  "status": "success",
  "parking_options": [
    {
      "parking_id": "P013",
      "name": "Gateway of India Plaza",
      "distance_km": 0.0,
      "availability": "available",
      "confidence": 0.74,
      "capacity": 200,
      "hourly_rate": 70
    },
    {
      "parking_id": "P024",
      "name": "Mumbai University Fort",
      "distance_km": 0.95,
      "availability": "available",
      "confidence": 0.73
    }
  ],
  "total_found": 4
}
```

---

### 3. Optimal Parking Times

**POST** `/parking/optimal-time`

Get best arrival times for a parking location.

```json
{
  "parking_id": "P013",
  "date": "2024-03-15",
  "time_range_hours": 24
}
```

**Response:**
```json
{
  "status": "success",
  "parking_name": "Gateway of India Plaza",
  "optimal_times": [
    {
      "time": "02:00",
      "availability": "abundant",
      "confidence": 0.89
    },
    {
      "time": "21:00",
      "availability": "abundant",
      "confidence": 0.85
    }
  ],
  "best_time": {
    "time": "02:00",
    "availability": "abundant"
  }
}
```

---

### 4. Route with Parking (Traffic Integration)

**POST** `/parking/route-with-parking`

Complete route planning with parking recommendation.

```json
{
  "origin_lat": 19.0760,
  "origin_lon": 72.8777,
  "destination_lat": 18.9220,
  "destination_lon": 72.8347,
  "arrival_time": "2024-03-15T14:30:00"
}
```

**Response:**
```json
{
  "status": "success",
  "route": {
    "origin": {"latitude": 19.0760, "longitude": 72.8777},
    "destination": {"latitude": 18.9220, "longitude": 72.8347},
    "estimated_arrival": "2024-03-15T14:30:00"
  },
  "parking_recommendation": {
    "name": "Gateway of India Plaza",
    "distance_km": 0.0,
    "availability": "available",
    "hourly_rate": 70
  },
  "alternative_parking": [...],
  "optimal_arrival_times": [...]
}
```

---

### 5. Get All Parking Locations

**GET** `/parking/locations`

List all available parking locations.

---

### 6. Health Check

**GET** `/parking/health`

Check if parking module is operational.

---

## Models

### Random Forest Classifier
- **Purpose**: Classify availability (abundant/available/limited/critical)
- **Accuracy**: 83.71%
- **Features**: 13 (time, location, weather, engineered features)
- **Trees**: 100
- **Max Depth**: 15

### LSTM (Optional)
- **Purpose**: Predict future occupancy percentage
- **Architecture**: 3 LSTM layers (128→64→32) + Dense layers
- **Input**: 24-hour sequence window
- **Output**: Next hour occupancy rate (0-100%)

---

## Availability Categories

| Category | Occupancy Range | Color | Description |
|----------|----------------|-------|-------------|
| **Abundant** | 0-30% | 🟢 Green | Plenty of spots |
| **Available** | 30-60% | 🟡 Yellow | Moderate availability |
| **Limited** | 60-85% | 🟠 Orange | Few spots left |
| **Critical** | 85-100% | 🔴 Red | Nearly full |

---

## Integration with Traffic Module

The parking module integrates seamlessly with the traffic congestion prediction system:

1. **Route Planning**: When user plans route A→B, system:
   - Predicts traffic on route
   - Finds parking near destination B
   - Recommends departure time considering both traffic and parking

2. **Combined Prediction**:
   ```
   User Input: Origin + Destination + Desired Arrival Time
        ↓
   Traffic Module: Predicts congestion on route
        ↓
   Parking Module: Predicts parking availability at destination
        ↓
   Combined Output: Best departure time + Best parking spot
   ```

---

## File Structure

```
backend/
├── dataset/
│   └── parking_dataset.csv          # 343K records
├── models/
│   ├── parking_rf_model.pkl         # Random Forest (43MB)
│   ├── parking_rf_scaler.pkl        # Feature scaler
│   ├── parking_encoder.pkl          # Label encoder
│   └── parking_feature_cols.pkl     # Feature names
├── src/
│   └── parking/
│       ├── __init__.py
│       ├── parking_preprocess.py    # Data preprocessing
│       ├── parking_rf_model.py      # Random Forest model
│       ├── parking_lstm_model.py    # LSTM model (optional)
│       ├── parking_predict.py       # Prediction logic
│       ├── parking_train.py         # Full training script
│       └── quick_setup.py           # Quick setup (recommended)
├── parking_api.py                   # API routes
└── generate_parking_dataset.py      # Dataset generator
```

---

## Usage Examples

### Python SDK

```python
from src.parking.parking_predict import ParkingPredictor
from datetime import datetime

# Initialize predictor
predictor = ParkingPredictor()

# Find parking near destination
result = predictor.predict_for_destination(
    destination_lat=18.9220,
    destination_lon=72.8347,
    arrival_datetime=datetime(2024, 3, 15, 14, 30),
    radius_km=2.0
)

print(f"Recommended: {result['recommended_parking']['name']}")
print(f"Availability: {result['recommended_parking']['availability']}")
```

### cURL

```bash
# Find nearby parking
curl -X POST "http://127.0.0.1:8000/parking/nearby" \
  -H "Content-Type: application/json" \
  -d '{
    "destination_lat": 18.9220,
    "destination_lon": 72.8347,
    "radius_km": 2.0
  }'
```

---

## Performance

- **Prediction Latency**: <100ms per request
- **Model Size**: 43MB (Random Forest)
- **Dataset Size**: 130MB (343K records)
- **Locations Covered**: 26 across Mumbai
- **Accuracy**: 83.71% (test set)

---

## Future Enhancements

🔮 Real-time parking sensor integration  
🔮 Dynamic pricing based on demand  
🔮 Reservation system  
🔮 Multi-city expansion  
🔮 Historical parking patterns per user  
🔮 EV charging station availability  

---

## Testing

Test the API interactively:
```bash
# Start server
uvicorn api:app --reload

# Open browser
http://127.0.0.1:8000/docs
```

Try example requests in Swagger UI!

---

## Credits

**Hackathon**: AI-Driven Predictive Urban Navigation  
**Team**: DeepGuardians  
**Module**: Parking Intelligence  
**Tech Stack**: Python, FastAPI, Scikit-learn, TensorFlow, Pandas

---

## License

MIT License - Feel free to use and modify!
