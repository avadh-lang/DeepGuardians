"""
FastAPI backend for real-time traffic congestion prediction
Run: uvicorn backend.app:app --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.live_predict import predict_live, reset_buffer

# Initialize FastAPI app
app = FastAPI(title="Traffic Congestion Predictor")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic model for request validation
class TrafficData(BaseModel):
    vehicle_count: float
    average_speed: float
    lane_occupancy: float
    flow_rate: float
    waiting_time: float
    density_veh_per_km: float
    queue_length_veh: float
    avg_accel_ms2: float


@app.post("/predict")
def predict(data: TrafficData):
    """
    Predict traffic congestion level from live traffic data.
    
    Requires consecutive calls to build up a sequence window (default: 10 samples).
    """
    try:
        print(f"Received data: {data}")
        
        # Extract features in order
        features = [
            data.vehicle_count,
            data.average_speed,
            data.lane_occupancy,
            data.flow_rate,
            data.waiting_time,
            data.density_veh_per_km,
            data.queue_length_veh,
            data.avg_accel_ms2
        ]
        
        # Get prediction
        result = predict_live(features)
        
        print(f"Prediction result: {result}")
        
        return result
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {"error": str(e), "status": "error"}


@app.post("/reset")
def reset():
    """Reset the prediction buffer for a new session."""
    reset_buffer()
    return {"status": "buffer_reset"}


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)