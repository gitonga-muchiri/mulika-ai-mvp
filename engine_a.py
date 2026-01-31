import PyPDF2
import re

def extract_tender_details(pdf_path):
    print(f"--- ANALYZING: {pdf_path} ---")
    
    # Open the PDF file
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            # Read every page
            for page in reader.pages:
                text += page.extract_text() + "\n"
                
        print(">>> DOCUMENT READ SUCCESSFULLY. SEARCHING FOR DATA...")
        
        # --- THE INTELLIGENCE (Regex Patterns) ---
        # We are looking for keywords like "Project Name" and "Budget"
        # 1. Look for lines starting with "Project Title:" or similar
        project_name_match = re.search(r"(Project Title|Project Name):\s*(.*)", text, re.IGNORECASE)
        project_name = project_name_match.group(2).strip() if project_name_match else "NOT FOUND"

        # 2. Look for Budget/Cost (Looking for KES, Ksh, or numbers)
        budget_match = re.search(r"(Budget|Cost|Amount):\s*(KES|Ksh\.?|Shs\.?)\s*([\d,]+)", text, re.IGNORECASE)
        budget = f"{budget_match.group(2)} {budget_match.group(3)}" if budget_match else "NOT FOUND"

        # 3. Look for Location (Simplified for MVP)
        location_match = re.search(r"(Location|County|Ward):\s*(.*)", text, re.IGNORECASE)
        location = location_match.group(2).strip() if location_match else "NOT FOUND"

        # --- REPORT ---
        print("\n=== MULIKA AI: TENDER EXTRACTION REPORT ===")
        print(f"PROJECT:  {project_name}")
        print(f"LOCATION: {location}")
        print(f"BUDGET:   {budget}")
        print("===========================================\n")
        
        return {"name": project_name, "location": location, "budget": budget}

    except Exception as e:
        print(f"ERROR: Could not read file. Reason: {e}")
        return None

# This line runs the function when you press Play
if __name__ == "__main__":
    # We will create this dummy file in Step 4
    extract_tender_details("sample_tender.pdf")