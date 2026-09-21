from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class RoadSegmentBase(BaseModel):
    osm_id: str
    surface: Optional[str] = None
    slope: Optional[float] = None
    width: Optional[float] = None
    accessibility_score: Optional[float] = None
    safety_score: Optional[float] = None

class RoadSegmentCreate(RoadSegmentBase):
    geom_wkt: str # Well-Known Text format for easy API submission

class RoadSegment(RoadSegmentBase):
    id: int
    class Config:
        from_attributes = True

class DestinationBase(BaseModel):
    name: str
    category: str
    accessibility_profile: Optional[Dict[str, Any]] = None
    overall_accessibility_score: Optional[float] = None
    data_confidence: Optional[float] = None

class DestinationCreate(DestinationBase):
    geom_wkt: str

class Destination(DestinationBase):
    id: int
    class Config:
        from_attributes = True

class ObstacleReportBase(BaseModel):
    user_id: int
    obstacle_type: str
    description: Optional[str] = None
    severity: str
    status: str = "Active"

class ObstacleReportCreate(ObstacleReportBase):
    geom_wkt: str

class ObstacleReport(ObstacleReportBase):
    id: int
    timestamp: datetime
    class Config:
        from_attributes = True

class UserPreferenceBase(BaseModel):
    accessibility_weight: float
    safety_weight: float
    low_slope_weight: float
    surface_weight: float
    distance_weight: float

class UserPreferenceCreate(UserPreferenceBase):
    user_id: int

class UserPreference(UserPreferenceBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True
