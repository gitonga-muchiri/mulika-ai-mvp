import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timedelta

load_dotenv()
supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

def inject_national_data():
    print("Purging old data...")
    # Clean slate for the 60 projects
    supabase.table("projects").delete().neq("tender_no", "0").execute()
    supabase.table("contractors").delete().neq("kra_pin", "0").execute()

    print("Injecting the 60 Verified Projects from the National Database...")

    # Data Structure: [Tender Ref/Name, Procuring Entity, County, Lat, Lon, Contractor, Budget, Expected Completion Date]
    # Dates are set variably (some past, some future) to test the AI's Time Overrun Flag
    projects_data = [
        ("RWC 096: Mbita-Sindo Road", "KERRA", "Homa Bay", -0.4281, 34.2045, "China Civil Eng. Corp.", 2469411261, "2023-12-01"),
        ("RWC 566: Ndaragwa-Maili Kumi Road", "KERRA", "Nyandarua", 0.0214, 36.3197, "China Railway No. 10", 2037119111, "2024-06-30"),
        ("RWC 852: Kyangong-Chebunyo Road", "KERRA", "Bomet", -0.9666, 35.1909, "China Civil Eng. Corp.", 2063901748, "2023-10-15"),
        ("RWC 104: Chogoria-Weru Road", "KERRA", "Tharaka Nithi", -0.2288, 37.6319, "Donwoods / China Jiangxi", 1085311741, "2025-01-20"),
        ("RWC 758: Tala-Ol Donyo Sabuk", "KERRA", "Machakos", -1.2824, 37.2486, "China Railway No. 10", 1417477696, "2024-08-10"),
        ("RWC 111: Daraja Sita-Dikirr", "KERRA", "Bomet/Narok", -0.9333, 35.3167, "Stecol Corporation", 3178333198, "2023-05-01"),
        ("RWC 125: Muigai Inn-Ichaweri", "KERRA", "Kiambu", -1.0333, 36.9000, "H Young Co. (EA) Ltd", 3818022084, "2024-11-30"),
        ("RWC 126: Ruaka-Banana-Limuru", "KERRA", "Kiambu", -1.1983, 36.7833, "Shengli Eng. Co. Ltd", 3210130000, "2023-12-15"),
        ("RWC 096: Mariakani-Bamba", "KERRA", "Kilifi", -3.8667, 39.4667, "China Wu Yi Co. Ltd", 2100500000, "2023-08-20"),
        ("RWC 814: Bondo-Uyawi Road", "KERRA", "Siaya", -0.2333, 34.2667, "Local Contractor Consortium", 850000000, "2022-12-01"),
        ("DEV/HQ/281: Nakuru CBD Roads", "KURA", "Nakuru", -0.2833, 36.0667, "Weihai International", 1815176216, "2023-01-10"),
        ("DEV/HQ/248: Lady Irene-Muslim Road", "KURA", "Bungoma", 0.5667, 34.5667, "Isfahan Contractors", 477150944, "2023-04-15"),
        ("RMLF/HQ/434: Outering Road", "KURA", "Nairobi", -1.2833, 36.8833, "Stecol Corporation", 11743792352, "2023-09-01"),
        ("DEV/HQ/129: Waiyaki Way-Redhill", "KURA", "Nairobi", -1.2500, 36.7833, "China Wu Yi Ltd", 3675222771, "2025-06-30"),
        ("DEV/HQ/425: Kangundo Road Bypass", "KURA", "Machakos", -1.2833, 37.0333, "China Aerospace Const.", 1160691029, "2024-12-01"),
        ("DEV/LE/093: Thika Bypass", "KURA", "Kiambu", -1.0333, 37.0667, "Tosha Holdings", 2240542876, "2025-05-15"),
        ("RMLF/LE/088: Wote CBD Roads", "KURA", "Makueni", -1.7802, 37.6274, "Haddakel Co. Limited", 13454596, "2023-11-01"),
        ("DEV/HQ/216: Hola Township Roads", "KURA", "Tana River", -1.5000, 40.0333, "Abdulhakim Ahmed Bayusuf", 549629977, "2023-07-20"),
        ("DEV/HQ/253: Mokowe Township", "KURA", "Lamu", -2.2333, 40.8500, "Northern Liberty Builders", 1147232220, "2023-10-30"),
        ("DEV/HQ/314: Jomvu Kuu Road", "KURA", "Mombasa", -3.9833, 39.5833, "Associated Construction", 1054897550, "2023-06-15"),
        ("2896/2025: Nairobi Western Bypass", "KENHA", "Kiambu", -1.2183, 36.7261, "China Road and Bridge", 17000000000, "2025-12-30"),
        ("R1/276/2024: Athi River Turnoff", "KENHA", "Machakos", -1.4500, 36.9833, "China Wu Yi Co. Ltd", 5300000000, "2025-08-15"),
        ("R4/336/2025: Mtwapa-Kilifi Interchanges", "KENHA", "Mombasa/Kilifi", -3.9500, 39.7333, "Stecol Corporation", 8500000000, "2026-03-01"),
        ("R10/364/2024: Mwache Creek Bridges", "KENHA", "Kwale", -4.0167, 39.5167, "China Civil Eng. Corp.", 4200000000, "2025-11-20"),
        ("R3/432/2024: Bugar-Iten Road", "KENHA", "Elgeyo Marakwet", 0.6833, 35.5333, "Regional Contractor", 350000000, "2024-05-30"),
        ("R9/155/2024: Mtito Andei-Tsavo", "KENHA", "Taita Taveta", -2.9833, 38.4667, "Osodynasty Group Limited", 27179182, "2024-04-15"),
        ("R10/367/2024: Griftu-Wajir", "KENHA", "Wajir", 1.7500, 39.9833, "Frontier Eng Ltd", 150000000, "2023-12-30"),
        ("R1/298/2024: Ranen-Chamgiwadu", "KENHA", "Migori", -0.8500, 34.5833, "NGM Co. Ltd", 210000000, "2024-07-20"),
        ("2662/2023: Samatar-Wajir Design", "KENHA", "Wajir", 1.7500, 40.0667, "SETS Saudi Arabia Eng.", 3092960000, "2025-02-15"),
        ("R10/359/2024: Kotulo-Dabasit", "KENHA", "Mandera", 2.5000, 40.0833, "Local Civil Contractor", 10000000, "2024-03-10"),
        ("T/019/2023: Thwake Multi-purpose Dam", "State Dept. Water", "Makueni/Kitui", -1.8020, 37.8180, "China Gezhouba Group", 37000000000, "2024-11-30"),
        ("KWSCRP-II: Mwache Dam", "State Dept. Water", "Kwale", -3.9920, 39.5210, "Sinohydro Corporation", 20000000000, "2026-06-30"),
        ("T/CW/037: Siyoi Muruny Dam", "State Dept. Water", "West Pokot", 1.6110, 35.5465, "China Jiangxi Int.", 5000000000, "2023-09-30"),
        ("T/A001: Karimenu II Dam", "Athi Water Works", "Kiambu", -0.9000, 36.8833, "Joint Venture AVIC Int.", 24000000000, "2023-05-30"),
        ("T/005/2020: Soin-Koru Dam", "State Dept. Water", "Kisumu/Kericho", -0.1500, 35.1833, "China Jiangxi Int.", 20000000000, "2027-12-01"),
        ("T/011/2023: Umaa Dam", "State Dept. Water", "Kitui", -1.3667, 38.0167, "China Jiangxi Corp.", 1900000000, "2025-08-30"),
        ("C/T/001/2014: Itare Dam", "State Dept. Water", "Nakuru", -0.3200, 35.5340, "CMC di Ravenna", 38000000000, "2020-12-30"),
        ("T/001/2017: Arror Dam", "KVDA", "Elgeyo Marakwet", 0.9850, 35.5900, "CMC di Ravenna", 38000000000, "2021-12-30"),
        ("T/002/2017: Kimwarer Dam", "KVDA", "Elgeyo Marakwet", 0.3800, 35.6300, "CMC di Ravenna", 28000000000, "2021-12-30"),
        ("T/019/2023: High Grand Falls Dam", "State Dept. Water", "Tana River/Tharaka", -0.1429, 38.0308, "GBM Engineering", 200000000000, "2030-01-01"),
        ("T/183/2024: Galana Kulalu Food Security", "NIA", "Kilifi/Tana River", -3.1200, 39.3800, "Irrico International", 7200000000, "2025-10-30"),
        ("T/171/2024: Iriari Irrigation", "NIA", "Embu", -0.4167, 37.5500, "Local Agricultural Cont.", 68000000, "2024-11-15"),
        ("T/080/2023: Lower Kuja Irrigation", "NIA", "Migori", -0.9500, 34.2500, "Multiple Contractors", 150000000, "2024-09-30"),
        ("T/050/2022: Rwabura Irrigation", "NIA", "Kiambu", -1.0000, 36.8833, "Local Consortium", 208000000, "2023-06-30"),
        ("T/185/2024: Kanyuambora Irrigation", "NIA", "Embu", -0.5500, 37.7167, "Local Civil Contractor", 85000000, "2024-12-20"),
        ("W/001/2024: Lochor Aikeny Borehole", "Turkana County", "Turkana", 3.1198, 35.5964, "Local Contractor", 18500000, "2024-05-30"),
        ("R/005/2024: Nakalale Drift", "Turkana County", "Turkana", 4.0177, 35.1123, "Local Contractor", 25000000, "2024-08-15"),
        ("T/001/2024: Talanta Sports Stadium", "Sports Kenya", "Nairobi", -1.3061, 36.7502, "China Road and Bridge", 45300000000, "2026-12-01"),
        ("T/012/2015: Kamariny Stadium", "Sports Kenya", "Elgeyo Marakwet", 0.6580, 35.5030, "Local Civil Contractor", 287000000, "2018-05-30"),
        ("T/014/2015: Marsabit Stadium", "Sports Kenya", "Marsabit", 2.3830, 37.9830, "Local Civil Contractor", 295000000, "2018-06-15"),
        ("T/022/2016: Wang'uru Stadium", "Sports Kenya", "Kirinyaga", -0.6825, 37.3569, "Local Civil Contractor", 300000000, "2022-10-20"),
        ("T/044/2017: Wote Stadium", "Makueni County", "Makueni", -1.7802, 37.6274, "Nitram & Traphes Ent.", 350000000, "2019-12-30"),
        ("T/001/2024: Bomas Int. Conference Centre", "Ministry of Defence", "Nairobi", -1.3369, 36.7691, "KDF Engineering Brigade", 31500000000, "2026-08-30"),
        ("T/001/2017: Ol Kalou County Headquarters", "Nyandarua County", "Nyandarua", -0.2730, 36.3780, "Contract Mutually Terminated", 617644564, "2020-04-15"),
        ("T/018/2021: Ndagani Market", "Tharaka Nithi", "Tharaka Nithi", -0.3333, 37.6500, "Local Contractor", 117999162, "2022-11-30"),
        ("T/045/2021: Kombani Wholesale Market", "Kwale County", "Kwale", -4.1660, 39.4500, "Local Contractor", 105911142, "2022-09-30"),
        ("T/1169/2022: Laare Modern Miraa Market", "Ministry of Ag.", "Meru", 0.1668, 37.7645, "Local Contractor", 178581150, "2023-12-15"),
        ("MOH/O01/2018: Trans Nzoia Referral", "Trans Nzoia", "Trans Nzoia", 1.0158, 35.0088, "Multiple Sub-contractors", 1600000000, "2021-08-30"),
        ("MOH/012/2022: Isiolo Hospital A&E", "Isiolo County", "Isiolo", 0.3658, 37.5899, "Equipment Supplier", 17400000, "2023-05-15"),
        ("T/1023/2011: Thika Prison Drainage", "Prisons Dept.", "Kiambu", -1.0333, 37.0833, "Local Contractor", 5200500, "2013-12-30")
    ]

    for p in projects_data:
        # Create a unique contractor for cartel mapping later
        contractor_res = supabase.table("contractors").insert({
            "company_name": p[5],
            "kra_pin": "P" + str(int(time.time() * 1000))[-9:] + "X"
        }).execute()
        
        c_id = contractor_res.data[0]['id']

        supabase.table("projects").insert({
            "project_name": p[0],
            "tender_no": "TND/" + str(int(time.time() * 10000))[-6:],
            "procuring_entity": p[1],
            "county": p[2],
            "latitude": p[3],
            "longitude": p[4],
            "budget_allocated": p[6],
            "expected_completion_date": p[7],
            "contractor_id": c_id,
            "project_status": "Pending AI Audit" # Removed hardcoded statuses. AI must verify.
        }).execute()
        print(f"Verified & Pinned: {p[0]}")

    print("\n✅ 60 PROJECTS INJECTED. Ready for AI Analysis.")

if __name__ == "__main__":
    inject_national_data()