import math
import os
import uuid
import time
from fastapi import APIRouter, HTTPException
from api_models.travel import TravelPlanRequest, TravelChatRequest
from services import mapbox, places, accessibility, gemini

router = APIRouter(prefix="/api/travel")

# In-memory trip store (for demonstration/cache purposes)
TRIP_STORE = {}

@router.post("/plan")
@router.post("/ai-travel-plan")
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
    
    data_mode = os.getenv("DATA_MODE", "demo" if not mapbox.MAPBOX_TOKEN else "real").strip().lower()
    
    response_data = {
        "status": "success",
        "data_mode": data_mode,
        "data_sources": ["Mapbox", "OpenStreetMap"] if data_mode == "real" else ["Synthetic Demo Data"],
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
