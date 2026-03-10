"""
FastAPI Server for Real-Time Traffic Congestion Prediction

Run with:
    uvicorn backend.api:app --reload

API Documentation:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.live_congestion_predictor import predict_congestion_live, reset_buffer

# Initialize FastAPI app
app = FastAPI(
    title="Traffic Congestion Prediction API",
    description="Real-time LSTM-based traffic congestion predictor",
    version="1.0.0"
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request model
class TrafficInput(BaseModel):
    """Traffic feature input for congestion prediction."""
    vehicle_count: float
    avg_speed: float
    lane_occupancy: float
    queue_length: float
    time_of_day: float
    day_of_week: float


@app.get("/")
def home():
    """Home endpoint with API information."""
    return {
        "message": "Traffic Congestion Prediction API Running",
        "version": "1.0.0",
        "docs": "http://127.0.0.1:8000/docs",
        "predict_endpoint": "POST /predict",
        "reset_endpoint": "POST /reset"
    }


@app.post("/predict")
def predict(data: TrafficInput):
    """
    Predict traffic congestion level from live traffic features.
    
    Required 10 consecutive calls to build sequence window before predictions begin.
    
    Args:
        vehicle_count: Number of vehicles on road
        avg_speed: Average vehicle speed (km/h)
        lane_occupancy: Occupancy percentage (0-1)
        queue_length: Number of vehicles in queue
        time_of_day: Hour of day (0-23)
        day_of_week: Day of week (0-6, 0=Monday)
    
    Returns:
        - While collecting: {"status": "collecting_data", "samples_collected": N, "required_points": M}
        - With prediction: {"status": "success", "congestion_level": "High", "confidence": 2.1}
    
    Example request:
        {
            "vehicle_count": 40,
            "avg_speed": 25,
            "lane_occupancy": 0.65,
            "queue_length": 10,
            "time_of_day": 18,
            "day_of_week": 3
        }
    """
    try:
        # Extract features as list
        features = [
            data.vehicle_count,
            data.avg_speed,
            data.lane_occupancy,
            data.queue_length,
            data.time_of_day,
            data.day_of_week
        ]

        # Get prediction
        result = predict_congestion_live(features)

        return result

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.post("/reset")
def reset():
    """Reset the prediction buffer for a new session."""
    result = reset_buffer()
    return result


@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "traffic-congestion-predictor"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
