import cv2
import numpy as np
from skimage.morphology import skeletonize

def calculate_road_length(img_path_before, img_path_after, resolution_meters_per_pixel=10):
    # 1. Load Images
    img1 = cv2.imread(img_path_before, 0) # Load as grayscale
    img2 = cv2.imread(img_path_after, 0)
    
    if img1 is None or img2 is None:
        return 0.0

    # 2. Create a "Difference Mask" (What changed?)
    # We blur slightly to remove noise (clouds/shadows)
    img1 = cv2.GaussianBlur(img1, (5, 5), 0)
    img2 = cv2.GaussianBlur(img2, (5, 5), 0)
    
    diff = cv2.absdiff(img1, img2)
    
    # 3. Threshold (Convert to Black & White)
    # If change > 30 (out of 255), it's a road/building.
    _, binary_mask = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    
    # 4. Skeletonize (Turn the thick road blob into a 1-pixel line)
    # We divide by 255 to make it 0s and 1s
    skeleton = skeletonize(binary_mask // 255)
    
    # 5. Count Pixels
    road_pixels = np.sum(skeleton)
    
    # 6. Calculate Length
    # Total KM = (Pixels * 10 meters) / 1000
    length_km = (road_pixels * resolution_meters_per_pixel) / 1000
    
    return round(length_km, 2)