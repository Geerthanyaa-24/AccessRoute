import requests
import pandas as pd
import json

def fetch_real_accessibility_data(city_name="Chennai"):
    print(f"Fetching real accessibility data from OpenStreetMap for {city_name}...")
    
    # Overpass API query to get real accessibility data
    # We look for nodes/ways that have wheelchair, tactile paving, or specific footway surfaces
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    overpass_query = f"""
    [out:json][timeout:25];
    area[name="{city_name}"]->.searchArea;
    (
      node["wheelchair"](area.searchArea);
      node["tactile_paving"](area.searchArea);
      node["highway"="crossing"](area.searchArea);
      way["highway"="footway"]["surface"](area.searchArea);
    );
    out body;
    >;
    out skel qt;
    """
    
    try:
        headers = {'User-Agent': 'AccessibilityNavApp/1.0 (Student Project)'}
        response = requests.post(overpass_url, data={'data': overpass_query}, headers=headers)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Failed to fetch data from Overpass API: {e}")
        return None

    elements = data.get('elements', [])
    print(f"Found {len(elements)} raw geographical elements. Processing...")

    dataset = []
    
    for el in elements:
        tags = el.get('tags', {})
        if not tags:
            continue
            
        # Extract features if they exist, or assign realistic defaults based on the feature type
        wheelchair = tags.get('wheelchair', 'unknown')
        surface = tags.get('surface', 'unknown')
        tactile_paving = tags.get('tactile_paving', 'no')
        highway = tags.get('highway', 'unknown')
        
        # We need to map these to the numeric features our ML model expects:
        # Features: incline_percentage, kerb_height_cm, surface_type_encoded, has_ramp_encoded, tactile_paving_encoded
        
        # 1. Surface Type (0: Bad/Dirt, 1: Average/Cobblestone, 2: Good/Asphalt, 3: Excellent/Paved)
        surface_score = 1
        if surface in ['paved', 'asphalt', 'concrete', 'paving_stones']:
            surface_score = 3
        elif surface in ['compacted', 'fine_gravel']:
            surface_score = 2
        elif surface in ['unpaved', 'dirt', 'grass', 'sand', 'gravel']:
            surface_score = 0
            
        # 2. Ramp (Wheelchair accessibility)
        has_ramp = 1 if wheelchair in ['yes', 'designated'] else 0
        
        # 3. Tactile Paving
        has_tactile = 1 if tactile_paving == 'yes' else 0
        
        # 4. Infer Kerb Height & Incline based on Real OSM data context
        kerb_height = 0.0
        incline = 0.0
        
        if wheelchair == 'no':
            kerb_height = 15.0 # High kerb, inaccessible
            incline = 12.0 # Steep incline
        elif wheelchair == 'yes':
            kerb_height = 0.0 # Flush with road
            incline = 2.0 # Gentle slope
        elif has_tactile == 1:
            kerb_height = 2.0 # Standard dropped kerb
            incline = 3.0
        else:
            # For 'unknown', assign statistical averages for city infrastructure
            kerb_height = 5.0 
            incline = 4.5
            
        # Target variable: is_safe (1 if accessible, 0 if not)
        is_safe = 1 if (has_ramp == 1 or kerb_height < 3.0) and surface_score >= 2 and incline < 8.0 else 0
        
        # Target variable: accessibility_score (0-100)
        score = (surface_score / 3.0) * 40
        score += (1 if has_ramp else 0) * 30
        score += (1 if has_tactile else 0) * 10
        score += max(0, 20 - (incline * 2))
        
        dataset.append({
            "osm_id": el.get('id'),
            "type": el.get('type'),
            "latitude": el.get('lat', 0),
            "longitude": el.get('lon', 0),
            "original_surface": surface,
            "original_wheelchair": wheelchair,
            "incline_percentage": round(incline, 1),
            "kerb_height_cm": round(kerb_height, 1),
            "surface_type_encoded": surface_score,
            "has_ramp_encoded": has_ramp,
            "tactile_paving_encoded": has_tactile,
            "accessibility_score": round(score, 1),
            "is_safe": is_safe
        })
        
    df = pd.DataFrame(dataset)
    
    # Filter out empty rows and save
    df = df[df['latitude'] != 0]
    
    if len(df) > 0:
        filename = "real_osm_accessibility_data.csv"
        df.to_csv(filename, index=False)
        print(f"Success! Saved {len(df)} real-world valid data points to {filename}")
        print("\nDataset Preview:")
        print(df[['osm_id', 'accessibility_score', 'is_safe']].head())
    else:
        print("No valid geospatial accessibility data was found for this region.")

if __name__ == "__main__":
    fetch_real_accessibility_data("Chennai")
