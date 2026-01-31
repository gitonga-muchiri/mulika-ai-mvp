import cv2
import numpy as np
from engine_b import fetch_satellite_image

def compare_images(img1_path, img2_path):
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)
    
    if img1 is None or img2 is None:
        return 0.0

    # Convert to Grayscale
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # Difference & Threshold
    diff = cv2.absdiff(gray1, gray2)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    
    # Calculate % Change
    total_pixels = thresh.size
    change_pixels = np.count_nonzero(thresh)
    percentage = (change_pixels / total_pixels) * 100
    
    return percentage

def run_full_audit(lat, lon, project_name, start_date, end_date):
    print(f"STARTING AUDIT FOR: {project_name}")
    
    # Fetch REAL Images (Engine B will Auto-Retry if cloudy)
    img1_path = fetch_satellite_image(lat, lon, start_date, "BEFORE")
    img2_path = fetch_satellite_image(lat, lon, end_date, "AFTER")
    
    if img1_path and img2_path:
        score = compare_images(img1_path, img2_path)
        
        # VERDICT LOGIC
        # < 5% change = Ghost Project (Red Flag)
        if score < 5.0:
            verdict = "RED FLAG"
        else:
            verdict = "GREEN FLAG"
            
        return verdict, score, img1_path, img2_path
    else:
        # Return Error State
        return "ERROR", 0.0, None, None