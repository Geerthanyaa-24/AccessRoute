import re

filepath = 'backend/main.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the OSM geocode block to append Chennai
old_geocode = """    query = value.strip()
    cache_key = query.casefold()
    if cache_key in _OSM_GEOCODE_CACHE:
        return _OSM_GEOCODE_CACHE[cache_key]
    results = _nominatim_request(OSM_GEOCODER_URL, {"q": query, "format": "jsonv2", "limit": 1})"""

new_geocode = """    query = value.strip()
    # Auto-append Chennai if not present, to prevent 2000km routing errors for generic terms
    if "chennai" not in query.casefold() and "india" not in query.casefold():
        query_for_search = query + ", Chennai"
    else:
        query_for_search = query
        
    cache_key = query.casefold()
    if cache_key in _OSM_GEOCODE_CACHE:
        return _OSM_GEOCODE_CACHE[cache_key]
    results = _nominatim_request(OSM_GEOCODER_URL, {"q": query_for_search, "format": "jsonv2", "limit": 1})"""

content = content.replace(old_geocode, new_geocode)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Geocoding restricted to Chennai.")
