from enum import Enum
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class AccessibilityProfile(str, Enum):
    wheelchair = "wheelchair"
    limited_mobility = "limited_mobility"
    visual = "visual"
    hearing = "hearing"
    general = "general"

class AccessibilityPreferences(BaseModel):
    avoid_stairs: bool = False
    prefer_ramps: bool = False
    prefer_elevators: bool = False
    prefer_step_free: bool = False
    accessible_restroom_required: bool = False
    accessible_parking_required: bool = False
    ground_floor_preferred: bool = False
    accessible_room_required: bool = False
    avoid_steep_slopes: bool = False
    avoid_obstacles: bool = False
    prefer_high_confidence: bool = False

class TravelPlanRequest(BaseModel):
    origin: str
    destination: str
    start_date: str
    end_date: Optional[str] = None
    travelers: int = 1
    accessibility_profile: AccessibilityProfile = AccessibilityProfile.general
    preferences: Dict[str, Any] = {}

class TravelChatRequest(BaseModel):
    trip_id: str
    message: str
