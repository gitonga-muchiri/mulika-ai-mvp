import os
from twilio.rest import Client

# --- TWILIO KEYS (PASTE YOURS HERE) ---
# You can get these from console.twilio.com
TWILIO_SID = "AC..."  # <--- Paste SID inside quotes
TWILIO_TOKEN = "..."   # <--- Paste Token inside quotes
TWILIO_FROM = "whatsapp:+14155238886" # Default Sandbox Number

def send_real_whatsapp(to_number, message_body, media_url=None):
    """
    Sends a WhatsApp message via Twilio.
    """
    # 1. Validation
    if not TWILIO_SID.startswith("AC"):
        return False, "⚠️ Twilio SID missing. Edit engine_alert.py"
    
    if "..." in TWILIO_TOKEN:
        return False, "⚠️ Twilio Token missing. Edit engine_alert.py"

    # 2. Format Number (Must have country code, e.g., +254)
    if not to_number.startswith("+"):
        return False, "⚠️ Invalid Number. Use format: +2547..."

    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        
        # 3. Prepare Message
        msg_params = {
            "from_": TWILIO_FROM,
            "body": message_body,
            "to": f"whatsapp:{to_number}"
        }
        
        # Note: Local file paths cannot be sent via Twilio URL directly without hosting.
        # For this demo, we send the Text Report. 
        # (To send images, they must be hosted on a public URL like AWS S3).

        message = client.messages.create(**msg_params)
        
        return True, f"✅ Sent! SID: {message.sid}"
        
    except Exception as e:
        error_msg = str(e)
        if "not currently authenticated" in error_msg:
            return False, "⚠️ SANDBOX ERROR: You must send 'join <code >' to the Twilio number first!"
        return False, f"❌ Error: {error_msg}"

def generate_whatsapp_link(phone, text):
    """
    Backup: Generates a clickable link if API fails.
    """
    import urllib.parse
    safe_text = urllib.parse.quote(text)
    return f"[https://wa.me/](https://wa.me/){phone}?text={safe_text}"