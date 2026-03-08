import os
import random
from dotenv import load_dotenv
from supabase import create_client, Client
from faker import Faker

# 1. Setup
fake = Faker()
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def build_the_matrix():
    print("Initiating Data Injection into Supabase...")
    
    # 2. Generate 10 Contractors (Injecting a Cartel Ring)
    shared_cartel_phone = "+254700111222" # We will hunt for this number later
    contractor_ids = []
    
    for i in range(10):
        # The first 3 companies will share a phone number (Cartel Alert!)
        phone = shared_cartel_phone if i < 3 else fake.phone_number()
        
        contractor_data = {
            "company_name": fake.company() + " Construction Ltd",
            "kra_pin": "P" + str(fake.random_number(digits=9, fix_len=True)) + "X",
            "directors_names": fake.name() + ", " + fake.name(),
            "phone_number": phone,
            "po_box": f"P.O Box {fake.random_int(min=100, max=9999)} Nairobi",
            "registration_number": "CPR/" + str(fake.random_number(digits=4))
        }
        
        # Save to database
        result = supabase.table("contractors").insert(contractor_data).execute()
        contractor_ids.append(result.data[0]['id'])
        print(f"Registered Contractor: {contractor_data['company_name']}")

    print("\n--- Generating Government Projects ---")
    
    # 3. Generate 20 Government Projects across Kenya
    counties = ["Nairobi", "Kiambu", "Nakuru", "Turkana", "Kilifi"]
    
    for i in range(20):
        # Generate random GPS coordinates within Kenya's borders
        lat = random.uniform(-4.0, 4.0)
        lon = random.uniform(34.0, 41.0)
        
        project_data = {
            "tender_no": "TENDER/" + str(fake.random_number(digits=6)),
            "project_name": fake.bs().title() + " Infrastructure",
            "procuring_entity": random.choice(counties) + " County Government",
            "budget_allocated": random.randint(10000000, 500000000), # 10M to 500M KES
            "county": random.choice(counties),
            "latitude": lat,
            "longitude": lon,
            "location": f"POINT({lon} {lat})", # This triggers the PostGIS Map feature
            "contractor_id": random.choice(contractor_ids),
            "project_status": random.choice(["Ongoing", "Stalled", "Completed"])
        }
        
        supabase.table("projects").insert(project_data).execute()
        print(f"Pinned Project on Map: {project_data['project_name']} in {project_data['county']}")
        
    print("\n✅ DATA INJECTION COMPLETE! Your map database is alive and populated.")

if __name__ == "__main__":
    build_the_matrix()