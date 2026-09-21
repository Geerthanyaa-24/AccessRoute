def calculate_accessibility_score(features: dict) -> dict:
    """
    Transparent scoring engine for accessibility.
    Returns individual component scores and a final weighted score.
    """
    
    # 1. Surface Score (0-20)
    surface = features.get('surface', 'unknown').lower()
    surface_weights = {
        'asphalt': 20,
        'concrete': 20,
        'paving_stones': 15,
        'cobblestone': 5,
        'dirt': 2,
        'gravel': 2,
        'unknown': 10
    }
    surface_score = surface_weights.get(surface, 10)
    
    # 2. Slope Score (0-30)
    # Wheelchair standards generally say >8% is very difficult.
    slope = abs(features.get('incline', 0.0))
    if slope <= 2.0:
        slope_score = 30
    elif slope <= 5.0:
        slope_score = 20
    elif slope <= 8.0:
        slope_score = 10
    else:
        slope_score = 0
        
    # 3. Obstacle Score (0-30)
    # Penalize heavily for obstacles
    obstacles = int(features.get('obstacle_count', 0))
    if obstacles == 0:
        obstacle_score = 30
    elif obstacles == 1:
        obstacle_score = 15
    elif obstacles == 2:
        obstacle_score = 5
    else:
        obstacle_score = 0
        
    # 4. Infrastructure (0-20)
    # e.g., Ramps, Tactical Paving
    ramp_score = 10 if features.get('has_ramp', False) else 0
    tactile_score = 10 if features.get('tactile_paving', False) else 0
    infra_score = ramp_score + tactile_score
    
    # Total Score
    total_score = surface_score + slope_score + obstacle_score + infra_score
    
    return {
        "overall_score": total_score,
        "components": {
            "surface_score": surface_score,
            "slope_score": slope_score,
            "obstacle_score": obstacle_score,
            "infrastructure_score": infra_score,
            "ramp_score": ramp_score,
            "tactile_score": tactile_score
        }
    }

def calculate_safety_score(features: dict) -> dict:
    """
    Separate safety score focusing purely on danger levels.
    """
    score = 100
    penalties = []
    
    obstacles = int(features.get('obstacle_count', 0))
    if obstacles > 0:
        score -= (obstacles * 15)
        penalties.append(f"{obstacles} physical obstacles detected.")
        
    slope = abs(features.get('incline', 0.0))
    if slope > 8.0:
        score -= 30
        penalties.append(f"Dangerously steep slope ({slope}%).")
        
    surface = features.get('surface', 'unknown').lower()
    if surface in ['cobblestone', 'dirt', 'gravel']:
        score -= 20
        penalties.append(f"Unsafe surface type: {surface}.")
        
    score = max(0, score) # Clamp at 0
    
    return {
        "safety_score": score,
        "penalties": penalties
    }
