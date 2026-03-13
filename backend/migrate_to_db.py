import pandas as pd
import os
from datetime import datetime
from src.parking.database import engine, SessionLocal, Base
from src.parking.models import ParkingLocation, OccupancyLog

# Get the base directory (backend folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "parking_dataset.csv")

def migrate_data():
    print("Starting migration from CSV to SQLite...")
    
    # Enable this if you want to wipe the db on each run
    # Base.metadata.drop_all(bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

    # Check if dataset exists
    if not os.path.exists(DATASET_PATH):
        print(f"Error: Dataset not found at {DATASET_PATH}")
        return

    # Load CSV in chunks to avoid memory issues if it's huge
    chunksize = 10000
    db = SessionLocal()
    
    try:
        # First, extract unique parking locations to populate the master table
        print("Extracting and migrating parking locations...")
        df_locations = pd.read_csv(DATASET_PATH, usecols=[
            'parking_id', 'parking_name', 'latitude', 'longitude', 
            'capacity', 'location_type', 'hourly_rate'
        ]).drop_duplicates(subset=['parking_id'])
        
        for _, row in df_locations.iterrows():
            # Check if location already exists to be safe
            exists = db.query(ParkingLocation).filter(ParkingLocation.id == row['parking_id']).first()
            if not exists:
                loc = ParkingLocation(
                    id=row['parking_id'],
                    name=row['parking_name'],
                    latitude=row['latitude'],
                    longitude=row['longitude'],
                    capacity=row['capacity'],
                    location_type=row['location_type'],
                    hourly_rate=row['hourly_rate']
                )
                db.add(loc)
        db.commit()
        print(f"Migrated {len(df_locations)} parking locations.")

        # Now migrate the actual historical logs
        print("Migrating occupancy logs (this might take a moment)...")
        logs_added = 0
        for chunk in pd.read_csv(DATASET_PATH, chunksize=chunksize):
            logs = []
            for _, row in chunk.iterrows():
                # Parse timestamp
                try:
                    ts = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    # Handle alternative formats if any
                    ts = pd.to_datetime(row['timestamp']).to_pydatetime()

                log = OccupancyLog(
                    parking_id=row['parking_id'],
                    timestamp=ts,
                    occupied_spots=row['occupied_spots'],
                    available_spots=row['available_spots'],
                    occupancy_rate=row['occupancy_rate'],
                    weather=row['weather']
                )
                logs.append(log)
            
            db.bulk_save_objects(logs)
            db.commit()
            logs_added += len(logs)
            print(f"  ... migrated {logs_added} records")
            
        print(f"Successfully migrated {logs_added} occupancy logs!")
        print("Migration complete.")
        
    except Exception as e:
        db.rollback()
        print(f"Error during migration: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_data()
