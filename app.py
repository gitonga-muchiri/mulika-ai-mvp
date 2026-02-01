from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
from engine_c import run_full_audit
from engine_e import run_batch_processor
import pandas as pd
from difflib import get_close_matches

app = Flask(__name__)

# --- AI BRAIN (Simple NLP) ---
def detect_intent(message):
    message = message.lower()
    
    # Intent 1: Batch Audit
    if any(x in message for x in ['batch', 'all projects', 'full scan', 'time machine', 'all 20']):
        return "BATCH"
    
    # Intent 2: Single Audit (Pattern: "audit [project name]")
    if "audit" in message or "check" in message or "verify" in message or "ukaguzi" in message:
        return "SINGLE"
        
    return "UNKNOWN"

@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').strip()
    sender_number = request.values.get('From', '')
    
    resp = MessagingResponse()
    msg = resp.message()
    
    intent = detect_intent(incoming_msg)
    
    # --- HANDLING BATCH AUDIT ---
    if intent == "BATCH":
        msg.body("🏭 Starting Batch Audit on 20 projects... This will take a moment.")
        run_batch_processor() # Run the engine
        
        # Read results
        if os.path.exists("batch_audit_results.csv"):
            df = pd.read_csv("batch_audit_results.csv")
            reds = len(df[df['Verdict'] == 'RED FLAG'])
            msg.body(f"✅ Batch Complete.\n🚨 Red Flags: {reds}\n✅ Verified: {len(df)-reds}\nReply with a project name to see photos.")
        else:
            msg.body("❌ Error running batch.")
            
    # --- HANDLING SINGLE AUDIT ---
    elif intent == "SINGLE":
        # Extract project name (AI Guessing)
        # Remove keywords to find the name
        clean_msg = incoming_msg.lower().replace("audit", "").replace("check", "").replace("ukaguzi", "").strip()
        project_name = clean_msg.title()
        
        msg.body(f"🛰️ Connecting to Sentinel-2 for '{project_name}'...")
        
        # Coordinates (Demo Map)
        lat, lon = 0.5186, 36.6578 # Default Rumuruti
        if "konza" in clean_msg: lat, lon = -1.6961, 37.1852
        if "nairobi" in clean_msg: lat, lon = -1.3622, 36.9317
        
        verdict, score, img1, img2 = run_full_audit(lat, lon, "WhatsApp_Request", "2023-01-01", "2024-01-01")
        
        # TEXT VERDICT
        if verdict == "RED FLAG":
            msg.body(f"🚨 RED FLAG DETECTED!\nGround Change: {score:.1f}%\nStatus: Ghost Project")
        else:
            msg.body(f"✅ GREEN FLAG.\nGround Change: {score:.1f}%\nStatus: Active Construction")
            
        # SEND IMAGES (The 'media' parameter)
        # Note: Codespaces URL changes, so we rely on relative hosting or public access
        # For Hackathon demo, showing the Text Verdict is key if media fails due to local host
        # But we try to attach:
        base_url = request.host_url # This gets the public ngrok/codespace link
        
        if img1:
            msg.media(f"{base_url}static/{img1}")
        if img2:
            msg.media(f"{base_url}static/{img2}")
            
    # --- GREETING ---
    else:
        msg.body("🤖 Mulika AI Online.\n\nYou can say:\n1. 'Audit Nairobi Expressway'\n2. 'Run Batch Scan'\n3. 'Fanya ukaguzi Karatina'")

    return str(resp)

# SERVE IMAGES
from flask import send_from_directory
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

if __name__ == "__main__":
    app.run(port=5000)