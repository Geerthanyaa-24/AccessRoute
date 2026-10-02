from typing import Dict, Any

def map_osm_accessibility(tags: dict) -> list:
    # Maps OSM tags to our strict structure: {label, status, source, confidence}
    acc = []
    
    # Wheelchair
    wc = tags.get("wheelchair")
    if wc == "yes":
        acc.append({"label": "Wheelchair Accessible", "status": "Available", "source": "OpenStreetMap", "confidence": "HIGH"})
    elif wc == "no":
        acc.append({"label": "Wheelchair Accessible", "status": "No", "source": "OpenStreetMap", "confidence": "HIGH"})
    elif wc == "limited":
        acc.append({"label": "Wheelchair Accessible", "status": "Limited", "source": "OpenStreetMap", "confidence": "MEDIUM"})
    else:
        acc.append({"label": "Wheelchair Accessible", "status": "Unknown", "source": "OpenStreetMap", "confidence": "UNKNOWN"})

    # Elevator / Lift
    elevator = tags.get("elevator")
    if elevator:
        st = "Available" if elevator == "yes" else "No"
        acc.append({"label": "Elevator", "status": st, "source": "OpenStreetMap", "confidence": "HIGH"})
    else:
        acc.append({"label": "Elevator", "status": "Unknown", "source": "OpenStreetMap", "confidence": "UNKNOWN"})

    # Blind / Tactile
    tactile = tags.get("tactile_paving")
    if tactile:
        st = "Available" if tactile == "yes" else "No"
        acc.append({"label": "Tactile Paving", "status": st, "source": "OpenStreetMap", "confidence": "HIGH"})

    return acc

def calculate_score(acc_features: list, profile: str) -> dict:
    score = 50 # Base
    known_features = 0
    available_features = 0
    
    for f in acc_features:
        if f["status"] != "Unknown":
            known_features += 1
            if f["status"] == "Available":
                available_features += 1
                
    if known_features > 0:
        score = 40 + int((available_features / known_features) * 60)
    else:
        score = 30 # Penalty for completely unknown

    return {
        "score": score,
        "rating": "Highly Accessible" if score > 80 else "Moderately Accessible" if score > 50 else "Accessibility Unknown",
        "confidence": 90 if known_features > 2 else 50
    }
