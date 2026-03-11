# Parking Module - User Guide 🅿️

## What I Fixed

1. **Location Input Simplified**: Changed from latitude/longitude coordinates to location names
   - Just type "Colaba", "Gateway of India", "Andheri Station", etc.
   - Uses OpenStreetMap geocoding to find coordinates automatically

2. **Fixed API Path Issues**: Updated model loading paths to work correctly from backend directory

3. **Server Running**: API is now running at http://127.0.0.1:8000

## How to Use the Parking Demo

### Option 1: Quick Popular Destinations
Click any of the 6 popular Mumbai destination buttons:
- 🏛️ Gateway of India
- 🏙️ BKC Business District
- 🚉 CST Railway Station
- 🛍️ Phoenix Mall
- 🏨 Bandra West
- ✈️ Mumbai Airport

### Option 2: Search Any Location
1. Type a location name in the "Search by Location" box
   - Examples: "Marine Drive", "Worli", "Powai", "Juhu Beach"
2. Adjust search radius (default 3 km)
3. Click **🔍 Find Parking Near This Location**

## What You'll See

### Nearby Parking Results
- **Parking location name** and distance
- **Current availability** status (Low/Medium/High/Full)
- **Occupancy percentage**
- **Location type** (Commercial, Shopping, Transit, etc.)

### Optimal Timing
- **Best time to visit** for easy parking
- **Worst time to avoid** (congested periods)
- Helps you plan when to travel

## Technical Details

### API Endpoints Available
- `POST /parking/predict` - Predict specific parking spot
- `POST /parking/nearby` - Find parking near coordinates
- `POST /parking/optimal-time` - Get best visiting times
- `POST /parking/route-with-parking` - Route with parking suggestions
- `GET /parking/locations` - List all parking locations
- `GET /parking/health` - API health check

### Models Used
- **Random Forest Classifier** (83.71% accuracy)
  - Predicts: Low/Medium/High/Full availability
  - Features: Time, day, weather, location type
- **LSTM Neural Network** (optional)
  - Predicts: Exact occupancy percentage

### Dataset
- 343,200 records (18 months of synthetic data)
- 26 parking locations across Mumbai
- 8 location types (Commercial, Shopping, Transit, Tourist, Residential, Hospital, Educational, Airport)

## Running the Server

### Start Server
```bash
cd backend
source ../venv/bin/activate
python -m uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

### Check Server Status
```bash
curl http://127.0.0.1:8000/parking/health
```

### Access Demo
Open browser: http://127.0.0.1:8000/parking-demo

## Troubleshooting

### "Failed to fetch parking data"
- Make sure server is running (check terminal)
- Try: `pgrep -fa uvicorn` to verify process
- Restart server if needed

### "Location not found"
- Add "Mumbai" to search: "Colaba Mumbai"
- Try alternate names: "CST Station" vs "Chhatrapati Shivaji Terminus"
- Use popular landmark names

### Server won't start
- Check virtual environment: `source ../venv/bin/activate`
- Check port 8000 is free: `lsof -i :8000`
- View logs for errors

## Files Modified

1. **backend/static/parking.html** - Frontend UI with location search
2. **backend/src/parking/parking_predict.py** - Fixed model loading paths
3. **backend/parking_api.py** - API endpoints
4. **backend/api.py** - Main FastAPI app

## Next Steps

### Enhancements You Can Add
1. **Map View**: Display parking locations on Google Maps/OpenStreetMap
2. **Real-time Updates**: WebSocket for live occupancy changes
3. **Navigation**: Integrate with Google Maps for turn-by-turn directions
4. **Notifications**: Alert when parking opens up at favorite locations
5. **Booking**: Reserve parking spots in advance
6. **Payment**: In-app parking payment integration

### For Teammates
- Dataset generation: `python generate_parking_dataset.py`
- Quick model training: `python src/parking/quick_setup.py`
- Full model training: `python src/parking/parking_train.py`
- Test API: `python test_api.py`

## How It Works

1. **User enters location** → Geocoding service finds lat/lon
2. **API finds nearby parking** → Searches within radius
3. **ML predicts availability** → Random Forest classifies current status
4. **Results displayed** → Sorted by distance, shows availability
5. **Optimal times calculated** → Analyzes 24-hour patterns

---

**Built by**: Person 2 (Parking Module Implementation)  
**Branch**: `parking-module`  
**Last Updated**: March 11, 2025
