import csv
import random
import uuid

def generate_routing_dataset(filename="accessibility_routing_data.csv", num_nodes=1000):
    print(f"Generating routing dataset: {filename}...")
    headers = [
        "node_id", "lat", "lon", "surface_type", "incline_percentage", 
        "has_ramp", "kerb_height_cm", "tactile_paving", "accessibility_score"
    ]
    
    surfaces = ["asphalt", "concrete", "paving_stones", "cobblestone", "dirt", "gravel"]
    
    # Coordinates roughly around a city center
    base_lat, base_lon = 40.7500, -73.9900
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        
        for _ in range(num_nodes):
            surface = random.choices(surfaces, weights=[40, 30, 15, 5, 5, 5])[0]
            incline = round(random.uniform(0.0, 15.0), 1)  # 0 to 15%
            has_ramp = random.choice([True, False, True, True]) # Skewed towards True
            kerb_height = round(random.uniform(0.0, 15.0), 1) if not has_ramp else 0.0
            tactile = random.choice([True, False])
            
            # Calculate a mock accessibility score (0-100)
            score = 100
            if surface in ["cobblestone", "dirt", "gravel"]: score -= 30
            if incline > 8.0: score -= 40
            elif incline > 5.0: score -= 20
            if kerb_height > 2.0: score -= 50
            if tactile: score += 10
            
            score = max(0, min(100, score))
            
            writer.writerow({
                "node_id": str(uuid.uuid4())[:8],
                "lat": round(base_lat + random.uniform(-0.02, 0.02), 6),
                "lon": round(base_lon + random.uniform(-0.02, 0.02), 6),
                "surface_type": surface,
                "incline_percentage": incline,
                "has_ramp": has_ramp,
                "kerb_height_cm": kerb_height,
                "tactile_paving": tactile,
                "accessibility_score": score
            })
    print(f"Done! {num_nodes} nodes generated in {filename}.")

def generate_ml_vision_dataset(filename="sidewalk_ml_dataset.csv", num_images=5000):
    print(f"Generating ML vision dataset: {filename}...")
    headers = [
        "image_filename", "label_has_ramp", "label_missing_ramp", 
        "label_obstacle", "label_surface_damage", "quality_class"
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        
        for i in range(1, num_images + 1):
            has_ramp = random.choice([0, 1])
            missing_ramp = 1 if (has_ramp == 0 and random.random() > 0.7) else 0
            obstacle = 1 if random.random() > 0.8 else 0
            surface_damage = 1 if random.random() > 0.85 else 0
            
            # Determine quality class for multi-class classification
            if missing_ramp or obstacle or surface_damage:
                quality_class = "Poor"
            elif has_ramp and not obstacle and not surface_damage:
                quality_class = "Excellent"
            else:
                quality_class = "Average"
                
            writer.writerow({
                "image_filename": f"sidewalk_img_{i:05d}.jpg",
                "label_has_ramp": has_ramp,
                "label_missing_ramp": missing_ramp,
                "label_obstacle": obstacle,
                "label_surface_damage": surface_damage,
                "quality_class": quality_class
            })
    print(f"Done! {num_images} image labels generated in {filename}.")

if __name__ == "__main__":
    generate_routing_dataset()
    generate_ml_vision_dataset()
