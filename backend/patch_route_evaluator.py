import re

filepath = 'backend/main.py'
with open(filepath, 'r') as f:
    content = f.read()

imports = """
from backend.services.route_evaluator import evaluate_route
"""
if "from backend.services.route_evaluator import evaluate_route" not in content:
    content = re.sub(r'(from fastapi import.*)', r'\1' + imports, content, count=1)

# Replace in _live_mapbox_routes
mapbox_old = """        confidence = max(0.45, 0.85 - nearby_report_count * 0.08)
        features = {
            "surface": "unknown", "incline": 0.0, "obstacle_count": nearby_report_count,
            "has_ramp": None, "tactile_paving": None,
        }
        accessibility = calculate_accessibility_score(features)
        safety = calculate_safety_score(features)"""

mapbox_new = """        confidence = max(0.45, 0.85 - nearby_report_count * 0.08)
        
        # USE NEW ROUTE EVALUATOR
        route_assessment = evaluate_route(leaflet_coords, nearby_report_count)
        features = route_assessment["aggregated_features"]
        accessibility = route_assessment["accessibility"]
        safety = route_assessment["safety"]"""

content = content.replace(mapbox_old, mapbox_new)

# Replace in _live_osm_routes
osm_old = """        confidence = max(0.35, 0.65 - len(report_hits) * 0.08)
        features = {"surface": "unknown", "incline": 0.0, "obstacle_count": len(report_hits), "has_ramp": None, "tactile_paving": None}
        accessibility = calculate_accessibility_score(features)
        safety = calculate_safety_score(features)"""

osm_new = """        confidence = max(0.35, 0.65 - len(report_hits) * 0.08)
        
        # USE NEW ROUTE EVALUATOR
        route_assessment = evaluate_route(coordinates, len(report_hits))
        features = route_assessment["aggregated_features"]
        accessibility = route_assessment["accessibility"]
        safety = route_assessment["safety"]"""
        
content = content.replace(osm_old, osm_new)

with open(filepath, 'w') as f:
    f.write(content)
print("Patch applied.")
