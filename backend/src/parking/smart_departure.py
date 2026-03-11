"""
Smart Departure Planning Module
Integrates traffic forecasting with parking intelligence to recommend optimal departure times
"""
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from parking.parking_predict import get_predictor


class SmartDeparturePlanner:
    """Combines traffic predictions and parking availability for optimal departure times"""
    
    def __init__(self):
        self.parking_predictor = get_predictor()
    
    def calculate_travel_time(self, origin_lat: float, origin_lon: float,
                             dest_lat: float, dest_lon: float, traffic_level: str) -> int:
        """Calculate travel time based on distance and traffic"""
        # Haversine formula
        R = 6371
        lat1, lon1 = np.radians(origin_lat), np.radians(origin_lon)
        lat2, lon2 = np.radians(dest_lat), np.radians(dest_lon)
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        distance_km = R * 2 * np.arcsin(np.sqrt(a))
        
        speed_map = {'Low': 40, 'Moderate': 25, 'High': 12, 'Critical': 8}
        avg_speed = speed_map.get(traffic_level, 25)
        travel_time_minutes = int((distance_km / avg_speed) * 60)
        return travel_time_minutes + max(5, int(travel_time_minutes * 0.1))
    
    def recommend_departure_time(self, origin_lat: float, origin_lon: float,
                                dest_lat: float, dest_lon: float,
                                arrival_time: datetime, parking_radius_km: float = 2.0,
                                traffic_predictor=None) -> Dict:
        """Recommend optimal departure time considering traffic and parking"""
        results = {
            'destination': {'lat': dest_lat, 'lon': dest_lon},
            'desired_arrival': arrival_time.isoformat(),
            'scenarios': []
        }
        
        # Test 9 departure time scenarios
        test_times = [arrival_time - timedelta(hours=2) + timedelta(minutes=15*i) for i in range(9)]
        
        for departure_time in test_times:
            # Predict traffic
            hour = departure_time.hour
            if hour in [7, 8, 9, 17, 18, 19]:
                traffic_level = 'High'
            elif hour in [10, 11, 14, 15, 16]:
                traffic_level = 'Moderate'
            else:
                traffic_level = 'Low'
            
            travel_time_min = self.calculate_travel_time(origin_lat, origin_lon, dest_lat, dest_lon, traffic_level)
            estimated_arrival = departure_time + timedelta(minutes=travel_time_min)
            
            # Check parking
            nearby_parking = self.parking_predictor.find_nearby_parking(dest_lat, dest_lon, parking_radius_km, estimated_arrival)
            available_spots = [p for p in nearby_parking if p['availability'] in ['abundant', 'available']] if nearby_parking else []
            parking_score = (len(available_spots) / len(nearby_parking) * 100) if nearby_parking else 0
            
            # Calculate scores
            time_diff_minutes = abs((estimated_arrival - arrival_time).total_seconds() / 60)
            time_score = max(0, 100 - time_diff_minutes * 2)
            traffic_scores = {'Low': 100, 'Moderate': 60, 'High': 20, 'Critical': 0}
            overall_score = time_score * 0.4 + traffic_scores[traffic_level] * 0.3 + parking_score * 0.3
            
            results['scenarios'].append({
                'departure_time': departure_time.isoformat(),
                'estimated_arrival': estimated_arrival.isoformat(),
                'travel_time_minutes': travel_time_min,
                'traffic_level': traffic_level,
                'parking_availability_score': round(parking_score, 1),
                'best_parking': available_spots[0]['name'] if available_spots else (nearby_parking[0]['name'] if nearby_parking else 'None'),
                'on_time': abs(time_diff_minutes) < 10,
                'overall_score': round(overall_score, 1),
                'recommendation': 'Excellent' if overall_score >= 80 else 'Good' if overall_score >= 60 else 'Fair' if overall_score >= 40 else 'Poor'
            })
        
        results['scenarios'].sort(key=lambda x: x['overall_score'], reverse=True)
        best = results['scenarios'][0]
        reasons = []
        if best['on_time']:
            reasons.append("arrives on time")
        if best['traffic_level'] == 'Low':
            reasons.append("minimal traffic")
        elif best['traffic_level'] != 'Critical':
            reasons.append(f"{best['traffic_level'].lower()} traffic")
        if best['parking_availability_score'] >= 70:
            reasons.append("good parking")
        results['recommended'] = {**best, 'reason': ", ".join(reasons).capitalize()}
        
        return results

_planner = None

def get_departure_planner():
    global _planner
    if _planner is None:
        _planner = SmartDeparturePlanner()
    return _planner
