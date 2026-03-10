"""
Test script for Traffic Congestion Prediction API

This script demonstrates how to use the FastAPI prediction server.

Usage:
    1. Start the server:
       uvicorn backend.api:app --reload
    
    2. Run this test:
       python test_api.py
"""

import requests
import json
import time
import random

BASE_URL = "http://127.0.0.1:8000"


def test_health():
    """Test health endpoint."""
    print("\n🏥 Testing Health Endpoint:")
    print("-" * 50)
    response = requests.get(f"{BASE_URL}/health")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200


def test_home():
    """Test home endpoint."""
    print("\n🏠 Testing Home Endpoint:")
    print("-" * 50)
    response = requests.get(f"{BASE_URL}/")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200


def generate_traffic_data(hour: int, congestion_level: str = "normal"):
    """
    Generate realistic traffic data with all 14 features.
    
    Args:
        hour: Hour of day (0-23)
        congestion_level: "low", "normal", "high", "severe"
    
    Returns:
        dict: Traffic feature data with all 14 features
    """
    if congestion_level == "low":
        vehicle_count = random.uniform(20, 40)
        average_speed = random.uniform(45, 60)
        lane_occupancy = random.uniform(0.2, 0.4)
        flow_rate = random.uniform(500, 800)
        waiting_time = random.uniform(0, 10)
        avg_speed_kmph = random.uniform(50, 70)
        density_veh_per_km = random.uniform(5, 15)
        avg_wait_time_s = random.uniform(5, 15)
        occupancy_pct = random.uniform(10, 25)
        flow_veh_per_hr = random.uniform(1500, 1800)
        queue_length_veh = random.uniform(0, 5)
        avg_accel_ms2 = random.uniform(0.5, 1.0)
        SRI = random.uniform(-2, 2)
    elif congestion_level == "normal":
        vehicle_count = random.uniform(40, 70)
        average_speed = random.uniform(30, 45)
        lane_occupancy = random.uniform(0.4, 0.6)
        flow_rate = random.uniform(800, 1200)
        waiting_time = random.uniform(10, 30)
        avg_speed_kmph = random.uniform(35, 50)
        density_veh_per_km = random.uniform(20, 40)
        avg_wait_time_s = random.uniform(15, 30)
        occupancy_pct = random.uniform(30, 50)
        flow_veh_per_hr = random.uniform(1200, 1600)
        queue_length_veh = random.uniform(5, 15)
        avg_accel_ms2 = random.uniform(0.2, 0.8)
        SRI = random.uniform(0, 3)
    elif congestion_level == "high":
        vehicle_count = random.uniform(70, 90)
        average_speed = random.uniform(15, 30)
        lane_occupancy = random.uniform(0.6, 0.8)
        flow_rate = random.uniform(1200, 1500)
        waiting_time = random.uniform(30, 60)
        avg_speed_kmph = random.uniform(20, 35)
        density_veh_per_km = random.uniform(40, 60)
        avg_wait_time_s = random.uniform(30, 60)
        occupancy_pct = random.uniform(50, 70)
        flow_veh_per_hr = random.uniform(800, 1200)
        queue_length_veh = random.uniform(15, 30)
        avg_accel_ms2 = random.uniform(-0.5, 0.3)
        SRI = random.uniform(2, 5)
    else:  # severe
        vehicle_count = random.uniform(90, 120)
        average_speed = random.uniform(5, 15)
        lane_occupancy = random.uniform(0.8, 1.0)
        flow_rate = random.uniform(1500, 2000)
        waiting_time = random.uniform(60, 150)
        avg_speed_kmph = random.uniform(5, 20)
        density_veh_per_km = random.uniform(60, 95)
        avg_wait_time_s = random.uniform(60, 130)
        occupancy_pct = random.uniform(70, 100)
        flow_veh_per_hr = random.uniform(500, 800)
        queue_length_veh = random.uniform(30, 60)
        avg_accel_ms2 = random.uniform(-1.0, -0.2)
        SRI = random.uniform(4, 6)

    return {
        "vehicle_count": vehicle_count,
        "average_speed": average_speed,
        "lane_occupancy": lane_occupancy,
        "flow_rate": flow_rate,
        "time_of_day": hour,
        "waiting_time": waiting_time,
        "avg_speed_kmph": avg_speed_kmph,
        "density_veh_per_km": density_veh_per_km,
        "avg_wait_time_s": avg_wait_time_s,
        "occupancy_pct": occupancy_pct,
        "flow_veh_per_hr": flow_veh_per_hr,
        "queue_length_veh": queue_length_veh,
        "avg_accel_ms2": avg_accel_ms2,
        "SRI": SRI
    }


