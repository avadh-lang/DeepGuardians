"""
Generate synthetic parking dataset for Mumbai locations
Creates realistic parking occupancy patterns based on:
- Time of day
- Day of week
- Location type (commercial, residential, tourist, transit)
- Nearby traffic patterns
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Mumbai parking locations with real coordinates
PARKING_LOCATIONS = [
    # Commercial Areas
    {"id": "P001", "name": "BKC Corporate Park", "lat": 19.0616, "lon": 72.8689, "capacity": 500, "type": "commercial", "hourly_rate": 50},
    {"id": "P002", "name": "Nariman Point Business Hub", "lat": 18.9254, "lon": 72.8243, "capacity": 350, "type": "commercial", "hourly_rate": 60},
    {"id": "P003", "name": "Lower Parel Office Complex", "lat": 18.9969, "lon": 72.8308, "capacity": 400, "type": "commercial", "hourly_rate": 45},
    {"id": "P004", "name": "Andheri SEEPZ IT Park", "lat": 19.1136, "lon": 72.8697, "capacity": 600, "type": "commercial", "hourly_rate": 40},
    
    # Shopping & Entertainment
    {"id": "P005", "name": "Phoenix Palladium Mall", "lat": 19.0626, "lon": 72.8327, "capacity": 800, "type": "shopping", "hourly_rate": 30},
    {"id": "P006", "name": "Inorbit Mall Malad", "lat": 19.1760, "lon": 72.8347, "capacity": 1000, "type": "shopping", "hourly_rate": 25},
    {"id": "P007", "name": "R City Mall Ghatkopar", "lat": 19.0863, "lon": 72.9081, "capacity": 700, "type": "shopping", "hourly_rate": 30},
    {"id": "P008", "name": "Oberoi Mall Goregaon", "lat": 19.1676, "lon": 72.8489, "capacity": 600, "type": "shopping", "hourly_rate": 25},
    
    # Transit Hubs
    {"id": "P009", "name": "Chhatrapati Shivaji Terminus", "lat": 18.9398, "lon": 72.8355, "capacity": 450, "type": "transit", "hourly_rate": 20},
    {"id": "P010", "name": "Bandra Terminus Station", "lat": 19.0626, "lon": 72.8409, "capacity": 300, "type": "transit", "hourly_rate": 20},
    {"id": "P011", "name": "Andheri Station East", "lat": 19.1197, "lon": 72.8464, "capacity": 350, "type": "transit", "hourly_rate": 15},
    {"id": "P012", "name": "Dadar Station West", "lat": 19.0179, "lon": 72.8439, "capacity": 280, "type": "transit", "hourly_rate": 15},
    
    # Tourist & Recreational
    {"id": "P013", "name": "Gateway of India Plaza", "lat": 18.9220, "lon": 72.8347, "capacity": 200, "type": "tourist", "hourly_rate": 70},
    {"id": "P014", "name": "Marine Drive Parking", "lat": 18.9432, "lon": 72.8236, "capacity": 150, "type": "tourist", "hourly_rate": 80},
    {"id": "P015", "name": "Juhu Beach Parking", "lat": 19.0990, "lon": 72.8268, "capacity": 300, "type": "tourist", "hourly_rate": 40},
    {"id": "P016", "name": "Sanjay Gandhi National Park", "lat": 19.2274, "lon": 72.9116, "capacity": 400, "type": "tourist", "hourly_rate": 20},
    
    # Residential Areas
    {"id": "P017", "name": "Powai Lake Residential", "lat": 19.1176, "lon": 72.9060, "capacity": 250, "type": "residential", "hourly_rate": 30},
    {"id": "P018", "name": "Bandra West Residency", "lat": 19.0596, "lon": 72.8295, "capacity": 200, "type": "residential", "hourly_rate": 35},
    {"id": "P019", "name": "Worli Sea Face Apartments", "lat": 19.0144, "lon": 72.8170, "capacity": 180, "type": "residential", "hourly_rate": 40},
    {"id": "P020", "name": "Andheri West Housing", "lat": 19.1368, "lon": 72.8269, "capacity": 220, "type": "residential", "hourly_rate": 25},
    
    # Hospitals & Healthcare
    {"id": "P021", "name": "Lilavati Hospital", "lat": 19.0525, "lon": 72.8321, "capacity": 300, "type": "hospital", "hourly_rate": 25},
    {"id": "P022", "name": "KEM Hospital Parel", "lat": 19.0030, "lon": 72.8417, "capacity": 250, "type": "hospital", "hourly_rate": 20},
    
    # Educational
    {"id": "P023", "name": "IIT Bombay Campus", "lat": 19.1334, "lon": 72.9133, "capacity": 500, "type": "educational", "hourly_rate": 10},
    {"id": "P024", "name": "Mumbai University Fort", "lat": 18.9299, "lon": 72.8313, "capacity": 200, "type": "educational", "hourly_rate": 15},
    
    # Airport
    {"id": "P025", "name": "Airport T1 Parking", "lat": 19.0896, "lon": 72.8656, "capacity": 1200, "type": "airport", "hourly_rate": 100},
    {"id": "P026", "name": "Airport T2 Parking", "lat": 19.0886, "lon": 72.8679, "capacity": 1500, "type": "airport", "hourly_rate": 100},
]


def get_base_occupancy_pattern(location_type, hour, day_of_week):
    """
    Calculate base occupancy rate based on location type and time
    Returns occupancy percentage (0-1)
    """
    is_weekend = day_of_week >= 5
    
    patterns = {
        "commercial": {
            "weekday": {
                "peak_hours": [9, 10, 11, 14, 15, 16, 17],
                "peak_occupancy": 0.90,
                "off_peak_occupancy": 0.20
            },
            "weekend": {
                "peak_hours": [],
                "peak_occupancy": 0.15,
                "off_peak_occupancy": 0.10
            }
        },
        "shopping": {
            "weekday": {
                "peak_hours": [12, 13, 18, 19, 20],
                "peak_occupancy": 0.75,
                "off_peak_occupancy": 0.40
            },
            "weekend": {
                "peak_hours": [11, 12, 13, 14, 15, 16, 17, 18, 19],
                "peak_occupancy": 0.95,
                "off_peak_occupancy": 0.60
            }
        },
        "transit": {
            "weekday": {
                "peak_hours": [7, 8, 9, 17, 18, 19, 20],
                "peak_occupancy": 0.95,
                "off_peak_occupancy": 0.50
            },
            "weekend": {
                "peak_hours": [10, 11, 17, 18, 19],
                "peak_occupancy": 0.70,
                "off_peak_occupancy": 0.40
            }
        },
        "tourist": {
            "weekday": {
                "peak_hours": [16, 17, 18, 19],
                "peak_occupancy": 0.70,
                "off_peak_occupancy": 0.30
            },
            "weekend": {
                "peak_hours": [10, 11, 12, 13, 14, 15, 16, 17, 18],
                "peak_occupancy": 0.90,
                "off_peak_occupancy": 0.60
            }
        },
        "residential": {
            "weekday": {
                "peak_hours": [20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6],
                "peak_occupancy": 0.85,
                "off_peak_occupancy": 0.40
            },
            "weekend": {
                "peak_hours": [22, 23, 0, 1, 2, 3, 4, 5, 6, 7, 8],
                "peak_occupancy": 0.90,
                "off_peak_occupancy": 0.70
            }
        },
        "hospital": {
            "weekday": {
                "peak_hours": [9, 10, 11, 15, 16, 17],
                "peak_occupancy": 0.80,
                "off_peak_occupancy": 0.50
            },
            "weekend": {
                "peak_hours": [10, 11, 16, 17],
                "peak_occupancy": 0.70,
                "off_peak_occupancy": 0.45
            }
        },
        "educational": {
            "weekday": {
                "peak_hours": [8, 9, 10, 14, 15, 16],
                "peak_occupancy": 0.85,
                "off_peak_occupancy": 0.20
            },
            "weekend": {
                "peak_hours": [],
                "peak_occupancy": 0.10,
                "off_peak_occupancy": 0.05
            }
        },
        "airport": {
            "weekday": {
                "peak_hours": [5, 6, 7, 8, 15, 16, 17, 18],
                "peak_occupancy": 0.85,
                "off_peak_occupancy": 0.60
            },
            "weekend": {
                "peak_hours": [6, 7, 8, 9, 16, 17, 18, 19],
                "peak_occupancy": 0.90,
                "off_peak_occupancy": 0.65
            }
        }
    }
    
    period = "weekend" if is_weekend else "weekday"
    pattern = patterns.get(location_type, patterns["commercial"])[period]
    
    if hour in pattern["peak_hours"]:
        return pattern["peak_occupancy"]
    else:
        return pattern["off_peak_occupancy"]


def generate_parking_data(start_date, end_date, locations):
    """
    Generate time-series parking data for all locations
    """
    data = []
    current_date = start_date
    
    print(f"Generating parking data from {start_date} to {end_date}...")
    
    while current_date <= end_date:
        for hour in range(24):
            timestamp = current_date.replace(hour=hour, minute=0, second=0)
            day_of_week = timestamp.weekday()
            
            for location in locations:
                # Base occupancy from pattern
                base_occupancy = get_base_occupancy_pattern(
                    location["type"], 
                    hour, 
                    day_of_week
                )
                
                # Add randomness (±10%)
                noise = np.random.uniform(-0.10, 0.10)
                occupancy_rate = np.clip(base_occupancy + noise, 0, 1)
                
                # Calculate actual values
                occupied_spots = int(location["capacity"] * occupancy_rate)
                available_spots = location["capacity"] - occupied_spots
                
                # Additional features
                is_peak_hour = hour in [8, 9, 17, 18, 19]
                is_weekend = day_of_week >= 5
                
                # Weather simulation (random)
                weather_conditions = ["Clear", "Rain", "Cloudy"]
                weather_weights = [0.7, 0.2, 0.1]
                weather = np.random.choice(weather_conditions, p=weather_weights)
                
                # If raining, reduce occupancy slightly (people avoid going out)
                if weather == "Rain":
                    occupancy_rate *= 0.85
                    occupied_spots = int(location["capacity"] * occupancy_rate)
                    available_spots = location["capacity"] - occupied_spots
                
                data.append({
                    "parking_id": location["id"],
                    "parking_name": location["name"],
                    "latitude": location["lat"],
                    "longitude": location["lon"],
                    "capacity": location["capacity"],
                    "occupied_spots": occupied_spots,
                    "available_spots": available_spots,
                    "occupancy_rate": round(occupancy_rate * 100, 2),
                    "timestamp": timestamp,
                    "hour": hour,
                    "day_of_week": day_of_week,
                    "is_weekend": is_weekend,
                    "is_peak_hour": is_peak_hour,
                    "location_type": location["type"],
                    "hourly_rate": location["hourly_rate"],
                    "weather": weather,
                    "month": timestamp.month,
                    "day_of_month": timestamp.day
                })
        
        current_date += timedelta(days=1)
    
    return pd.DataFrame(data)


def main():
    print("=" * 60)
    print("Mumbai Parking Dataset Generator")
    print("=" * 60)
    
    # Generate 6 months of data
    start_date = datetime(2023, 7, 1)
    end_date = datetime(2024, 12, 31)
    
    print(f"\nLocations: {len(PARKING_LOCATIONS)}")
    print(f"Date Range: {start_date.date()} to {end_date.date()}")
    print(f"Total Days: {(end_date - start_date).days + 1}")
    print(f"Records per day: {len(PARKING_LOCATIONS) * 24}")
    print(f"Expected total records: {(end_date - start_date).days * len(PARKING_LOCATIONS) * 24}")
    
    df = generate_parking_data(start_date, end_date, PARKING_LOCATIONS)
    
    print(f"\n✓ Generated {len(df)} records")
    print(f"\nDataset Info:")
    print(f"  - Columns: {len(df.columns)}")
    print(f"  - Memory Usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    
    # Save dataset
    output_path = "dataset/parking_dataset.csv"
    df.to_csv(output_path, index=False)
    print(f"\n✓ Saved to: {output_path}")
    
    # Display statistics
    print("\n" + "=" * 60)
    print("Dataset Statistics")
    print("=" * 60)
    print(f"\nOccupancy Rate Statistics:")
    print(df.groupby("location_type")["occupancy_rate"].describe())
    
    print(f"\nSample Records:")
    print(df.head(10).to_string())
    
    print("\n" + "=" * 60)
    print("Dataset generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
