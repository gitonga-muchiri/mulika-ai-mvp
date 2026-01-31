import os
from sentinelhub import SHConfig, SentinelHubRequest, DataCollection, MimeType, CRS, BBox
from config import SH_CLIENT_ID, SH_CLIENT_SECRET
import matplotlib.pyplot as plt
import numpy as np

def fetch_satellite_image(lat, lon, date, title):
    print(f"\n--- CONTACTING SATELLITE FOR: {title} on {date} ---")
    
    # 1. Setup the Configuration (Unlock the door)
    config = SHConfig()
    config.sh_client_id = SH_CLIENT_ID
    config.sh_client_secret = SH_CLIENT_SECRET
    
    # 2. Define the Box (The Area we want to see)
    # We create a small box around the coordinate (approx 1km x 1km)
    box_size = 0.01 
    bbox = BBox(bbox=[lon - box_size, lat - box_size, lon + box_size, lat + box_size], crs=CRS.WGS84)

    # 3. The Request (Ask for True Color Image)
    # We ask for "Bands B04, B03, B02" which makes a regular Red/Green/Blue photo
    request = SentinelHubRequest(
        evalscript="""
            //VERSION=3
            function setup() {
                return {
                    input: ["B04", "B03", "B02"],
                    output: { bands: 3 }
                };
            }
            function evaluatePixel(sample) {
                return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02];
            }
        """,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L1C,
                time_interval=(date, date) # Look for image on this day
            )
        ],
        responses=[
            SentinelHubRequest.output_response("default", MimeType.PNG)
        ],
        bbox=bbox,
        config=config
    )

    # 4. Download
    try:
        print(">>> DOWNLOADING IMAGE CHUNKS...")
        image = request.get_data()[0] # Get the first image found
        
        # Save it to our folder so we can see it
        filename = f"sat_image_{title}_{date}.png"
        plt.imsave(filename, image)
        print(f">>> SUCCESS! Saved as {filename}")
        return filename
        
    except Exception as e:
        print(f"ERROR: Could not fetch image. Satellite might be cloudy or key is wrong. \nDetails: {e}")
        return None

# TEST RUN
if __name__ == "__main__":
    # Coordinates for a place in Nairobi (e.g., Near CBD)
    # Lat: -1.286389, Lon: 36.817223
    fetch_satellite_image(-1.286389, 36.817223, "2024-01-20", "TEST_LOCATION")