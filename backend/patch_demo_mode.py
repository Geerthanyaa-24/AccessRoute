import os
import re

# 1. Update mapbox.py
with open("services/mapbox.py", "r") as f:
    mapbox_code = f.read()

mapbox_code = mapbox_code.replace("""def geocode(location: str) -> Tuple[float, float, str]:
    if not MAPBOX_TOKEN:
        raise HTTPException(status_code=500, detail="MAPBOX_ACCESS_TOKEN not configured")""", """def geocode(location: str) -> Tuple[float, float, str]:
    data_mode = os.getenv("DATA_MODE", "demo").strip().lower()
    if not MAPBOX_TOKEN or data_mode == "demo":
        # Return demo coordinates
        if "chennai" in location.lower(): return 13.0827, 80.2707, "Chennai, Tamil Nadu"
        if "maha" in location.lower(): return 12.6208, 80.1945, "Mahabalipuram, Tamil Nadu"
        if "bengaluru" in location.lower(): return 12.9716, 77.5946, "Bengaluru, Karnataka"
        if "mysuru" in location.lower(): return 12.2958, 76.6394, "Mysuru, Karnataka"
        if "mumbai" in location.lower(): return 19.0760, 72.8777, "Mumbai, Maharashtra"
        if "pune" in location.lower(): return 18.5204, 73.8567, "Pune, Maharashtra"
        return 40.7128, -74.0060, f"{location} (Demo)"

    if not MAPBOX_TOKEN:
        raise HTTPException(status_code=500, detail="MAPBOX_ACCESS_TOKEN not configured")""")
with open("services/mapbox.py", "w") as f:
    f.write(mapbox_code)

# 2. Update places.py
with open("services/places.py", "r") as f:
    places_code = f.read()

places_code = places_code.replace("""def search_places(lat: float, lon: float, radius: int, node_types: List[str]) -> List[Dict[str, Any]]:""", """import os
def search_places(lat: float, lon: float, radius: int, node_types: List[str]) -> List[Dict[str, Any]]:
    data_mode = os.getenv("DATA_MODE", "demo").strip().lower()
    if data_mode == "demo":
        # Generate stable demo places based on coordinates so they change per location
        seed = int(lat + lon)
        loc_name = "City"
        if lat == 12.6208: loc_name = "Mahabalipuram"
        elif lat == 12.2958: loc_name = "Mysuru"
        elif lat == 18.5204: loc_name = "Pune"
        
        places = []
        if "tourism=hotel" in node_types[0]:
            places.append({"id": f"h{seed}", "name": f"{loc_name} Grand Accessible Resort", "lat": lat + 0.01, "lon": lon + 0.01, "source": "Demo Data", "tags": {"wheelchair": "yes", "elevator": "yes", "tactile_paving": "yes"}})
            places.append({"id": f"h{seed+1}", "name": f"{loc_name} Budget Stay", "lat": lat - 0.01, "lon": lon - 0.01, "source": "Demo Data", "tags": {"wheelchair": "limited", "elevator": "no"}})
        elif "amenity=restaurant" in node_types[0]:
            places.append({"id": f"r{seed}", "name": f"{loc_name} Authentic Dining", "lat": lat + 0.005, "lon": lon + 0.005, "source": "Demo Data", "tags": {"wheelchair": "yes"}})
        else:
            places.append({"id": f"a{seed}", "name": f"{loc_name} Cultural Museum", "lat": lat + 0.015, "lon": lon + 0.015, "source": "Demo Data", "tags": {"wheelchair": "yes", "elevator": "yes"}})
            places.append({"id": f"a{seed+1}", "name": f"{loc_name} Heritage Monument", "lat": lat - 0.015, "lon": lon - 0.015, "source": "Demo Data", "tags": {"wheelchair": "no"}})
        return places
""")
with open("services/places.py", "w") as f:
    f.write(places_code)

# 3. Update gemini.py
with open("services/gemini.py", "r") as f:
    gemini_code = f.read()

gemini_code = gemini_code.replace("""    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not gemini_key:
        return "AI Summary is unavailable (Gemini API key missing).\"""", """    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    data_mode = os.getenv("DATA_MODE", "demo").strip().lower()
    if not gemini_key or data_mode == "demo":
        origin = trip_data.get("origin", "Origin")
        dest = trip_data.get("destination", "Destination")
        return f"**(DEMO AI SUMMARY)** Your trip from {origin} to {dest} looks fantastic! We have selected highly accessible venues based on your preferences. Make sure to verify specific facilities before arrival." """)
with open("services/gemini.py", "w") as f:
    f.write(gemini_code)

# 4. Update api/travel.py response to include data_mode
with open("api/travel.py", "r") as f:
    travel_code = f.read()

travel_code = travel_code.replace("""    response_data = {
        "status": "success",""", """    data_mode = os.getenv("DATA_MODE", "demo" if not mapbox.MAPBOX_TOKEN else "real").strip().lower()
    
    response_data = {
        "status": "success",
        "data_mode": data_mode,
        "data_sources": ["Mapbox", "OpenStreetMap"] if data_mode == "real" else ["Synthetic Demo Data"],""")
with open("api/travel.py", "w") as f:
    f.write(travel_code)

print("Demo mode fallback implemented.")
