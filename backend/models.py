from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RoadSegment(Base):
    __tablename__ = "road_segments"
    id = Column(Integer, primary_key=True, index=True)
    osm_id = Column(String, index=True)
    # 4326 is WGS 84 (standard lat/lon)
    geom = Column(Geometry('LINESTRING', srid=4326))
    surface = Column(String, nullable=True)
    slope = Column(Float, nullable=True) # Percentage
    width = Column(Float, nullable=True) # Meters
    accessibility_score = Column(Float, nullable=True)
    safety_score = Column(Float, nullable=True)
    
class Destination(Base):
    __tablename__ = "destinations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True)
    geom = Column(Geometry('POINT', srid=4326))
    
    # Detailed accessibility profile (e.g., {"ramp": "yes", "elevator": "working"})
    accessibility_profile = Column(JSON, nullable=True)
    overall_accessibility_score = Column(Float, nullable=True)
    data_confidence = Column(Float, nullable=True)

class ObstacleReport(Base):
    __tablename__ = "obstacle_reports"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    obstacle_type = Column(String) # e.g., "Ramp blocked", "Construction"
    description = Column(String, nullable=True)
    geom = Column(Geometry('POINT', srid=4326))
    severity = Column(String) # "High", "Medium", "Low"
    status = Column(String, default="Active") # "Active", "Under review", "Resolved"
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    destination_id = Column(Integer, ForeignKey("destinations.id"))
    scores = Column(JSON) # e.g., {"Accessibility": 4, "Surface": 3}
    text = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class UserPreference(Base):
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    accessibility_weight = Column(Float, default=40.0)
    safety_weight = Column(Float, default=25.0)
    low_slope_weight = Column(Float, default=20.0)
    surface_weight = Column(Float, default=10.0)
    distance_weight = Column(Float, default=5.0)
