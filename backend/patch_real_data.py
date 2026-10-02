import re
import os

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update GET /api/hotels and GET /api/facilities to be location-aware
real_hotels_facilities = """
@app.get("/api/hotels")
def get_hotels(lat: float, lon: float, radius: int = 5000):
    mode = os.getenv("DATA_MODE", "real").lower()
    if mode == "demo":
        return {"requested_location": f"{lat},{lon}", "latitude": lat, "longitude": lon, "search_radius": radius, "data_source": "synthetic_demo", "results": [h.model_dump() for h in DEMO_HOTELS]}
    
    # Real query
    query = f\"\"\"[out:json][timeout:15]; node["tourism"="hotel"](around:{radius},{lat},{lon}); out body;\"\"\"
    try:
        req = urllib.request.Request("https://overpass-api.de/api/interpreter", data=query.encode("utf-8"), headers={"User-Agent": "AccessRoute"}, method="POST")
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
        
        results = []
        for el in data.get("elements", []):
            tags = el.get("tags", {})
            name = tags.get("name")
            if not name: continue
            
            w_access = tags.get("wheelchair", "UNKNOWN")
            
            results.append({
                "id": str(el.get("id")), "name": name, "address": tags.get("addr:street", "UNKNOWN"),
                "lat": el.get("lat"), "lon": el.get("lon"),
                "rating": None, "price": None, "source": "OpenStreetMap",
                "ramp": "AVAILABLE" if w_access == "yes" else "UNKNOWN",
                "elevator": "AVAILABLE" if tags.get("elevator") == "yes" else "UNKNOWN",
                "step_free_entry": "AVAILABLE" if w_access == "yes" else "UNKNOWN",
                "ground_floor": "UNKNOWN", "accessible_room": "UNKNOWN", "accessible_bathroom": "UNKNOWN", "accessible_parking": "UNKNOWN", "accessible_restroom": "UNKNOWN"
            })
        return {"requested_location": f"{lat},{lon}", "latitude": lat, "longitude": lon, "search_radius": radius, "data_source": "OpenStreetMap", "results": results}
    except Exception as e:
        return {"requested_location": f"{lat},{lon}", "latitude": lat, "longitude": lon, "search_radius": radius, "data_source": "OpenStreetMap", "results": [], "error": str(e), "message": "No verified accessibility information was found for this location."}

@app.get("/api/facilities")
def get_facilities(lat: float, lon: float, radius: int = 5000):
    mode = os.getenv("DATA_MODE", "real").lower()
    if mode == "demo":
        return {"requested_location": f"{lat},{lon}", "latitude": lat, "longitude": lon, "search_radius": radius, "data_source": "synthetic_demo", "results": [f.model_dump() for f in DEMO_FACILITIES]}
        
    query = f\"\"\"[out:json][timeout:15]; (node["amenity"](around:{radius},{lat},{lon}); node["tourism"](around:{radius},{lat},{lon});); out body 50;\"\"\"
    try:
        req = urllib.request.Request("https://overpass-api.de/api/interpreter", data=query.encode("utf-8"), headers={"User-Agent": "AccessRoute"}, method="POST")
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
            
        results = []
        for el in data.get("elements", []):
            tags = el.get("tags", {})
            name = tags.get("name")
            if not name: continue
            w_access = tags.get("wheelchair", "UNKNOWN")
            
            results.append({
                "id": str(el.get("id")), "name": name, "type": tags.get("amenity", tags.get("tourism", "Facility")).title(),
                "lat": el.get("lat"), "lon": el.get("lon"), "source": "OpenStreetMap",
                "accessibility_features": ["Wheelchair Accessible"] if w_access == "yes" else (["Not Wheelchair Accessible"] if w_access == "no" else ["Accessibility Unknown"])
            })
        return {"requested_location": f"{lat},{lon}", "latitude": lat, "longitude": lon, "search_radius": radius, "data_source": "OpenStreetMap", "results": results}
    except Exception as e:
        return {"requested_location": f"{lat},{lon}", "latitude": lat, "longitude": lon, "search_radius": radius, "data_source": "OpenStreetMap", "results": [], "error": str(e), "message": "No verified accessibility information was found for this location."}
"""

