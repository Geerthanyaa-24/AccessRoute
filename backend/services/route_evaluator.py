import os
import math
import pandas as pd
from typing import List, Dict, Any
from backend.scoring_engine import assess_ml_safety, calculate_accessibility_score, calculate_safety_score

# Load OSM Data for Segment Matching
_OSM_DATA = None

def get_osm_data() -> pd.DataFrame:
    global _OSM_DATA
    if _OSM_DATA is None:
        try:
            csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "real_osm_accessibility_data.csv")
            _OSM_DATA = pd.read_csv(csv_path)
            # Ensure safe/unsafe target matches the pipeline training logic
            _OSM_DATA['ramp_available'] = _OSM_DATA['original_wheelchair'].apply(lambda x: 1 if x in ['yes', 'designated'] else 0)
        except Exception as e:
            print(f"Warning: Failed to load real_osm_accessibility_data.csv for routing. Error: {e}")
            _OSM_DATA = pd.DataFrame()
    return _OSM_DATA

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000 # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def match_point_to_osm(lat: float, lon: float, threshold_m: float = 50.0) -> dict:
    df = get_osm_data()
    if df.empty:
        return {}
        
    # Quick distance approximation (avoiding full haversine on all 419 rows if possible, but 419 is tiny)
    # So we can just calculate haversine for all
    distances = df.apply(lambda row: haversine(lat, lon, row['latitude'], row['longitude']), axis=1)
    min_idx = distances.idxmin()
    min_dist = distances[min_idx]
    
    if min_dist <= threshold_m:
        row = df.iloc[min_idx]
        return {
            "incline": float(row.get("incline_percentage", 0.0)),
            "kerb_height": float(row.get("kerb_height_cm", 0.0)),
            "surface": str(row.get("original_surface", "unknown")),
            "has_ramp": bool(row.get("ramp_available", 0)),
            "tactile_paving": bool(row.get("tactile_paving_encoded", 0)),
            "distance_to_osm_m": min_dist
        }
    return {}

def evaluate_route(route_coords: List[List[float]], obstacle_count: int = 0) -> Dict[str, Any]:
    """
    Evaluates a route by splitting it into segments, matching to OSM data,
    predicting ML safety for each segment, and aggregating the result.
    """
    segments = []
    
    # Sub-sample coords (evaluate every 5th point to avoid excessive computation for long routes)
    # Real routes might have hundreds of coordinates.
    sampled_coords = route_coords[::max(1, len(route_coords) // 10)]
    
    for lat, lon in sampled_coords:
        matched = match_point_to_osm(lat, lon)
        
        features = {
            "surface": matched.get("surface", "unknown"),
            "incline": matched.get("incline", 0.0),
            "kerb_height": matched.get("kerb_height", 0.0),
            "has_ramp": matched.get("has_ramp", False),
            "tactile_paving": matched.get("tactile_paving", False),
            "obstacle_count": 0 # We will apply overall obstacles at route level
        }
        
        # 1. ML PREDICTION FOR SEGMENT
        ml_prediction = assess_ml_safety(features)
        
        segments.append({
            "lat": lat, "lon": lon,
            "features": features,
            "ml_prediction": ml_prediction,
            "matched_osm": bool(matched)
        })
        
    # Aggregate Route Features
    if not segments:
        aggregated = {"surface": "unknown", "incline": 0.0, "has_ramp": False, "tactile_paving": False}
    else:
        max_incline = max([s["features"]["incline"] for s in segments])
        # Find most common surface
        surfaces = [s["features"]["surface"] for s in segments]
        most_common_surface = max(set(surfaces), key=surfaces.count)
        
        has_ramp = any([s["features"]["has_ramp"] for s in segments])
        tactile = any([s["features"]["tactile_paving"] for s in segments])
        
        # Unsafe segment count
        unsafe_segments = sum(1 for s in segments if s["ml_prediction"]["class"] == 0)
        
        aggregated = {
            "surface": most_common_surface,
            "incline": max_incline,
            "has_ramp": has_ramp,
            "tactile_paving": tactile,
            "obstacle_count": obstacle_count,
            "unsafe_segment_count": unsafe_segments,
            "total_segments_evaluated": len(segments)
        }
        
    # Calculate overall Route Score using the scoring engine
    acc = calculate_accessibility_score(aggregated)
    saf = calculate_safety_score(aggregated)
    
    # Penalize if multiple segments are deemed unsafe by ML
    if aggregated.get("unsafe_segment_count", 0) > 0:
        penalty = 10 * aggregated["unsafe_segment_count"]
        acc["overall_score"] = max(0, acc["overall_score"] - penalty)
        saf["safety_score"] = max(0, saf["safety_score"] - penalty)
        saf["penalties"].append(f"{aggregated['unsafe_segment_count']} segment(s) predicted UNSAFE by ML.")
    
    return {
        "aggregated_features": aggregated,
        "segments": segments,
        "accessibility": acc,
        "safety": saf
    }
