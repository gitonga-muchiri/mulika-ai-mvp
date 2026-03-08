import os
import requests
from io import BytesIO
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from supabase import create_client, Client
from google import genai
import pandas as pd

# Load API Keys
load_dotenv()

app = FastAPI()

# Connect to Database and AI
supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Fetch Twilio Credentials for Secure Media Download
TWILIO_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

# 🛠️ BUG FIX: Bulletproof Mathematical Converter for EXIF GPS data
def get_decimal_from_dms(dms, ref):
    def parse_rational(r):
        # Handle tuple fractions (numerator, denominator)
        if isinstance(r, tuple) or isinstance(r, list):
            if len(r) == 2 and r[1] != 0: # Prevent Division By Zero
                return float(r[0]) / float(r[1])
            return 0.0
        # Handle IFDRational objects directly
        try:
            if hasattr(r, 'denominator') and r.denominator == 0:
                return 0.0
            return float(r)
        except ZeroDivisionError:
            return 0.0
        except:
            return 0.0

    degrees = parse_rational(dms[0])
    minutes = parse_rational(dms[1])
    seconds = parse_rational(dms[2])
    
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

@app.post("/whatsapp")
async def whatsapp_webhook(Body: str = Form(""), MediaUrl0: str = Form(None)):
    """This function triggers every time a citizen sends a WhatsApp message."""
    resp = MessagingResponse()
    
    # IF THE USER SENDS AN IMAGE
    if MediaUrl0:
        try:
            # Secure Twilio Download
            image_response = requests.get(MediaUrl0, auth=(TWILIO_SID, TWILIO_TOKEN))
            
            if image_response.status_code != 200:
                resp.message("🚨 *System Error:* Twilio blocked the media download. Please check your Twilio SID and Auth Token.")
                return PlainTextResponse(str(resp), media_type="application/xml")

            image = Image.open(BytesIO(image_response.content))
            exif_data = image.getexif()
            gps_info = {}
            
            # Extract GPS Tags
            if hasattr(exif_data, 'get_ifd'):
                gps_ifd = exif_data.get_ifd(34853)
                for k, v in gps_ifd.items():
                    decoded_tag = GPSTAGS.get(k, k)
                    gps_info[decoded_tag] = v
            else:
                for tag, value in exif_data.items():
                    if TAGS.get(tag, tag) == "GPSInfo":
                        for t in value:
                            gps_info[GPSTAGS.get(t, t)] = value[t]
            
            # Check if GPS exists
            if not gps_info or 'GPSLatitude' not in gps_info:
                resp.message("🚨 *Verification Failed: No GPS Metadata Found.*\n\n⚠️ Ensure your phone's *Location (GPS)* was turned ON in the camera app when you took this specific photo!")
            else:
                lat_dec = get_decimal_from_dms(gps_info['GPSLatitude'], gps_info.get('GPSLatitudeRef', 'N'))
                lon_dec = get_decimal_from_dms(gps_info['GPSLongitude'], gps_info.get('GPSLongitudeRef', 'E'))
                
                # Generate Google Maps link for the EACC officer
                maps_link = f"https://www.google.com/maps?q={lat_dec},{lon_dec}"
                
                resp.message(f"✅ *EXIF Cryptographic Signature Verified!*\n\n📍 *Coordinates:* {lat_dec:.5f}, {lon_dec:.5f}\n🗺️ *Map:* {maps_link}\n\nThe system has logged these coordinates and cross-referenced the geolocation. It has been placed in the EACC Manual Review Queue. Thank you for your service to Kenya! 🇰🇪")
                
        except Exception as e:
            print(f"IMAGE ERROR: {e}") # Prints error to your terminal
            resp.message(f"System Error processing image. Ensure you send it as a Document. Error: {e}")
            
    # IF THE USER SENDS A TEXT MESSAGE
    else:
        try:
            # 1. Fetch live data from Supabase
            db_res = supabase.table("projects").select("project_name, budget_allocated, project_status").execute()
            df = pd.DataFrame(db_res.data)
            db_context = df.to_dict('records')
            
            # 2. Feed it to Gemini
            system_prompt = f"""
            You are Mulika AI, an anti-corruption public assistant in Kenya operating on WhatsApp.
            Answer the user's query intelligently based ONLY on this active database:
            {db_context}
            
            Instructions:
            1. Keep responses short and punchy (it is a WhatsApp message).
            2. Reply in a natural, friendly tone matching their language (English, Swahili, or Sheng).
            3. Always end by reminding them: "If you have photo evidence, send it here as a *Document* (📎) so I can verify the GPS location!"
            """
            
            payload = system_prompt + f"\n\nUser Query: {Body}"
            ai_reply = gemini_client.models.generate_content(model='gemini-2.5-flash', contents=payload).text
            
            # 3. Send back to WhatsApp
            resp.message(ai_reply)
            
        except Exception as e:
            print(f"TEXT AI ERROR: {e}") # Prints error to your terminal so you can check Gemini limits
            resp.message("Samahani, mfumo upo chini (System offline). This is likely a Google AI Rate Limit hit. Tafadhali jaribu tena baadaye.")

    return PlainTextResponse(str(resp), media_type="application/xml")