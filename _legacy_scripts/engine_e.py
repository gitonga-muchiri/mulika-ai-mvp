import pandas as pd
from engine_c import run_full_audit
import os
import shutil

def run_batch_processor(csv_path="central_database.csv"):
    print(f"\n--- 🏭 BATCH PROCESSOR ---")
    if not os.path.exists(csv_path): return
        
    df = pd.read_csv(csv_path)
    audit_results = []
    contractor_strikes = {}
    
    evidence_dir = "batch_evidence"
    if os.path.exists(evidence_dir): shutil.rmtree(evidence_dir)
    os.makedirs(evidence_dir)
    
    for index, row in df.iterrows():
        name = row.get('Project', 'Unknown')
        lat = row.get('Latitude')
        lon = row.get('Longitude')
        cont = row.get('Contractor', 'Unknown')
        
        if pd.isna(lat): continue
        
        # Blind Audit
        unique_id = f"{evidence_dir}/Batch_{index+1}"
        verdict, score, i1, i2 = run_full_audit(lat, lon, unique_id, "2023-01-01", "2024-01-01")
        
        if verdict == "RED FLAG":
            contractor_strikes[cont] = contractor_strikes.get(cont, 0) + 1
            
        audit_results.append({
            "Project": name, "Contractor": cont, "Location": row.get('Location'),
            "Verdict": verdict, "Score": score,
            "Img_Before": i1, "Img_After": i2
        })

    pd.DataFrame(audit_results).to_csv("batch_audit_results.csv", index=False)
    
    # Update Blacklist
    blacklist = [{"Contractor": k, "Red_Flags": v} for k, v in contractor_strikes.items() if v >= 2]
    if blacklist: pd.DataFrame(blacklist).to_csv("contractor_blacklist.csv", index=False)

if __name__ == "__main__":
    run_batch_processor()