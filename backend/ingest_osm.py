import osmnx as ox
import geopandas as gpd
import networkx as nx
import pandas as pd
import random
import os

# Configure OSMnx
ox.settings.log_console = True
ox.settings.use_cache = True

def download_and_process_osm_data(place_name="T Nagar, Chennai, India"):
    print(f"Downloading OpenStreetMap network for {place_name}...")
    
    # Download the walkable street network (which applies to wheelchairs)
    G = ox.graph_from_place(place_name, network_type='walk', simplify=True)
    
    print(f"Downloaded Graph with {len(G.nodes)} nodes and {len(G.edges)} edges.")
    
    # Convert Graph to GeoDataFrames
    nodes, edges = ox.graph_to_gdfs(G)
    
    print("Performing Data Cleaning and Feature Extraction...")
    
    # 1. Clean missing attributes
    if 'surface' not in edges.columns:
        edges['surface'] = 'unknown'
    if 'incline' not in edges.columns:
        edges['incline'] = '0'
        
    # 2. Simulate missing accessibility data 
    # Real OSM data often lacks detailed wheelchair tags. We simulate them 
    # based on the road type (highway tag) to prove the Data Science pipeline works.
    
    surfaces = ['asphalt', 'paving_stones', 'cobblestone', 'dirt', 'concrete']
    
    def simulate_features(row):
        # Default fallback values
        surface = row.get('surface', 'unknown')
        if pd.isna(surface) or surface == 'unknown':
            # Assign probabilities based on road type
            hw = str(row.get('highway', ''))
            if 'pedestrian' in hw or 'footway' in hw:
                surface = random.choices(['paving_stones', 'concrete', 'asphalt'], weights=[0.4, 0.4, 0.2])[0]
            else:
                surface = random.choices(surfaces, weights=[0.6, 0.2, 0.05, 0.05, 0.1])[0]
        
        # Simulate Incline (0 to 15%)
        incline = abs(random.gauss(2, 3))
        
        # Simulate Obstacles
        obstacle_count = random.choices([0, 1, 2, 3], weights=[0.7, 0.2, 0.08, 0.02])[0]
        
        return pd.Series([surface, round(incline, 2), obstacle_count])
        
    edges[['processed_surface', 'simulated_incline', 'obstacle_count']] = edges.apply(simulate_features, axis=1)
    
    print("Saving processed data locally (Pending PostGIS connection)...")
    
    # Save to GeoJSON for local caching
    cache_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(cache_dir, exist_ok=True)
    
    nodes.to_file(os.path.join(cache_dir, 'nodes.geojson'), driver='GeoJSON')
    
    # Drop complex list columns before saving edges to GeoJSON
    for col in edges.columns:
        if edges[col].apply(lambda x: isinstance(x, list)).any():
            edges[col] = edges[col].apply(lambda x: str(x))
            
    edges.to_file(os.path.join(cache_dir, 'edges.geojson'), driver='GeoJSON')
    
    print(f"Phase 2 Data Ingestion Complete! Saved to {cache_dir}")
    return G, nodes, edges

if __name__ == "__main__":
    download_and_process_osm_data()
