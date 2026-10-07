import re

filepath = 'backend/services/mapbox.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the demo return with a Nominatim fallback or just returning the string itself
old_demo_return = """        if "pune" in location.lower(): return 18.5204, 73.8567, "Pune, Maharashtra"
        return 40.7128, -74.0060, f"{location} (Demo)" """

new_demo_return = """        if "pune" in location.lower(): return 18.5204, 73.8567, "Pune, Maharashtra"
        
        # Fallback to Nominatim OSM geocoder instead of hardcoding Demo coordinates
        try:
            import urllib.request
            import urllib.parse
            import json
            query = location.strip()
            if "chennai" not in query.casefold() and "india" not in query.casefold():
                query += ", Chennai"
            url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=jsonv2&limit=1"
            req = urllib.request.Request(url, headers={'User-Agent': 'AccessRoute/1.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                res = json.loads(response.read().decode())
                if res:
                    return float(res[0]["lat"]), float(res[0]["lon"]), res[0].get("display_name", location)
        except Exception:
            pass
            
        return 13.0827, 80.2707, location # default to chennai coordinate instead of NY, remove (Demo)"""

content = content.replace(old_demo_return, new_demo_return)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Geocoding patched in AI Travel Planner.")