def test_predictions():
    """Test prediction endpoint with multiple requests."""
    print("\n🚦 Testing Prediction Endpoint:")
    print("-" * 50)
    
    # Reset buffer first
    print("\n1️⃣ Resetting buffer...")
    response = requests.post(f"{BASE_URL}/reset")
    print(response.json())
    
    # Simulate 15 consecutive traffic observations
    print("\n2️⃣ Sending 15 traffic observations (10 required to build sequence)...")
    print("-" * 50)
    
    scenarios = [
        ("Morning Rush (6 AM, High)", 6, "high"),
        ("Morning Rush (7 AM, High)", 7, "high"),
        ("Morning Highway (8 AM, High)", 8, "high"),
        ("Late Morning (10 AM, Normal)", 10, "normal"),
        ("Late Morning (11 AM, Normal)", 11, "normal"),
        ("Midday (12 PM, Low)", 12, "low"),
        ("Afternoon (2 PM, Normal)", 14, "normal"),
        ("Afternoon (3 PM, Normal)", 15, "normal"),
        ("Evening (5 PM, High)", 17, "high"),
        ("Evening Rush (6 PM, High)", 18, "high"),
        ("Evening Rush (7 PM, Severe)", 19, "severe"),
        ("Evening (8 PM, High)", 20, "high"),
        ("Night (9 PM, Normal)", 21, "normal"),
        ("Night (10 PM, Low)", 22, "low"),
        ("Late Night (11 PM, Low)", 23, "low"),
    ]
    
    for i, (scenario, hour, level) in enumerate(scenarios, 1):
        data = generate_traffic_data(hour, level)
        
        print(f"\n🔹 Request {i}: {scenario}")
        print(f"   Input: {data}")
        
        response = requests.post(
            f"{BASE_URL}/predict",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        result = response.json()
        print(f"   Response: {result}")
        
        # Small delay between requests
        time.sleep(0.5)
    
    return True


def test_single_prediction():
    """Test a single prediction with specific data."""
    print("\n📊 Testing Single Prediction:")
    print("-" * 50)

    # Reset for fresh test
    requests.post(f"{BASE_URL}/reset")

    # Example data with all 14 features
    example_data = {
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

    print(f"Sending example data: {json.dumps(example_data, indent=2)}")

    response = requests.post(
        f"{BASE_URL}/predict",
        json=example_data
    )

    result = response.json()
    print(f"\nResponse:\n{json.dumps(result, indent=2)}")

    return response.status_code == 200


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🚗 TRAFFIC CONGESTION PREDICTION API - TEST SUITE")
    print("=" * 60)
    
    try:
        # Test health
        if not test_health():
            print("\n❌ Health check failed! Make sure the server is running:")
            print("   uvicorn backend.api:app --reload")
            return
        
        # Test home
        if not test_home():
            print("\n❌ Home endpoint failed!")
            return
        
        # Test single prediction
        if not test_single_prediction():
            print("\n❌ Single prediction failed!")
            return
        
        # Test multiple predictions
        if not test_predictions():
            print("\n❌ Multiple predictions failed!")
            return
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n📚 API Documentation: http://127.0.0.1:8000/docs")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server!")
        print("\nMake sure the FastAPI server is running:")
        print("   cd backend")
        print("   uvicorn api:app --reload")


if __name__ == "__main__":
    main()
