"""
Parking API Integration
Adds parking prediction endpoints to the FastAPI backend
Integrates with traffic module for comprehensive navigation assistance
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List
import sys
sys.path.append('src/parking')

from src.parking.parking_predict import get_predictor


# Create router
router = APIRouter(prefix="/parking", tags=["parking"])


# Pydantic models for request/response
class ParkingPredictionRequest(BaseModel):
    parking_id: str
    arrival_datetime: Optional[str] = None  # ISO format
    weather: Optional[str] = "Clear"


class DestinationRequest(BaseModel):
    destination_lat: float
    destination_lon: float
    arrival_datetime: Optional[str] = None
    radius_km: Optional[float] = 2.0


class RouteWithParkingRequest(BaseModel):
    origin_lat: float
    origin_lon: float
    destination_lat: float
    destination_lon: float
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None


class OptimalTimeRequest(BaseModel):
    parking_id: str
    date: str  # YYYY-MM-DD format
    time_range_hours: Optional[int] = 24


# Endpoints
@router.get("/health")
async def parking_health():
    """Check if parking module is ready"""
    try:
        pred = get_predictor()
        return {
            "status": "healthy",
            "models_loaded": True,
            "parking_locations": len(pred.parking_locations)
        }
    except Exception as e:
        return {
            "status": "error",
            "models_loaded": False,
            "error": str(e)
        }


@router.post("/predict")
async def predict_parking_availability(request: ParkingPredictionRequest):
    """
    Predict parking availability for a specific parking lot
    
    Example:
    ```json
    {
        "parking_id": "P013",
        "arrival_datetime": "2024-03-15T14:30:00",
        "weather": "Clear"
    }
    ```
    """
    try:
        pred = get_predictor()
        
        # Parse arrival time
        if request.arrival_datetime:
            arrival_dt = datetime.fromisoformat(request.arrival_datetime)
        else:
            arrival_dt = datetime.now() + timedelta(minutes=30)
        
        # Check if parking exists
        if request.parking_id not in pred.parking_locations:
            raise HTTPException(status_code=404, detail="Parking location not found")
        
        # Get prediction
        result = pred.predict_availability_category(
            request.parking_id,
            arrival_dt,
            request.weather
        )
        
        # Get location details
        location = pred.parking_locations[request.parking_id]
        
        return {
            "status": "success",
            "parking_id": request.parking_id,
            "parking_name": location['parking_name'],
            "arrival_time": arrival_dt.isoformat(),
            "availability": result['category'],
            "confidence": result['confidence'],
            "probabilities": result['probabilities'],
            "location": {
                "latitude": location['latitude'],
                "longitude": location['longitude'],
                "capacity": location['capacity'],
                "hourly_rate": location['hourly_rate'],
                "type": location['location_type']
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/nearby")
async def find_nearby_parking(request: DestinationRequest):
    """
    Find nearby parking options for a destination
    
    Example:
    ```json
    {
        "destination_lat": 18.9220,
        "destination_lon": 72.8347,
        "arrival_datetime": "2024-03-15T14:30:00",
        "radius_km": 2.0
    }
    ```
    """
    try:
        pred = get_predictor()
        
        # Parse arrival time
        if request.arrival_datetime:
            arrival_dt = datetime.fromisoformat(request.arrival_datetime)
        else:
            arrival_dt = datetime.now() + timedelta(minutes=30)
        
        # Find nearby parking
        nearby = pred.find_nearby_parking(
            request.destination_lat,
            request.destination_lon,
            request.radius_km,
            arrival_dt
        )
        
        return {
            "status": "success",
            "destination": {
                "latitude": request.destination_lat,
                "longitude": request.destination_lon
            },
            "arrival_time": arrival_dt.isoformat(),
            "radius_km": request.radius_km,
            "parking_options": nearby,
            "total_found": len(nearby)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimal-time")
async def get_optimal_parking_time(request: OptimalTimeRequest):
    """
    Get optimal arrival times for a parking location
    
    Example:
    ```json
    {
        "parking_id": "P013",
        "date": "2024-03-15",
        "time_range_hours": 24
    }
    ```
    """
    try:
        pred = get_predictor()
        
        # Check if parking exists
        if request.parking_id not in pred.parking_locations:
            raise HTTPException(status_code=404, detail="Parking location not found")
        
        # Parse date
        target_date = datetime.strptime(request.date, "%Y-%m-%d").date()
        
        # Get recommendations
        recommendations = pred.recommend_optimal_time(
            request.parking_id,
            target_date,
            request.time_range_hours
        )
        
        # Get location details
        location = pred.parking_locations[request.parking_id]
        
        return {
            "status": "success",
            "parking_id": request.parking_id,
            "parking_name": location['parking_name'],
            "date": request.date,
            "optimal_times": recommendations,
            "best_time": recommendations[0] if recommendations else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/route-with-parking")
async def route_with_parking(request: RouteWithParkingRequest):
    """
    Complete route planning with parking recommendation
    Integrates traffic prediction with parking availability
    
    Example:
    ```json
    {
        "origin_lat": 19.0760,
        "origin_lon": 72.8777,
        "destination_lat": 18.9220,
        "destination_lon": 72.8347,
        "arrival_time": "2024-03-15T14:30:00"
    }
    ```
    """
    try:
        pred = get_predictor()
        
        # Parse time
        if request.arrival_time:
            arrival_dt = datetime.fromisoformat(request.arrival_time)
        elif request.departure_time:
            departure_dt = datetime.fromisoformat(request.departure_time)
            # Estimate 30 min travel time (you can integrate with traffic module here)
            arrival_dt = departure_dt + timedelta(minutes=30)
        else:
            arrival_dt = datetime.now() + timedelta(minutes=30)
        
        # Get parking predictions for destination
        parking_result = pred.predict_for_destination(
            request.destination_lat,
            request.destination_lon,
            arrival_dt,
            radius_km=2.0
        )
        
        return {
            "status": "success",
            "route": {
                "origin": {
                    "latitude": request.origin_lat,
                    "longitude": request.origin_lon
                },
                "destination": parking_result['destination'],
                "estimated_arrival": arrival_dt.isoformat()
            },
            "parking_recommendation": parking_result['recommended_parking'],
            "alternative_parking": parking_result['nearby_parking'][1:4] if len(parking_result['nearby_parking']) > 1 else [],
            "optimal_arrival_times": parking_result['optimal_arrival_times']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/locations")
async def get_all_parking_locations():
    """Get list of all parking locations"""
    try:
        pred = get_predictor()
        
        locations = []
        for parking_id, details in pred.parking_locations.items():
            locations.append({
                "parking_id": parking_id,
                "name": details['parking_name'],
                "latitude": details['latitude'],
                "longitude": details['longitude'],
                "capacity": details['capacity'],
                "hourly_rate": details['hourly_rate'],
                "type": details['location_type']
            })
        
        return {
            "status": "success",
            "total_locations": len(locations),
            "locations": locations
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/location/{parking_id}")
async def get_parking_location_details(parking_id: str):
    """Get details for a specific parking location"""
    try:
        pred = get_predictor()
        
        if parking_id not in pred.parking_locations:
            raise HTTPException(status_code=404, detail="Parking location not found")
        
        location = pred.parking_locations[parking_id]
        
        return {
            "status": "success",
            "parking_id": parking_id,
            **location
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
