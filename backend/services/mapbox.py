import os
import urllib.parse
import urllib.request
import json
from typing import Tuple, Optional, Dict, Any
from fastapi import HTTPException

MAPBOX_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN", "").strip()

def geocode(location: str) -> Tuple[float, float, str]:
    try:
        if "," in location:
            parts = location.split(",")
            if len(parts) == 2:
                return float(parts[0]), float(parts[1]), f"Location ({float(parts[0]):.4f}, {float(parts[1]):.4f})"
    except:
        pass
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
