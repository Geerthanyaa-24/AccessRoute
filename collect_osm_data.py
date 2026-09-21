import requests
import json
import csv

def fetch_osm_accessibility_data():
    print("Fetching OpenStreetMap accessibility data via Overpass API...")
    
    # Overpass query to find footways, pedestrian paths, and nodes with wheelchair tags
    # We will query a bounding box (e.g., around a section of Manhattan, NY)
    # Bounding box format: (south, west, north, east)
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = """
    [out:json][timeout:25];
    (
      node["wheelchair"](40.75,-73.99,40.76,-73.98);
      way["highway"="footway"](40.75,-73.99,40.76,-73.98);
      node["kerb"](40.75,-73.99,40.76,-73.98);
      node["tactile_paving"](40.75,-73.99,40.76,-73.98);
    );
    out body;
    >;
    out skel qt;
    """
    
    response = requests.post(overpass_url, data={'data': overpass_query})
    
    if response.status_code == 200:
        data = response.json()
        
        # Save raw JSON
        with open('osm_accessibility_data.json', 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Saved raw JSON data with {len(data['elements'])} elements to osm_accessibility_data.json")
        
        # Parse into a simplified CSV for routing/analysis
        nodes = []
        for element in data['elements']:
            if element['type'] == 'node':
                tags = element.get('tags', {})
                nodes.append({
                    'id': element['id'],
                    'lat': element['lat'],
                    'lon': element['lon'],
                    'wheelchair': tags.get('wheelchair', 'unknown'),
                    'kerb': tags.get('kerb', 'unknown'),
                    'tactile_paving': tags.get('tactile_paving', 'unknown'),
                    'highway': tags.get('highway', 'unknown')
                })
        
        if nodes:
            keys = nodes[0].keys()
            with open('osm_accessibility_nodes.csv', 'w', newline='', encoding='utf-8') as f:
                dict_writer = csv.DictWriter(f, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(nodes)
            print(f"Saved parsed CSV data with {len(nodes)} nodes to osm_accessibility_nodes.csv")
        else:
            print("No relevant nodes found in the bounding box.")
            
    else:
        print(f"Error fetching data: {response.status_code}")

if __name__ == "__main__":
    fetch_osm_accessibility_data()
