from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class ParkingLocation(Base):
    __tablename__ = "parking_locations"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    capacity = Column(Integer)
    location_type = Column(String)
    hourly_rate = Column(Float)

    # Relationship to occupancy logs
    occupancy_logs = relationship("OccupancyLog", back_populates="parking_location")

class OccupancyLog(Base):
    __tablename__ = "occupancy_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    parking_id = Column(String, ForeignKey("parking_locations.id"), index=True)
    timestamp = Column(DateTime, index=True)
    occupied_spots = Column(Integer)
    available_spots = Column(Integer)
    occupancy_rate = Column(Float)
    weather = Column(String)

    # Relationship back to the parking location
    parking_location = relationship("ParkingLocation", back_populates="occupancy_logs")
