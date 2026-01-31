import cv2
import numpy as np
from engine_b import fetch_satellite_image
from config import DATE_BEFORE, DATE_AFTER

def compare_images(img1_path, img2_path):
    print(f"\n--- COMPARING: {img1_path} vs {img2_path} ---")
    
    # 1. Load the two images
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)
    
    if img1 is None or img2 is None:
        return "ERROR: Images are empty/corrupt."

    # 2. Convert to Grayscale (Simplifies the math)
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # 3. Calculate "Difference" (The Magic Trick)
    # We subtract pixel values. 
    # If pixel was "Brown" (Dirt) and is now "Black" (Tarmac), the difference is HUGE.
    # If pixel was "Green" and stays "Green", difference is ZERO.
    diff = cv2.absdiff(gray1, gray2)
    
    # 4. Calculate a "Change Score"
    # We sum up all the differences to get one big number.
    score = np.sum(diff)
    print(f">>> CHANGE SCORE DETECTED: {score}")
    
    # 5. The Verdict (Red Flag Logic)
    # Threshold: We pick a number. Below this = No Work Done.
    THRESHOLD = 100000 
    
    if score < THRESHOLD:
        return "RED FLAG: GHOST PROJECT (No significant physical change detected)"
    else:
        return "GREEN FLAG: WORK DETECTED (Ground disturbance/Construction visible)"

def run_full_audit(lat, lon, project_name):
    print(f"STARTING AUDIT FOR: {project_name}")
    
    # Step 1: Get Before Image
    print("1. Fetching Baseline Image...")
    img1 = fetch_satellite_image(lat, lon, DATE_BEFORE, "BEFORE")
    
    # Step 2: Get After Image
    print("2. Fetching Current Status Image...")
    img2 = fetch_satellite_image(lat, lon, DATE_AFTER, "AFTER")
    
    # Step 3: Compare
    if img1 and img2:
        result = compare_images(img1, img2)
        print("\n" + "="*50)
        print(f"MULIKA AI AUDIT REPORT: {project_name}")
        print(f"TIMEFRAME: {DATE_BEFORE} to {DATE_AFTER}")
        print(f"RESULT: {result}")
        print("="*50 + "\n")
    else:
        print("ERROR: Could not complete audit. Satellite connection failed.")

if __name__ == "__main__":
    # TEST: We will check the same Nairobi location
    # Since it's a built-up city, the change might be small (Red Flag) 
    # unless a building was demolished/built.
    run_full_audit(-1.286389, 36.817223, "Nairobi_Road_Test")