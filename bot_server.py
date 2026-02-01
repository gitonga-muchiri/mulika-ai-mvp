from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from engine_nlp import process_whatsapp_query
import os

app = Flask(__name__)

@app.route("/bot", methods=['POST'])
def bot():
    """
    1. Receives WhatsApp msg from User.
    2. Sends it to Mulika AI (Gemini).
    3. Returns the smart answer to User.
    """
    # 1. Get incoming text
    incoming_msg = request.values.get('Body', '').strip()
    sender = request.values.get('From', '')
    
    print(f"\n📩 NEW WHATSAPP from {sender}")
    print(f"   👤 User said: {incoming_msg}")
    
    # 2. Get AI Response
    # This calls engine_nlp.py -> which calls Google Gemini
    result = process_whatsapp_query(incoming_msg)
    response_text = result['text']
    
    print(f"   🤖 Mulika replying: {response_text[:50]}...")

    # 3. Send back to Twilio
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(response_text)
    
    return str(resp)

if __name__ == "__main__":
    print("🚀 MULIKA WHATSAPP LISTENER ACTIVE ON PORT 5000")
    print("   waiting for messages...")
    app.run(host='0.0.0.0', port=5000)