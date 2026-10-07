import os
import re

# 1. Create directories
os.makedirs("models", exist_ok=True)
os.makedirs("schemas", exist_ok=True)
os.makedirs("services", exist_ok=True)
os.makedirs("api", exist_ok=True)

# 2. Write models/travel.py
with open("models/travel.py", "w", encoding="utf-8") as f:
    f.write("""from enum import Enum
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
    preferences: AccessibilityPreferences = AccessibilityPreferences()

class TravelChatRequest(BaseModel):
    trip_id: str
    message: str
""")

# 3. Write services/mapbox.py
with open("services/mapbox.py", "w", encoding="utf-8") as f:
    f.write("""import os
import urllib.parse
import urllib.request
import json
from typing import Tuple, Optional, Dict, Any
from fastapi import HTTPException

MAPBOX_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN", "").strip()

def geocode(location: str) -> Tuple[float, float, str]:
    if not MAPBOX_TOKEN:
        raise HTTPException(status_code=500, detail="MAPBOX_ACCESS_TOKEN not configured")
    
    url = f"https://api.mapbox.com/search/geocode/v6/forward?q={urllib.parse.quote(location)}&limit=1&access_token={MAPBOX_TOKEN}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            if not data.get("features"):
                raise HTTPException(status_code=400, detail=f"Location not found: {location}")
            feat = data["features"][0]
            coords = feat["geometry"]["coordinates"] # [lon, lat]
            name = feat["properties"].get("full_address") or feat["properties"].get("place_formatted") or feat["properties"].get("name") or location
            return coords[1], coords[0], name
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geocoding failed: {str(e)}")

def get_routes(origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float) -> list[Dict[str, Any]]:
    if not MAPBOX_TOKEN:
        return []
    
    # Using driving profile as baseline, Mapbox provides multiple alternatives
    url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{origin_lon},{origin_lat};{dest_lon},{dest_lat}?alternatives=true&geometries=geojson&steps=true&access_token={MAPBOX_TOKEN}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get("routes", [])
    except Exception as e:
        return []
""")

# 4. Write services/places.py
with open("services/places.py", "w", encoding="utf-8") as f:
    f.write("""import urllib.request
import json
from typing import List, Dict, Any

def search_places(lat: float, lon: float, radius: int, node_types: List[str]) -> List[Dict[str, Any]]:
    # Use Overpass API to get real POIs around the destination
    type_filters = "".join([f'node["{t.split("=")[0]}"="{t.split("=")[1]}"](around:{radius},{lat},{lon});' for t in node_types])
    
    query = f"[out:json][timeout:15];({type_filters});out body 20;"
    url = "https://overpass-api.de/api/interpreter"
    
    try:
        req = urllib.request.Request(url, data=query.encode('utf-8'), headers={'User-Agent': 'AccessRouteApp'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
            places = []
            for el in data.get('elements', []):
                tags = el.get('tags', {})
                name = tags.get('name')
                if not name:
                    continue
                
                place = {
                    "id": str(el['id']),
                    "name": name,
                    "lat": el['lat'],
                    "lon": el['lon'],
                    "source": "OpenStreetMap",
                    "tags": tags
                }
                places.append(place)
            return places
    except Exception:
        return []

def search_hotels(lat: float, lon: float, radius: int = 3000):
    return search_places(lat, lon, radius, ["tourism=hotel"])

def search_restaurants(lat: float, lon: float, radius: int = 2000):
    return search_places(lat, lon, radius, ["amenity=restaurant"])

def search_attractions(lat: float, lon: float, radius: int = 4000):
    return search_places(lat, lon, radius, ["tourism=attraction", "tourism=museum", "historic=monument"])
""")

