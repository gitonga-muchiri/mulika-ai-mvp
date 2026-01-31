import os
from sentinelhub import SHConfig, SentinelHubRequest, DataCollection, MimeType, CRS, BBox
from config import SH_CLIENT_ID, SH_CLIENT_SECRET
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import cv2

def is_image_cloudy_or_empty(image):
    """
    Checks if an image is usable.
    - Rejects if mostly Black (Empty data)
    - Rejects if mostly White (Clouds)
    """
    # 1. Check for Empty Data (Black)
    if np.mean(image) < 5:
        return True, "EMPTY (Black)"

    # 2. Check for Clouds (Bright White pixels)
    # We convert to grayscale to check brightness
    # Image comes in 0-255 range. Clouds are usually > 200.
    if image.shape[2] == 3: # If RGB
        gray = np.mean(image, axis=2)
    else:
        gray = image

    # Count how many pixels are "Very Bright" (> 200 brightness)
    cloud_pixels = np.sum(gray > 220)
    total_pixels = gray.size
    cloud_percentage = (cloud_pixels / total_pixels) * 100

    if cloud_percentage > 15.0: # If more than 15% is white cloud
        return True, f"CLOUDY ({cloud_percentage:.1f}%)"
    
    return False, "CLEAR"

def fetch_satellite_image(lat, lon, date_str, title):
    print(f"\n--- INTELLIGENT SEARCH FOR: {title} starting {date_str} ---")
    
    config = SHConfig()
    config.sh_client_id = SH_CLIENT_ID
    config.sh_client_secret = SH_CLIENT_SECRET
    
    # Define 1km Box
    box_size = 0.01 
    bbox = BBox(bbox=[lon - box_size, lat - box_size, lon + box_size, lat + box_size], crs=CRS.WGS84)

    # LOOP: Try up to 3 times (shifting months)
    current_date = datetime.strptime(date_str, "%Y-%m-%d")
    
    for attempt in range(3):
        # Window: Look at 45 days before the target date
        start_date = (current_date - timedelta(days=45)).strftime("%Y-%m-%d")
        end_date = current_date.strftime("%Y-%m-%d")
        
        print(f"   > Attempt {attempt+1}: Scanning {start_date} to {end_date}...")

        # EVALSCRIPT: Auto-Brightening + True Color
        evalscript = """
        //VERSION=3
        function setup() {
            return {
                input: ["B04", "B03", "B02"],
                output: { bands: 3, sampleType: "AUTO" }
            };
        }
        function evaluatePixel(sample) {
            // Multiply by 2.5 to brighten dark ground
            return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02];
        }
        """

        request = SentinelHubRequest(
            evalscript=evalscript,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L1C,
                    time_interval=(start_date, end_date),
                    maxcc=0.2, # Pre-filter at 20%
                    mosaicking_order="leastCC" # Request least cloudy pixel
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
            bbox=bbox,
            config=config
        )

        try:
            image = request.get_data()[0]
            
            # RUN THE QUALITY CHECK
            is_bad, reason = is_image_cloudy_or_empty(image)
            
            if is_bad:
                print(f"     [X] REJECTED: Image is {reason}. Retrying with earlier dates...")
                # Shift date back by 2 months for next attempt
                current_date = current_date - timedelta(days=60)
                continue
            else:
                # SUCCESS
                print(f"     [✓] ACCEPTED: Image is {reason}.")
                filename = f"sat_image_{title}_{end_date}.png"
                plt.imsave(filename, image)
                return filename

        except Exception as e:
            print(f"     [!] Error on attempt {attempt}: {e}")

    # If all 3 attempts fail, return None (or a placeholder)
    print(">>> CRITICAL FAILURE: Could not find clear image after 3 attempts.")
    return None