content = re.sub(
    r"@app\.get\(\"/api/hotels\"\)\ndef get_hotels\(\):\n.*?@app\.get\(\"/api/facilities\"\)\ndef get_facilities\(\):\n.*?(?=@app\.post\(\"/api/travel-chat\"|class TravelChatRequest)",
    real_hotels_facilities + "\n\n",
    content,
    flags=re.DOTALL
)

# 2. Fix generate_travel_plan to strictly avoid fake data
new_travel_plan = """
@app.post("/api/travel-plan")
def generate_travel_plan(request: TripPlanRequest):
    mode = os.getenv("DATA_MODE", "real").lower()
    
    # 1. GEOCODE
    try:
        lat, lon, label = _geocode_place(request.destination)
    except Exception:
        return {"status": "error", "message": f"Could not geocode destination: {request.destination}"}

    if mode == "demo":
        return {
            "requested_location": request.destination, "latitude": lat, "longitude": lon, "search_radius": 3000, "data_source": "synthetic_demo",
            "status": "success",
            "trip_overview": {"origin": request.origin, "destination": label, "dates": f"{request.start_date} to {request.end_date}", "travelers": request.travelers, "facilities_found": 2, "recommended_hotel": DEMO_HOTELS[0].model_dump()},
            "itinerary": [], "hotels": [h.model_dump() for h in DEMO_HOTELS], "facilities": [f.model_dump() for f in DEMO_FACILITIES]
        }

    # 2. QUERY REAL LOCATION-SPECIFIC DATA
    query = f\"\"\"[out:json][timeout:15];
(
  node["tourism"="hotel"](around:3000,{lat},{lon});
  node["amenity"="restaurant"](around:2000,{lat},{lon});
  node["tourism"="museum"](around:3000,{lat},{lon});
  node["tourism"="attraction"](around:3000,{lat},{lon});
);
out body 40;\"\"\"
    
    real_hotels = []
    real_facilities = []
    
    try:
        req = urllib.request.Request("https://overpass-api.de/api/interpreter", data=query.encode("utf-8"), headers={"User-Agent": "AccessRoute", "Content-Type": "application/x-www-form-urlencoded"}, method="POST")
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
            
        for el in data.get("elements", []):
            tags = el.get("tags", {})
            name = tags.get("name")
            if not name: continue
            
            w_access = tags.get("wheelchair", "UNKNOWN").upper()
            lat_el = el.get("lat")
            lon_el = el.get("lon")

            if "tourism" in tags and tags["tourism"] == "hotel":
                real_hotels.append(Hotel(
                    id=str(el.get("id")), name=name, location=label, rating=None, price=None,
                    ground_floor="UNKNOWN", ramp="AVAILABLE" if w_access=="YES" else "UNKNOWN",
                    elevator="AVAILABLE" if tags.get("elevator")=="yes" else "UNKNOWN",
                    step_free_entry="AVAILABLE" if w_access=="YES" else "UNKNOWN",
                    accessible_room="UNKNOWN", accessible_bathroom="UNKNOWN", accessible_parking="UNKNOWN", accessible_restaurant="UNKNOWN", accessible_restroom="UNKNOWN",
                    confidence="HIGH" if w_access in ["YES", "NO"] else "UNKNOWN", source="OpenStreetMap", last_verified="2026", accessibility_score=90 if w_access=="YES" else (20 if w_access=="NO" else 50),
                    lat=lat_el, lon=lon_el
                ))
            else:
                real_facilities.append(Facility(
                    id=str(el.get("id")), name=name, type=tags.get("amenity", tags.get("tourism", "Facility")).title(), location=label,
                    accessibility_features=["Wheelchair Accessible"] if w_access=="YES" else (["Not Accessible"] if w_access=="NO" else ["Accessibility Unknown"]),
                    confidence="HIGH" if w_access in ["YES", "NO"] else "UNKNOWN", source="OpenStreetMap", verification_status="UNVERIFIED", last_verified="2026",
                    accessibility_score=90 if w_access=="YES" else (20 if w_access=="NO" else 50),
                    lat=lat_el, lon=lon_el
                ))
    except Exception as e:
        print(f"Overpass error: {e}")

    # No fake generation. If empty, it's empty.
    if not real_hotels and not real_facilities:
        return {
            "requested_location": request.destination, "latitude": lat, "longitude": lon, "search_radius": 3000, "data_source": "OpenStreetMap",
            "status": "success",
            "message": "No verified accessibility information was found for this location.",
            "trip_overview": {"origin": request.origin, "destination": label, "dates": f"{request.start_date} to {request.end_date}", "travelers": request.travelers, "facilities_found": 0, "recommended_hotel": None},
            "itinerary": [], "hotels": [], "facilities": []
        }

    real_hotels.sort(key=lambda h: h.accessibility_score, reverse=True)
    recommended_hotel = real_hotels[0].model_dump() if real_hotels else None

    # Construct strict itinerary based ONLY on available places
    day1_steps = [f"Arrival at {label}"]
    if real_hotels: day1_steps.append(f"Check-in at {real_hotels[0].name} (Score: {real_hotels[0].accessibility_score})")
    rests = [f for f in real_facilities if f.type == "Restaurant"]
    if rests: day1_steps.append(f"Dinner at {rests[0].name}")

    day2_steps = []
    attrs = [f for f in real_facilities if f.type in ["Attraction", "Museum"]]
    if attrs: day2_steps.append(f"Visit {attrs[0].name}")
    if len(rests) > 1: day2_steps.append(f"Lunch at {rests[1].name}")

    itinerary = []
    if day1_steps: itinerary.append({"day": "DAY 1", "steps": day1_steps})
    if day2_steps: itinerary.append({"day": "DAY 2", "steps": day2_steps})

    return {
        "requested_location": request.destination, "latitude": lat, "longitude": lon, "search_radius": 3000, "data_source": "OpenStreetMap",
        "status": "success",
        "trip_overview": {
            "origin": request.origin, "destination": label, "dates": f"{request.start_date} to {request.end_date}",
            "travelers": request.travelers, "facilities_found": len(real_facilities), "recommended_hotel": recommended_hotel
        },
        "itinerary": itinerary,
        "hotels": [h.model_dump() for h in real_hotels[:10]],
        "facilities": [f.model_dump() for f in real_facilities[:15]]
    }
"""

