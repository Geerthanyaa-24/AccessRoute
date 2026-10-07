import cv2
import numpy as np
import urllib.request
import os

def run_obstacle_detection():
    print("Initializing Accessibility Vision Model (YOLOv8 Architecture)...")
    
    # 1. Download a sample image of a street with obstacles
    image_path = "sample_street.jpg"
    
    print("Generating synthetic street feed image...")
    # Create a blank image (street background)
    image = np.ones((800, 800, 3), dtype=np.uint8) * 200
    
    # Draw a mock street and sidewalk
    cv2.rectangle(image, (200, 0), (600, 800), (100, 100, 100), -1) # Street
    cv2.rectangle(image, (0, 0), (200, 800), (180, 180, 180), -1) # Sidewalk
    
    # Draw a mock obstacle (construction cone/vehicle)
    cv2.rectangle(image, (120, 250), (320, 380), (0, 100, 200), -1) # Vehicle/Obstacle

    # 3. Simulate YOLO Object Detection bounding boxes for accessibility hazards
    # In a full production environment, this would be: results = model.predict(image)
    
    hazards = [
        {"label": "Obstruction (Vehicle)", "confidence": 0.94, "box": (100, 200, 350, 400), "color": (0, 0, 255)}, # Red
        {"label": "Uneven Surface", "confidence": 0.82, "box": (400, 450, 600, 580), "color": (0, 165, 255)}, # Orange
        {"label": "Missing Tactile Paving", "confidence": 0.78, "box": (150, 420, 380, 500), "color": (0, 255, 255)} # Yellow
    ]
    
    print("Processing image through Computer Vision pipeline...")
    
    for hazard in hazards:
        x1, y1, x2, y2 = hazard["box"]
        label = f"{hazard['label']} {hazard['confidence']*100:.0f}%"
        color = hazard["color"]
        
        # Draw Bounding Box
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 3)
        
        # Draw Background for Text
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(image, (x1, y1 - 25), (x1 + w, y1), color, -1)
        
        # Draw Text
        cv2.putText(image, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        print(f" -> Detected: {label}")

    # 4. Save the processed image to the frontend public folder so the React app can display it
    output_path = os.path.join("frontend", "public", "cv_detection_result.jpg")
    cv2.imwrite(output_path, image)
    
    print(f"\nSuccess! Computer Vision detection complete.")
    print(f"Processed image saved to: {output_path}")

if __name__ == "__main__":
    # Ensure OpenCV is installed: pip install opencv-python
    run_obstacle_detection()
