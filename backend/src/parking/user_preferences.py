"""
Personalized User Behavior Learning Module
Tracks user preferences and travel patterns for personalized recommendations
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import numpy as np


class UserPreferences:
    """Tracks and learns from user behavior"""
    
    def __init__(self, user_id: str, storage_path: str = "../../user_data"):
        self.user_id = user_id
        self.storage_path = storage_path
        self.preferences_file = os.path.join(storage_path, f"{user_id}_preferences.json")
        os.makedirs(storage_path, exist_ok=True)
        self.data = self.load_user_data()
    
    def load_user_data(self) -> Dict:
        if os.path.exists(self.preferences_file):
            with open(self.preferences_file, 'r') as f:
                return json.load(f)
        return {
            'user_id': self.user_id,
            'created_at': datetime.now().isoformat(),
            'trip_history': [],
            'favorite_destinations': {},
            'favorite_parking': {},
            'parking_preferences': {
                'max_walking_distance_km': 0.5,
                'max_hourly_rate': 100,
                'covered_preferred': False
            },
            'statistics': {'total_trips': 0, 'total_parking_searches': 0}
        }
    
    def save_user_data(self):
        with open(self.preferences_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_trip(self, origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float,
                   dest_name: str, departure_time: datetime, arrival_time: datetime,
                   parking_id: Optional[str] = None, parking_name: Optional[str] = None,
                   route_rating: Optional[int] = None):
        """Record completed trip"""
        trip = {
            'trip_id': len(self.data['trip_history']) + 1,
            'timestamp': datetime.now().isoformat(),
            'origin': {'lat': origin_lat, 'lon': origin_lon},
            'destination': {'lat': dest_lat, 'lon': dest_lon, 'name': dest_name},
            'departure_time': departure_time.isoformat(),
            'arrival_time': arrival_time.isoformat(),
            'travel_time_minutes': int((arrival_time - departure_time).total_seconds() / 60),
            'parking_id': parking_id,
            'parking_name': parking_name,
            'rating': route_rating
        }
        
        self.data['trip_history'].append(trip)
        self.data['statistics']['total_trips'] += 1
        
        # Update favorites
        if dest_name not in self.data['favorite_destinations']:
            self.data['favorite_destinations'][dest_name] = {
                'location': {'lat': dest_lat, 'lon': dest_lon},
                'visit_count': 0,
                'last_visited': None
            }
        self.data['favorite_destinations'][dest_name]['visit_count'] += 1
        self.data['favorite_destinations'][dest_name]['last_visited'] = datetime.now().isoformat()
        
        if parking_id:
            if parking_id not in self.data['favorite_parking']:
                self.data['favorite_parking'][parking_id] = {
                    'name': parking_name,
                    'use_count': 0,
                    'average_rating': 0,
                    'ratings': []
                }
            self.data['favorite_parking'][parking_id]['use_count'] += 1
            if route_rating:
                self.data['favorite_parking'][parking_id]['ratings'].append(route_rating)
                self.data['favorite_parking'][parking_id]['average_rating'] = np.mean(self.data['favorite_parking'][parking_id]['ratings'])
        
        self.save_user_data()
    
    def get_favorite_destinations(self, limit: int = 10) -> List[Dict]:
        favorites = [{'name': name, 'location': data['location'], 'visits': data['visit_count'], 
                     'last_visited': data['last_visited']} 
                    for name, data in self.data['favorite_destinations'].items()]
        favorites.sort(key=lambda x: x['visits'], reverse=True)
        return favorites[:limit]
    
    def get_favorite_parking(self, limit: int = 10) -> List[Dict]:
        favorites = [{'parking_id': pid, 'name': data['name'], 'uses': data['use_count'],
                     'average_rating': round(data['average_rating'], 1) if data['average_rating'] else None}
                    for pid, data in self.data['favorite_parking'].items()]
        favorites.sort(key=lambda x: x['uses'], reverse=True)
        return favorites[:limit]
    
    def get_personalized_parking_suggestions(self, parking_options: List[Dict]) -> List[Dict]:
        """Rank parking based on user preferences"""
        favorite_parking_ids = set(self.data['favorite_parking'].keys())
        max_walk_km = self.data['parking_preferences']['max_walking_distance_km']
        max_rate = self.data['parking_preferences']['max_hourly_rate']
        
        for parking in parking_options:
            score = 50
            reasons = []
            
            if parking.get('parking_id') in favorite_parking_ids:
                score += 30
                reasons.append("You've used this before")
                avg_rating = self.data['favorite_parking'][parking['parking_id']].get('average_rating', 0)
                if avg_rating >= 4:
                    score += 10
                    reasons.append(f"You rated it {avg_rating:.1f}/5")
            
            # Use distance_km (the actual field name from find_nearby_parking)
            distance = parking.get('distance_km', parking.get('distance', 999))
            if distance <= max_walk_km:
                score += 15
                reasons.append("Within preferred walking distance")
            
            if parking.get('hourly_rate', 0) <= max_rate:
                score += 10
            
            if parking['availability'] == 'abundant':
                score += 20
            elif parking['availability'] == 'available':
                score += 10
            
            if not reasons:
                reasons.append("Recommended based on availability")
            
            parking['personalization_score'] = min(100, max(0, score))
            parking['personalization_reasons'] = reasons
        
        parking_options.sort(key=lambda x: x['personalization_score'], reverse=True)
        return parking_options
    
    def get_user_statistics(self) -> Dict:
        return {
            'total_trips': self.data['statistics']['total_trips'],
            'total_parking_searches': self.data['statistics']['total_parking_searches'],
            'favorite_destinations': self.get_favorite_destinations(5),
            'favorite_parking': self.get_favorite_parking(5),
            'member_since': self.data['created_at'],
            'preferences': self.data['parking_preferences']
        }

_users = {}

def get_user_preferences(user_id: str) -> UserPreferences:
    if user_id not in _users:
        _users[user_id] = UserPreferences(user_id)
    return _users[user_id]