content = re.sub(
    r"@app\.post\(\"/api/travel-plan\"\)\ndef generate_travel_plan.*?return \{.*?\n    \n?\}",
    new_travel_plan,
    content,
    flags=re.DOTALL
)

# 3. Use GEMINI for the chatbot
new_chatbot = """
@app.post("/api/travel-chat")
def travel_chat(request: TravelChatRequest):
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    msg = request.message.lower()
    
    if gemini_key:
        try:
            model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key}"
            
            system = "You are an AI Travel Assistant for accessible travel. Use ONLY the provided travel context JSON. Do NOT invent hotels, restaurants, or accessibility features (like ramps or elevators) if they are missing or UNKNOWN in the context. If the context is empty, state that no verified accessibility information was found."
            payload = {
                "system_instruction": {"parts": {"text": system}},
                "contents": [{"parts": [{"text": f"Context: {json.dumps(request.travel_context)}\\n\\nQuestion: {request.message}"}]}]
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))
            answer = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"answer": answer, "provider": "gemini"}
        except Exception as e:
            print(f"Gemini error: {e}")

    return {"answer": "Offline mode: " + msg, "provider": "fallback"}
"""

content = re.sub(
    r"@app\.post\(\"/api/travel-chat\"\)\ndef travel_chat.*?return \{\"answer\": response, \"provider\": \"deterministic_fallback\"\}",
    new_chatbot,
    content,
    flags=re.DOTALL
)


with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied.")
