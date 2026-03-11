"""
Parking Prediction Module
Combines LSTM and Random Forest for comprehensive parking availability prediction
"""
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from datetime import datetime, timedelta
import pandas as pd


class ParkingPredictor:
    """
    Hybrid parking prediction system using LSTM + Random Forest
    """
    
    def __init__(self):
        """Initialize and load models"""
        self.lstm_model = None
        self.rf_model = None
        self.scaler = None
        self.encoder = None
        self.feature_cols = None
        self.parking_locations = None
        self.load_models()
        self.load_parking_locations()
    
    def load_models(self):
        """Load trained models and preprocessing objects"""
        try:
            # Load LSTM model (optional for now)
            try:
                self.lstm_model = load_model("../../models/parking_lstm_model.h5")
                print("✓ LSTM model loaded")
            except:
                print("⚠️ LSTM model not available (using RF only)")
                self.lstm_model = None
            
            # Load Random Forest model
            self.rf_model = joblib.load("../../models/parking_rf_model.pkl")
            print("✓ Random Forest model loaded")
            
            # Load preprocessing objects
            self.scaler = joblib.load("../../models/parking_rf_scaler.pkl")
            self.encoder = joblib.load("../../models/parking_encoder.pkl")
            self.feature_cols = joblib.load("../../models/parking_feature_cols.pkl")
            print("✓ Preprocessing objects loaded")
            
        except Exception as e:
            print(f"Error loading models: {e}")
            raise
    
    def load_parking_locations(self):
        """Load parking location data"""
        # Load from dataset to get location information
        df = pd.read_csv("../../dataset/parking_dataset.csv")
        
        # Get unique parking locations with their details
        self.parking_locations = df.groupby('parking_id').agg({
            'parking_name': 'first',
            'latitude': 'first',
            'longitude': 'first',
            'capacity': 'first',
            'location_type': 'first',
            'hourly_rate': 'first'
        }).to_dict('index')
        
        print(f"✓ Loaded {len(self.parking_locations)} parking locations")
    
    def prepare_features(self, hour, day_of_week, is_weekend, is_peak_hour, 
                        capacity, hourly_rate, location_type, weather, month):
        """
        Prepare features for Random Forest prediction
        """
        # Engineered features
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)
        day_sin = np.sin(2 * np.pi * day_of_week / 7)
        day_cos = np.cos(2 * np.pi * day_of_week / 7)
        
        # Encode categorical
        location_type_map = {'commercial': 0, 'shopping': 1, 'transit': 2, 
                            'tourist': 3, 'residential': 4, 'hospital': 5, 
                            'educational': 6, 'airport': 7}
        weather_map = {'Clear': 0, 'Rain': 1, 'Cloudy': 2}
        
        location_encoded = location_type_map.get(location_type, 0)
        weather_encoded = weather_map.get(weather, 0)
        
        # Create feature dict
        features = {
            'hour': hour,
            'day_of_week': day_of_week,
            'is_weekend': int(is_weekend),
            'is_peak_hour': int(is_peak_hour),
            'capacity': capacity,
            'hourly_rate': hourly_rate,
            'hour_sin': hour_sin,
            'hour_cos': hour_cos,
            'day_sin': day_sin,
            'day_cos': day_cos,
            'month': month,
            'location_encoded': location_encoded,
            'weather_encoded': weather_encoded
        }
        
        # Create array in correct order
        X = np.array([[features[col] for col in self.feature_cols]])
        
        # Scale
        X_scaled = self.scaler.transform(X)
        
        return X_scaled
    
    def predict_availability_category(self, parking_id, target_datetime, weather="Clear"):
        """
        Predict availability category using Random Forest
        Returns: category (abundant, available, limited, critical)
        """
        location = self.parking_locations[parking_id]
        
        hour = target_datetime.hour
        day_of_week = target_datetime.weekday()
        is_weekend = day_of_week >= 5
        is_peak_hour = hour in [8, 9, 17, 18, 19]
        month = target_datetime.month
        
        # Prepare features
        X = self.prepare_features(
            hour, day_of_week, is_weekend, is_peak_hour,
            location['capacity'], location['hourly_rate'],
            location['location_type'], weather, month
        )
        
        # Predict
        category_encoded = self.rf_model.predict(X)[0]
        category = self.encoder.inverse_transform([category_encoded])[0]
        
        # Get probability
        probabilities = self.rf_model.predict_proba(X)[0]
        confidence = probabilities[category_encoded]
        
        return {
            'category': category,
            'confidence': float(confidence),
            'probabilities': {
                cat: float(prob) 
                for cat, prob in zip(self.encoder.classes_, probabilities)
            }
        }
    
    def predict_occupancy_lstm(self, parking_id, historical_data):
        """
        Predict future occupancy using LSTM
        
        Args:
            parking_id: parking location ID
            historical_data: array of shape (24, 7) - last 24 hours
        
        Returns:
            predicted occupancy rate (0-100)
        """
        # Reshape for model
        X = historical_data.reshape(1, 24, 7)
        
        # Predict (returns normalized 0-1)
        prediction = self.lstm_model.predict(X, verbose=0)[0][0]
        
        # Convert to percentage
        occupancy_rate = prediction * 100
        
        return float(np.clip(occupancy_rate, 0, 100))
    
    def find_nearby_parking(self, lat, lon, radius_km=2.0, target_datetime=None):
        """
        Find nearby parking locations within radius
        
        Args:
            lat, lon: destination coordinates
            radius_km: search radius in kilometers
            target_datetime: when you'll arrive (default: now + 30 min)
        
        Returns:
            list of parking options with predictions
        """
        if target_datetime is None:
            target_datetime = datetime.now() + timedelta(minutes=30)
        
        nearby = []
        
        for parking_id, location in self.parking_locations.items():
            # Calculate distance (simple approximation)
            lat_diff = (location['latitude'] - lat) * 111  # km per degree
            lon_diff = (location['longitude'] - lon) * 111 * np.cos(np.radians(lat))
            distance = np.sqrt(lat_diff**2 + lon_diff**2)
            
            if distance <= radius_km:
                # Get prediction
                prediction = self.predict_availability_category(parking_id, target_datetime)
                
                nearby.append({
                    'parking_id': parking_id,
                    'name': location['parking_name'],
                    'latitude': location['latitude'],
                    'longitude': location['longitude'],
                    'distance_km': round(distance, 2),
                    'capacity': location['capacity'],
                    'hourly_rate': location['hourly_rate'],
                    'location_type': location['location_type'],
                    'availability': prediction['category'],
                    'confidence': prediction['confidence']
                })
        
        # Sort by availability and distance
        category_priority = {'abundant': 0, 'available': 1, 'limited': 2, 'critical': 3}
        nearby.sort(key=lambda x: (category_priority[x['availability']], x['distance_km']))
        
        return nearby
    
    def recommend_optimal_time(self, parking_id, date, time_range_hours=24):
        """
        Recommend best arrival times for parking
        
        Args:
            parking_id: parking location ID
            date: target date
            time_range_hours: hours to consider (default 24)
        
        Returns:
            list of time slots with availability predictions
        """
        recommendations = []
        
        start_datetime = datetime.combine(date, datetime.min.time())
        
        for hour_offset in range(time_range_hours):
            check_time = start_datetime + timedelta(hours=hour_offset)
            
            prediction = self.predict_availability_category(parking_id, check_time)
            
            recommendations.append({
                'time': check_time.strftime('%H:%M'),
                'datetime': check_time.isoformat(),
                'hour': check_time.hour,
                'availability': prediction['category'],
                'confidence': prediction['confidence']
            })
        
        # Sort by best availability
        category_priority = {'abundant': 0, 'available': 1, 'limited': 2, 'critical': 3}
        recommendations.sort(key=lambda x: category_priority[x['availability']])
        
        return recommendations
    
    def predict_for_destination(self, destination_lat, destination_lon, 
                               arrival_datetime=None, radius_km=2.0):
        """
        Complete parking prediction for a destination
        Combines nearby search with availability predictions
        
        Args:
            destination_lat, destination_lon: destination coordinates
            arrival_datetime: when you'll arrive
            radius_km: search radius
        
        Returns:
            dict with parking recommendations and optimal times
        """
        if arrival_datetime is None:
            arrival_datetime = datetime.now() + timedelta(minutes=30)
        
        # Find nearby parking
        nearby = self.find_nearby_parking(destination_lat, destination_lon, 
                                         radius_km, arrival_datetime)
        
        # Get top recommendation
        top_parking = nearby[0] if nearby else None
        
        # Get optimal times for top recommendation
        optimal_times = []
        if top_parking:
            optimal_times = self.recommend_optimal_time(
                top_parking['parking_id'], 
                arrival_datetime.date()
            )[:5]  # Top 5 times
        
        return {
            'destination': {
                'latitude': destination_lat,
                'longitude': destination_lon
            },
            'arrival_time': arrival_datetime.isoformat(),
            'nearby_parking': nearby[:5],  # Top 5 locations
            'recommended_parking': top_parking,
            'optimal_arrival_times': optimal_times
        }


# Create global predictor instance
predictor = None

def get_predictor():
    """Get or create predictor instance"""
    global predictor
    if predictor is None:
        predictor = ParkingPredictor()
    return predictor


if __name__ == "__main__":
    print("Testing Parking Predictor...")
    
    pred = ParkingPredictor()
    
    # Test prediction for a destination (Gateway of India area)
    print("\n" + "="*60)
    print("TEST: Parking prediction for Gateway of India")
    print("="*60)
    
    result = pred.predict_for_destination(
        destination_lat=18.9220,
        destination_lon=72.8347,
        arrival_datetime=datetime(2024, 3, 15, 14, 30),  # 2:30 PM
        radius_km=2.0
    )
    
    print(f"\nArrival Time: {result['arrival_time']}")
    print(f"\nNearby Parking Options ({len(result['nearby_parking'])}):")
    for p in result['nearby_parking']:
        print(f"  • {p['name']} ({p['distance_km']}km) - {p['availability']} ({p['confidence']:.2%})")
    
    print(f"\nRecommended: {result['recommended_parking']['name']}")
    print(f"\nOptimal Arrival Times:")
    for t in result['optimal_arrival_times']:
        print(f"  • {t['time']} - {t['availability']}")
