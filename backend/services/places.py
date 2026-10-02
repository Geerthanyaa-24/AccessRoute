import urllib.request
import json
from typing import List, Dict, Any

import os
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
