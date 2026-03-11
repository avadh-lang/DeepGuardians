"""
FastAPI Server for Real-Time Traffic Congestion Prediction

Run with:
    uvicorn backend.api:app --reload

API Documentation:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.live_congestion_predictor import predict_congestion_live, reset_buffer
import os

# Import parking router
try:
    from parking_api import router as parking_router
    parking_available = True
except:
    parking_available = False
    print("⚠️ Parking module not available")

# Initialize FastAPI app
app = FastAPI(
    title="DeepGuardians - Traffic & Parking Prediction API",
    description="Real-time LSTM-based traffic congestion and parking availability predictor",
    version="2.0.0"
)

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Include parking router if available
if parking_available:
    app.include_router(parking_router)

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
    average_speed: float
    lane_occupancy: float
    flow_rate: float
    time_of_day: float
    waiting_time: float
    avg_speed_kmph: float
    density_veh_per_km: float
    avg_wait_time_s: float
    occupancy_pct: float
    flow_veh_per_hr: float
    queue_length_veh: float
    avg_accel_ms2: float
    SRI: float


@app.get("/")
def home():
    """Home endpoint with API information."""
    return {
        "message": "DeepGuardians - Traffic & Parking Prediction API",
        "version": "2.0.0",
        "docs": "http://127.0.0.1:8000/docs",
        "parking_demo": "http://127.0.0.1:8000/parking-demo",
        "endpoints": {
            "traffic": "POST /predict",
            "parking": "POST /parking/nearby, /parking/predict, /parking/route-with-parking"
        }
    }


@app.get("/parking-demo")
def parking_demo():
    """Serve the parking prediction demo page"""
    return FileResponse("static/parking.html")


@app.post("/predict")
def predict(data: TrafficInput):
    """
    Predict traffic congestion level from live traffic features.
    
    Required 10 consecutive calls to build sequence window before predictions begin.
    
    Args:
        vehicle_count: Number of vehicles on road
        average_speed: Average vehicle speed (km/h)
        lane_occupancy: Occupancy percentage (0-1)
        flow_rate: Traffic flow rate (vehicles/minute)
        time_of_day: Hour of day (0-23)
        waiting_time: Average waiting time (seconds)
        avg_speed_kmph: Average speed in km/h
        density_veh_per_km: Vehicle density per km
        avg_wait_time_s: Average wait time in seconds
        occupancy_pct: Occupancy percentage
        flow_veh_per_hr: Flow rate in vehicles per hour
        queue_length_veh: Queue length in vehicles
        avg_accel_ms2: Average acceleration (m/s²)
        SRI: Speed Reduction Index
    
    Returns:
        - While collecting: {"status": "collecting_data", "samples_collected": N, "required_points": 10}
        - With prediction: {"status": "success", "congestion_level": "High", "confidence": 2.1}
    
    Example request:
        {
            "vehicle_count": 40,
            "average_speed": 25,
            "lane_occupancy": 0.65,
            "flow_rate": 850,
            "time_of_day": 18,
            "waiting_time": 15,
            "avg_speed_kmph": 28,
            "density_veh_per_km": 35,
            "avg_wait_time_s": 20,
            "occupancy_pct": 45,
            "flow_veh_per_hr": 1250,
            "queue_length_veh": 10,
            "avg_accel_ms2": 0.8,
            "SRI": 2.5
        }
    """
    try:
        # Extract features as list in the correct order (matching training data)
        features = [
            data.vehicle_count,
            data.average_speed,
            data.lane_occupancy,
            data.flow_rate,
            data.time_of_day,
            data.waiting_time,
            data.avg_speed_kmph,
            data.density_veh_per_km,
            data.avg_wait_time_s,
            data.occupancy_pct,
            data.flow_veh_per_hr,
            data.queue_length_veh,
            data.avg_accel_ms2,
            data.SRI
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
