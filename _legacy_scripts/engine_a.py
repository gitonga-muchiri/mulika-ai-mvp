import PyPDF2
import re

def extract_tender_details(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        
        # --- FIXED REGEX ---
        # 1. Project Name (Look for "TENDER NOTICE:" explicitly based on your generator)
        name_match = re.search(r"TENDER NOTICE:\s*(.*)", text)
        project_name = name_match.group(1).strip() if name_match else "Unknown Project"

        # 2. Budget (Look for "Budget Allocation:")
        budget_match = re.search(r"Budget Allocation:\s*(.*)", text)
        budget = budget_match.group(1).strip() if budget_match else "Unknown Budget"

        # 3. Location (Look for "Ward:")
        loc_match = re.search(r"Ward:\s*(.*)", text)
        location = loc_match.group(1).strip() if loc_match else "Unknown Location"
        
        # 4. Coordinates
        lat_match = re.search(r"Latitude:\s*([0-9\.\-\+]+)", text)
        lon_match = re.search(r"Longitude:\s*([0-9\.\-\+]+)", text)
        
        return {
            "name": project_name,
            "budget": budget,
            "location": location,
            "lat": lat_match.group(1) if lat_match else None,
            "lon": lon_match.group(1) if lon_match else None
        }
    except Exception as e:
        return {}