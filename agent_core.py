import os
from dotenv import load_dotenv
from supabase import create_client, Client
from google import genai  # <-- The brand new library

# 1. Load the hidden keys from the .env file
load_dotenv()

# 2. Connect to the Supabase Database
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: Supabase keys not found. Check your .env file.")
    exit()

supabase: Client = create_client(url, key)

# 3. Connect to the Google Gemini AI Brain using the NEW system
gemini_key = os.environ.get("GEMINI_API_KEY")
if not gemini_key:
    print("Error: Gemini key not found. Check your .env file.")
    exit()

client = genai.Client(api_key=gemini_key)

def wake_up_agent():
    print("Initializing Mulika AI Core Agent...")
    
    # Test Database Connection
    try:
        response = supabase.table("projects").select("*").limit(1).execute()
        print("✅ DATABASE STATUS: Connected successfully to Supabase PostGIS.")
    except Exception as e:
        print(f"❌ DATABASE ERROR: {e}")

    # Test Gemini Connection
    try:
        print("Testing Neural Link to Gemini 2.5 Flash...")
        ai_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="You are Mulika AI, Kenya's digital auditor. Say a 1-sentence greeting in Swahili."
        )
        print(f"✅ AI STATUS: Online. Gemini says: '{ai_response.text.strip()}'")
    except Exception as e:
        print(f"❌ AI ERROR: {e}")

if __name__ == "__main__":
    wake_up_agent()