import pandas as pd
import os

def run_forensic_analysis(csv_path="central_database.csv"):
    print("\n--- 🕵️ RUNNING FORENSIC AI ANALYSIS ---")
    
    if not os.path.exists(csv_path):
        print("❌ Error: Database not found. Run database_manager.py first.")
        return

    df = pd.read_csv(csv_path)
    red_flags = []
    
    # CHECK 1: The "Monopoly" Check 
    contractor_counts = df['Contractor'].value_counts()
    for name, count in contractor_counts.items():
        if count >= 3:
            red_flags.append(f"🚩 MONOPOLY ALERT: '{name}' has won {count} tenders (High Concentration Risk).")

    # CHECK 2: The "Cartel" Check (Shared PO Box)
    box_groups = df.groupby('PO_Box')['Contractor'].unique()
    for box, companies in box_groups.items():
        if len(companies) > 1:
            red_flags.append(f"🚩 CARTEL ALERT: PO Box '{box}' is shared by multiple companies: {companies}. Suggests collusion.")

    # PRINT REPORT
    print("\n=== 🚨 MULIKA AI INTELLIGENCE REPORT 🚨 ===")
    if not red_flags:
        print("No systemic anomalies detected.")
    else:
        for flag in red_flags:
            print(flag)
    print("===========================================\n")

if __name__ == "__main__":
    run_forensic_analysis()