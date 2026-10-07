import json

filepath = 'backend/main.py'
with open(filepath, 'r') as f:
    content = f.read()

# Define the start and end of the block to replace
start_marker = 'def nearby_places(lat: float, lon: float, radius_m: int = 2000, category: str = "all"):'
end_marker = 'def _haversine_m('

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

if start_idx == -1 or end_idx == -1:
    print("Could not find markers")
    exit(1)

new_logic = """def nearby_places(lat: float, lon: float, radius_m: int = 2000, category: str = "all"):
    if not -90 <= lat <= 90 or not -180 <= lon <= 180:
        raise HTTPException(status_code=400, detail="Coordinates are outside the valid range")
    if not 250 <= radius_m <= 10000:
        raise HTTPException(status_code=400, detail="Search radius must be between 250 and 10000 metres")

    amenity_values = {
        "all": ("hospital", "clinic", "restaurant", "cafe", "school", "college", "university", "toilets", "bus_station", "pharmacy", "park", "library", "social_facility", "public_building"),
        "hospitals": ("hospital", "clinic", "doctors"),
        "restaurants": ("restaurant", "cafe", "food_court"),
        "colleges": ("school", "college", "university", "library"),
        "toilets": ("toilets",),
        "transport": ("bus_station", "train_station", "taxi"),
        "pharmacies": ("pharmacy",),
        "parks": ("park",),
        "shopping": ("mall", "marketplace", "supermarket")
    }
    
    # Handle both singular and plural forms from frontend
    mapped_cat = category.lower()
    if mapped_cat == "health": mapped_cat = "hospitals"
    if mapped_cat == "education": mapped_cat = "colleges"
    if mapped_cat == "community": mapped_cat = "all"
    
    amenities = amenity_values.get(mapped_cat, amenity_values["all"])

    node_queries = "".join(f'node["amenity"="{a}"](around:{radius_m},{lat},{lon});' for a in amenities if a not in ('park', 'mall', 'supermarket'))
    node_queries += "".join(f'node["leisure"="{a}"](around:{radius_m},{lat},{lon});' for a in amenities if a == 'park')
    node_queries += "".join(f'node["shop"="{a}"](around:{radius_m},{lat},{lon});' for a in amenities if a in ('mall', 'supermarket'))
    
    query = f"[out:json][timeout:10];({node_queries});out body 60;"
    contact = os.getenv("ACCESSROUTE_CONTACT", "local development instance")
    
    elements = []
    try:
        request = urllib.request.Request(
            "https://overpass-api.de/api/interpreter",
            data=urllib.parse.urlencode({"data": query}).encode("utf-8"),
            headers={"User-Agent": f"AccessRoute/1.0 ({contact})", "Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=8) as response:
            elements = json.loads(response.read().decode("utf-8")).get("elements", [])
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Nearby OpenStreetMap data is temporarily unavailable. Try again shortly.") from exc

    places = []
    seen = set()
    
    for element in elements:
        tags = element.get("tags", {})
        point = element.get("center") or element
        if point.get("lat") is None or point.get("lon") is None:
            continue
        place_lat, place_lon = float(point["lat"]), float(point["lon"])
        
        dedupe_key = (round(place_lat, 5), round(place_lon, 5))
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        
        name = tags.get("name")
        if not name:
            name = (tags.get("amenity") or tags.get("leisure") or tags.get("shop") or "Place").replace("_", " ").title()
            
        address = ", ".join(filter(None, (
            " ".join(filter(None, (tags.get("addr:housenumber"), tags.get("addr:street")))),
            tags.get("addr:suburb"), tags.get("addr:city"),
        )))
        
        # Calculate Accessibility Score & Confidence
        wheelchair = tags.get("wheelchair", "unknown")
        ramp = tags.get("ramp", "unknown")
        elevator = tags.get("elevator", "unknown")
        tactile_paving = tags.get("tactile_paving", "unknown")
        accessible_entrance = tags.get("entrance", "unknown")
        accessible_toilet = tags.get("toilets:wheelchair", "unknown")
        
        score = 0
        known_attrs = 0
        total_attrs = 6
        
        if wheelchair != "unknown":
            known_attrs += 1
            if wheelchair in ["yes", "designated"]: score += 40
            elif wheelchair == "limited": score += 15
            
        if ramp != "unknown":
            known_attrs += 1
            if ramp == "yes": score += 15
            
        if elevator != "unknown":
            known_attrs += 1
            if elevator == "yes": score += 15
            
        if tactile_paving != "unknown":
            known_attrs += 1
            if tactile_paving == "yes": score += 10
            
        if accessible_entrance != "unknown":
            known_attrs += 1
            if accessible_entrance in ["yes", "main", "wheelchair"]: score += 10
            
        if accessible_toilet != "unknown":
            known_attrs += 1
            if accessible_toilet == "yes": score += 10
            
        # Base confidence 10%, plus 15% for every known attribute
        confidence = 10 + (known_attrs * 15)
        if known_attrs == 0:
            score = 30 # Default unknown baseline
        elif score == 0 and known_attrs > 0:
            score = 10 # Explicitly inaccessible
        elif known_attrs < total_attrs:
            # Scale score based on knowns if not 0, so 40/40 becomes 100/100 essentially
            score = int(min(100, score * (total_attrs / (known_attrs + 0.1))))
            
        if score >= 80: status = "Highly Accessible"
        elif score >= 60: status = "Moderately Accessible"
        elif score >= 40: status = "Limited Accessibility"
        else: status = "Low Accessibility"
        
        if known_attrs == 0:
            status = "Insufficient Data"

        places.append({
            "id": f"{element.get('type')}/{element.get('id')}",
            "name": name,
            "category": (tags.get("amenity") or tags.get("leisure") or tags.get("shop") or "Place").title().replace("_", " "),
            "location": {"latitude": place_lat, "longitude": place_lon},
            "distance_meters": round(_haversine_m(lat, lon, place_lat, place_lon)),
            "address": address,
            "accessibility": {
                "score": score,
                "confidence": min(100, confidence),
                "status": status,
                "wheelchair": wheelchair,
                "ramp": ramp,
                "elevator": elevator,
                "accessible_entrance": accessible_entrance,
                "accessible_toilet": accessible_toilet,
                "tactile_paving": tactile_paving,
                "known_attributes_count": known_attrs
            }
        })

    # Default sort by distance (Frontend can resort)
    places.sort(key=lambda place: place["distance_meters"])

    return {
        "user_location": {"latitude": lat, "longitude": lon},
        "radius_m": radius_m,
        "places": places[:60],
        "category_requested": category
    }


"""

content = content[:start_idx] + new_logic + content[end_idx:]

with open(filepath, 'w') as f:
    f.write(content)
print("Patch applied.")