# 5. Write services/accessibility.py
with open("services/accessibility.py", "w", encoding="utf-8") as f:
    f.write("""from typing import Dict, Any

def map_osm_accessibility(tags: dict) -> list:
    # Maps OSM tags to our strict structure: {label, status, source, confidence}
    acc = []
    
    # Wheelchair
    wc = tags.get("wheelchair")
    if wc == "yes":
        acc.append({"label": "Wheelchair Accessible", "status": "Available", "source": "OpenStreetMap", "confidence": "HIGH"})
    elif wc == "no":
        acc.append({"label": "Wheelchair Accessible", "status": "No", "source": "OpenStreetMap", "confidence": "HIGH"})
    elif wc == "limited":
        acc.append({"label": "Wheelchair Accessible", "status": "Limited", "source": "OpenStreetMap", "confidence": "MEDIUM"})
    else:
        acc.append({"label": "Wheelchair Accessible", "status": "Unknown", "source": "OpenStreetMap", "confidence": "UNKNOWN"})

    # Elevator / Lift
    elevator = tags.get("elevator")
    if elevator:
        st = "Available" if elevator == "yes" else "No"
        acc.append({"label": "Elevator", "status": st, "source": "OpenStreetMap", "confidence": "HIGH"})
    else:
        acc.append({"label": "Elevator", "status": "Unknown", "source": "OpenStreetMap", "confidence": "UNKNOWN"})

    # Blind / Tactile
    tactile = tags.get("tactile_paving")
    if tactile:
        st = "Available" if tactile == "yes" else "No"
        acc.append({"label": "Tactile Paving", "status": st, "source": "OpenStreetMap", "confidence": "HIGH"})

    return acc

def calculate_score(acc_features: list, profile: str) -> dict:
    score = 50 # Base
    known_features = 0
    available_features = 0
    
    for f in acc_features:
        if f["status"] != "Unknown":
            known_features += 1
            if f["status"] == "Available":
                available_features += 1
                
    if known_features > 0:
        score = 40 + int((available_features / known_features) * 60)
    else:
        score = 30 # Penalty for completely unknown

    return {
        "score": score,
        "rating": "Highly Accessible" if score > 80 else "Moderately Accessible" if score > 50 else "Accessibility Unknown",
        "confidence": 90 if known_features > 2 else 50
    }
""")

# 6. Write services/gemini.py
with open("services/gemini.py", "w", encoding="utf-8") as f:
    f.write("""import os
import json
import urllib.request

def generate_ai_summary(trip_data: dict) -> str:
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not gemini_key:
        return "AI Summary is unavailable (Gemini API key missing)."
        
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
    
    prompt = f\"\"\"You are an AI Travel Assistant for accessible travel.
Analyze the following travel plan data. Provide a short, welcoming 2-3 paragraph summary for the user. 
DO NOT INVENT PLACES, RATINGS, OR ACCESSIBILITY DATA. Stick strictly to what is provided below.
If accessibility data is Unknown, mention that the user should verify.

Data:
{json.dumps(trip_data, default=str)[:8000]}
\"\"\"
    
    try:
        req = urllib.request.Request(url, data=json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
            return data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"AI generation failed: {str(e)}"
""")

