import networkx as nx
import geopandas as gpd
import os

def load_graph():
    """Loads the graph from the GeoJSON files saved by OSM ingestion."""
    cache_dir = os.path.join(os.path.dirname(__file__), 'data')
    try:
        nodes = gpd.read_file(os.path.join(cache_dir, 'nodes.geojson'))
        edges = gpd.read_file(os.path.join(cache_dir, 'edges.geojson'))
    except FileNotFoundError:
        return None
        
    # Reconstruct NetworkX graph
    G = nx.MultiDiGraph()
    for idx, row in nodes.iterrows():
        G.add_node(row['osmid'], y=row.geometry.y, x=row.geometry.x)
        
    for idx, row in edges.iterrows():
        u = row['u']
        v = row['v']
        key = row.get('key', 0)
        
        # Parse attributes
        length = float(row.get('length', 1.0))
        incline = float(row.get('simulated_incline', 0.0))
        obstacles = int(row.get('obstacle_count', 0))
        
        # Calculate weights for different route types
        
        # 1. Shortest (just length)
        shortest_weight = length
        
        # 2. Safest (penalize obstacles heavily)
        safest_weight = length * (1 + (obstacles * 5))
        
        # 3. Low-Slope (penalize steep inclines)
        if incline > 8:
            slope_penalty = 10
        elif incline > 5:
            slope_penalty = 3
        else:
            slope_penalty = 1
        low_slope_weight = length * slope_penalty
        
        # 4. Balanced (User Preferences)
        # We can dynamically apply weights here
        balanced_weight = length * (1 + obstacles) * (1 + (incline/10))
        
        G.add_edge(u, v, key=key, 
                   length=length,
                   shortest_weight=shortest_weight,
                   safest_weight=safest_weight,
                   low_slope_weight=low_slope_weight,
                   balanced_weight=balanced_weight,
                   geometry=row.geometry)
                   
    return G

def calculate_route(G, start_node, end_node, route_type='balanced'):
    """Calculates the optimal route based on the selected weight metric."""
    
    weight_map = {
        'shortest': 'shortest_weight',
        'safest': 'safest_weight',
        'low_slope': 'low_slope_weight',
        'balanced': 'balanced_weight'
    }
    
    weight_key = weight_map.get(route_type, 'balanced_weight')
    
    try:
        path = nx.shortest_path(G, start_node, end_node, weight=weight_key)
        
        # Extract coordinates for frontend mapping
        coords = []
        total_distance = 0
        total_obstacles = 0
        
        for i in range(len(path)-1):
            u = path[i]
            v = path[i+1]
            edge_data = G.get_edge_data(u, v)[0]
            
            # If edge has a Linestring geometry, extract its coords
            if 'geometry' in edge_data and edge_data['geometry'] is not None:
                coords.extend(list(edge_data['geometry'].coords))
            else:
                # Fallback to straight line between nodes
                coords.append((G.nodes[u]['x'], G.nodes[u]['y']))
                
            total_distance += edge_data.get('length', 0)
            total_obstacles += edge_data.get('obstacle_count', 0)
            
        # Ensure last node is added if fallback used
        coords.append((G.nodes[end_node]['x'], G.nodes[end_node]['y']))
        
        return {
            "status": "success",
            "route_type": route_type,
            "coordinates": [[lat, lon] for lon, lat in coords], # React Leaflet uses [lat, lon]
            "metrics": {
                "distance_meters": round(total_distance, 1),
                "obstacles_encountered": total_obstacles
            }
        }
        
    except nx.NetworkXNoPath:
        return {"status": "error", "message": "No path found."}
    except nx.NodeNotFound:
        return {"status": "error", "message": "Start or destination node invalid."}
