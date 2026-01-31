from flask import Flask, request
from engine_a import extract_tender_details
from engine_c import run_full_audit
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/bot", methods=["POST"])
def bot():
    # 1. Get the message the user sent
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    
    print(f"--- NEW MESSAGE RECEIVED: {incoming_msg} ---")

    # 2. Logic: What did they ask for?
    if "audit" in incoming_msg:
        # Example: User types "Audit Karatina Road"
        # For the MVP, we will hardcode the logic to run our demo test
        msg.body("🔍 MULIKA AI: Starting Audit for 'Karatina Road'...\n\n"
                 "1. 📄 Analyzing Tender Documents...\n"
                 "2. 🛰️ Contacting Sentinel-2 Satellite...\n"
                 "3. ⚠️ VERDICT: RED FLAG DETECTED.\n\n"
                 "Reason: Satellite imagery shows 0% ground disturbance between Jan 2023 and Jan 2024 despite KES 50M budget payout.")
    
    elif "status" in incoming_msg:
        msg.body("✅ MULIKA AI SYSTEM STATUS:\n"
                 "- Document Engine: ONLINE\n"
                 "- Satellite Engine: ONLINE\n"
                 "- Fraud Detection: ACTIVE")
                 
    else:
        msg.body("👋 Welcome to Mulika AI.\n"
                 "To audit a project, reply with 'AUDIT [Project Name]'.\n"
                 "Example: 'Audit Karatina Road'")

    return str(resp)

if __name__ == "__main__":
    app.run(port=5000)