# 7. Write api/travel.py
with open("api/travel.py", "w", encoding="utf-8") as f:
    f.write("""import math
import uuid
import time
from fastapi import APIRouter, HTTPException
from models.travel import TravelPlanRequest, TravelChatRequest
from services import mapbox, places, accessibility, gemini

router = APIRouter(prefix="/api/travel")

# In-memory trip store (for demonstration/cache purposes)
TRIP_STORE = {}

@router.post("/plan")
def create_travel_plan(request: TravelPlanRequest):
    # 1. Geocode
    o_lat, o_lon, o_label = mapbox.geocode(request.origin)
    d_lat, d_lon, d_label = mapbox.geocode(request.destination)
    
    # 2. Places
    raw_hotels = places.search_hotels(d_lat, d_lon)
    raw_rests = places.search_restaurants(d_lat, d_lon)
    raw_attrs = places.search_attractions(d_lat, d_lon)
    
    # Process Hotels
    hotels = []
    for h in raw_hotels[:5]:
        acc = accessibility.map_osm_accessibility(h['tags'])
        score_data = accessibility.calculate_score(acc, request.accessibility_profile)
        hotels.append({
            "id": h["id"],
            "name": h["name"],
            "lat": h["lat"], "lon": h["lon"],
            "rating": 4.0, # Placeholder until integrated with real ratings
            "price": "Check local pricing",
            "accessibility_score": score_data["score"],
            "confidence": score_data["confidence"],
            "accessibility": acc,
            "source": h["source"]
        })
    hotels.sort(key=lambda x: x["accessibility_score"], reverse=True)
    
    # Process Rests
    restaurants = []
    for r in raw_rests[:5]:
        acc = accessibility.map_osm_accessibility(r['tags'])
        score_data = accessibility.calculate_score(acc, request.accessibility_profile)
        restaurants.append({
            "id": r["id"],
            "name": r["name"],
            "lat": r["lat"], "lon": r["lon"],
            "accessibility_score": score_data["score"],
            "accessibility": acc
        })
        
    # Process Attrs
    attractions = []
    for a in raw_attrs[:5]:
        acc = accessibility.map_osm_accessibility(a['tags'])
        score_data = accessibility.calculate_score(acc, request.accessibility_profile)
        attractions.append({
            "id": a["id"],
            "name": a["name"],
            "lat": a["lat"], "lon": a["lon"],
            "accessibility_score": score_data["score"],
            "accessibility": acc
        })

    # 3. Route
    routes = mapbox.get_routes(o_lat, o_lon, d_lat, d_lon)
    route_dist_km = 0
    route_time_min = 0
    if routes:
        route_dist_km = round(routes[0]["distance"] / 1000, 1)
        route_time_min = int(routes[0]["duration"] / 60)
    else:
        # Fallback Haversine if Mapbox fails
        R = 6371
        dlat = math.radians(d_lat - o_lat)
        dlon = math.radians(d_lon - o_lon)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(o_lat)) * math.cos(math.radians(d_lat)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        route_dist_km = round(R * c, 1)
        route_time_min = int(route_dist_km * 1.5)

    # 4. Itinerary
    day1_steps = []
    
    day1_steps.append({
        "time": "08:00 AM",
        "title": f"Travel from {request.origin} to {d_label}",
        "type": "Transport", "icon": "Car", 
        "subtitle": f"~ {route_dist_km} km",
        "accessibility": []
    })
    
    if hotels:
        h = hotels[0]
        day1_steps.append({
            "time": "09:30 AM",
            "title": f"Check-in at {h['name']}",
            "type": "Hotel", "icon": "Building", "address": "City Center",
            "subtitle": "Accessible Accommodation",
            "rating": h["rating"], "price": h["price"],
            "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=400&q=80",
            "accessibility": h["accessibility"],
            "source": h["source"]
        })
        
    if attractions:
        a = attractions[0]
        day1_steps.append({
            "time": "11:00 AM",
            "title": f"Visit {a['name']}",
            "type": "Attraction", "icon": "Camera", "address": "Local Area",
            "accessibility": a["accessibility"],
            "source": "OpenStreetMap"
        })
        
    if restaurants:
        r = restaurants[0]
        day1_steps.append({
            "time": "01:30 PM",
            "title": f"Lunch at {r['name']}",
            "type": "Restaurant", "icon": "Utensils",
            "accessibility": r["accessibility"],
            "source": "OpenStreetMap"
        })
        
    if len(attractions) > 1:
        a2 = attractions[1]
        day1_steps.append({
            "time": "03:00 PM",
            "title": f"Explore {a2['name']}",
            "type": "Attraction", "icon": "Camera",
            "accessibility": a2["accessibility"],
            "source": "OpenStreetMap"
        })
        
    day1_steps.append({
        "time": "06:00 PM",
        "title": f"Return to {request.origin}",
        "type": "Transport", "icon": "Car",
        "accessibility": []
    })

    # 5. Build final object
    avg_score = 0
    if hotels:
        avg_score = hotels[0]["accessibility_score"]
    
    trip_id = str(uuid.uuid4())
    
    response_data = {
        "status": "success",
        "trip_id": trip_id,
        "trip_overview": {
            "origin": o_label,
            "destination": d_label,
            "distance_km": route_dist_km,
            "travel_time_min": route_time_min,
            "overall_accessibility_score": avg_score,
            "recommended_hotel": hotels[0] if hotels else None
        },
        "latitude": d_lat,
        "longitude": d_lon,
        "hotels": hotels,
        "restaurants": restaurants,
        "attractions": attractions,
        "itinerary": [
            {"day": "DAY 1", "steps": day1_steps}
        ]
    }
    
    # 6. Gemini Contextual Summary
    ai_sum = gemini.generate_ai_summary({
        "origin": o_label, "destination": d_label,
        "hotels": [{"name": h["name"], "score": h["accessibility_score"]} for h in hotels[:3]],
        "distance": route_dist_km
    })
    response_data["ai_summary"] = ai_sum
    
    TRIP_STORE[trip_id] = response_data
    return response_data

@router.get("/plan/{trip_id}")
def get_trip(trip_id: str):
    if trip_id not in TRIP_STORE:
        raise HTTPException(status_code=404, detail="Trip not found")
    return TRIP_STORE[trip_id]
""")

# 8. Inject the router into main.py
with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

# Add import if missing
if "from api.travel import router as travel_router" not in main_code:
    # insert near other imports
    main_code = re.sub(r'(from fastapi import FastAPI.*?\n)', r'\1from api.travel import router as travel_router\n', main_code, count=1)
    
# Add router include
if "app.include_router(travel_router)" not in main_code:
    # insert near app = FastAPI()
    main_code = re.sub(r'(app = FastAPI\(.*?\)\n)', r'\1app.include_router(travel_router)\n', main_code, count=1)
    
with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)

print("Modular backend created successfully!")
