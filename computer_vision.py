import os
import cv2
import numpy as np

def assess_image(image_path: str = None, image_bytes: bytes = None) -> dict:
    """
    Placeholder Computer Vision Interface for Obstacle Detection.
    
    IMPORTANT DISCLAIMER:
    This function currently serves as a FALLBACK/MOCK architectural interface.
    No pre-trained real-time CV model (e.g., YOLO) is currently loaded.
    This interface simulates the expected output structure for the pipeline.
    """
    
    # 1. Fallback validation (Check if image exists if path is provided)
    if image_path and not os.path.exists(image_path):
        return {
            "obstacle_detected": False,
            "obstacle_type": "none",
            "confidence": 0.0,
            "error": "Image not found."
        }
        
    # 2. Mock Inference Logic (Since no real model is implemented yet)
    # We pretend the model detected a 'blocked_ramp' with 87% confidence 
    # for testing the integration pipeline.
    
    # In a real implementation, this would be:
    # model = load_yolo_model("weights.pt")
    # results = model.predict(image)
    # return parse_results(results)
    
    return {
        "obstacle_detected": True,
        "obstacle_type": "blocked_ramp",
        "confidence": 0.87
    }

def run_obstacle_detection_demo():
    """Generates the synthetic cv_detection_result.jpg for the frontend dashboard."""
    print("Initializing Placeholder Accessibility Vision Model...")
    
    image = np.ones((800, 800, 3), dtype=np.uint8) * 200
    cv2.rectangle(image, (200, 0), (600, 800), (100, 100, 100), -1) 
    cv2.rectangle(image, (0, 0), (200, 800), (180, 180, 180), -1) 
    cv2.rectangle(image, (120, 250), (320, 380), (0, 100, 200), -1) 

    hazards = [
        {"label": "Obstruction (Vehicle)", "confidence": 0.94, "box": (100, 200, 350, 400), "color": (0, 0, 255)}, 
        {"label": "Uneven Surface", "confidence": 0.82, "box": (400, 450, 600, 580), "color": (0, 165, 255)}, 
        {"label": "Missing Tactile Paving", "confidence": 0.78, "box": (150, 420, 380, 500), "color": (0, 255, 255)} 
    ]
    
    for hazard in hazards:
        x1, y1, x2, y2 = hazard["box"]
        label = f"{hazard['label']} {hazard['confidence']*100:.0f}%"
        color = hazard["color"]
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 3)
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(image, (x1, y1 - 25), (x1 + w, y1), color, -1)
        cv2.putText(image, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    os.makedirs(os.path.join("frontend", "public"), exist_ok=True)
    output_path = os.path.join("frontend", "public", "cv_detection_result.jpg")
    cv2.imwrite(output_path, image)
    print(f"Placeholder image saved to: {output_path}")

if __name__ == "__main__":
    run_obstacle_detection_demo()
    print("Testing CV API Interface:", assess_image())
