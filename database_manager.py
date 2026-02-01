import os
import pandas as pd
import re
import PyPDF2

def extract_details_clean(pdf_path):
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = reader.pages[0].extract_text()
            
        name_match = re.search(r"PROJECT: (.*)", text)
        project_name = name_match.group(1).strip() if name_match else "Unknown"

        budget_match = re.search(r"BUDGET: (.*)", text)
        budget = budget_match.group(1).strip() if budget_match else "0"

        cont_match = re.search(r"CONTRACTOR: (.*)", text)
        contractor = cont_match.group(1).strip() if cont_match else "Unknown"

        loc_match = re.search(r"LOCATION: (.*)", text)
        location = loc_match.group(1).strip() if loc_match else "Kenya"

        lat_match = re.search(r"LAT: ([\-0-9\.]+)", text)
        lat = float(lat_match.group(1)) if lat_match else 0.0

        lon_match = re.search(r"LON: ([\-0-9\.]+)", text)
        lon = float(lon_match.group(1)) if lon_match else 0.0
        
        # STATUS IS GONE. The Database is now agnostic.

        return {
            "Project": project_name,
            "Budget": budget,
            "Contractor": contractor,
            "Location": location,
            "Latitude": lat,
            "Longitude": lon
        }

    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return None

def build_central_database(folder_path="tender_docs"):
    print("--- 🔄 BUILDING CLEAN DATABASE ---")
    if not os.path.exists(folder_path): return

    all_projects = []
    files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    
    for f in files:
        data = extract_details_clean(os.path.join(folder_path, f))
        if data:
            data["File"] = f
            all_projects.append(data)
    
    if all_projects:
        df = pd.DataFrame(all_projects)
        df.to_csv("central_database.csv", index=False)
        print(f"✅ SUCCESS: {len(df)} records saved (NO Status Column).")

if __name__ == "__main__":
    build_central_database()