from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# --- 50 REAL PROJECTS ---
# Format: (Name, Budget, Contractor, Lat, Lon, Location_Name)
# NOTE: We removed the "Real/Ghost" tag. The system doesn't know anymore.
PROJECT_DATA = [
    ("Nairobi Expressway Exit", "KES 800M", "CRBC", -1.3622, 36.9317, "Mlolongo"),
    ("Thiba Dam Project", "KES 8.2B", "Strabag", -0.5325, 37.3367, "Rukenya"),
    ("Makupa Bridge", "KES 4.5B", "CCCC", -4.0300, 39.6500, "Mombasa"),
    ("Konza City Data Center", "KES 40B", "Konza Auth", -1.6961, 37.1852, "Konza"),
    ("Dongo Kundu Bypass", "KES 28B", "Fujita", -4.0620, 39.5800, "Likoni"),
    ("Arror Dam Project", "KES 63B", "CMC Di Ravenna", 0.9081, 35.6669, "Elgeyo"),
    ("Kimwarer Dam", "KES 22B", "CMC Di Ravenna", 0.4167, 35.6333, "Keiyo"),
    ("Itare Dam Water Supply", "KES 38B", "CMC Di Ravenna", -0.5167, 35.7333, "Kuresoi"),
    ("Galana Kulalu Farm", "KES 7B", "Green Arava", -3.0833, 39.5000, "Tana"),
    ("Wote Stadium", "KES 350M", "Traphes Ent", -1.7802, 37.6275, "Makueni"),
    ("Likoni Floating Bridge", "KES 1.9B", "CRBC", -4.0753, 39.6644, "Likoni"),
    ("GTC Nairobi Complex", "KES 15B", "Avic International", -1.2721, 36.8122, "Westlands"),
    ("Kibwezi-Kitui Road", "KES 18B", "Sinohydro Corp", -1.3500, 38.0167, "Kitui South"),
    ("Kenol-Sagana-Marua Road", "KES 16B", "Wu Yi Company", -0.7000, 37.1500, "Muranga"),
    ("Nairobi SGR Terminus", "KES 32B", "CRBC", -1.3501, 36.9328, "Syokimau"),
    ("Suswa SGR Station", "KES 4.5B", "CCCC", -1.0833, 36.3667, "Narok"),
    ("Ngong Road Expansion", "KES 2.3B", "World Kaihatsu", -1.3000, 36.7500, "Dagoretti"),
    ("Eastern Bypass Expansion", "KES 12B", "CCCC", -1.2333, 36.9500, "Embakasi"),
    ("Western Bypass", "KES 17B", "CRBC", -1.2167, 36.7667, "Kiambu"),
    ("Kamariny Stadium", "KES 287M", "Funan Construction", 0.6498, 35.5076, "Iten"),
    ("Ruringu Stadium", "KES 200M", "Benisa Ltd", -0.4244, 36.9536, "Nyeri"),
    ("Karatu Stadium", "KES 150M", "Smith & Gold", -1.0500, 36.9000, "Gatundu"),
    ("Koru-Soin Dam", "KES 20B", "China Gezhouba", -0.1833, 35.2500, "Kisumu"),
    ("Lake Turkana Transmission", "KES 10B", "Isolux Corsan", 2.5000, 36.8000, "Loiyangalani"),
    ("Lower Kuja Irrigation", "KES 400M", "NIB", -0.8167, 34.4000, "Migori"),
    ("Tatu City Infrastructure", "KES 5B", "Rendeavour", -1.1333, 36.9167, "Ruaka"),
    ("Mama Ngina Waterfront", "KES 460M", "Suhufi Agencies", -4.0734, 39.6784, "Mombasa"),
    ("Kisumu Port Refurb", "KES 3B", "Kenya Navy", -0.1061, 34.7432, "Kisumu"),
    ("Uhuru Gardens Museum", "KES 600M", "KDF Projects", -1.3321, 36.7997, "Langata"),
    ("Ruiru Sewerage Plant", "KES 1.1B", "Athi Water", -1.1610, 36.9920, "Ruiru"),
    ("Dandora Stadium", "KES 350M", "Dandora Contractors", -1.2486, 36.9031, "Dandora"),
    ("Kinoru Stadium Meru", "KES 900M", "Toddy Civil Works", 0.0463, 37.6559, "Meru"),
    ("Ulinzi Sports Complex", "KES 1B", "KDF Engineering", -1.2990, 36.7860, "Langata"),
    ("Siaya Referral Hospital", "KES 400M", "Siaya County", 0.0620, 34.2882, "Siaya"),
    ("Nakuru Market Complex", "KES 600M", "Nakuru County", -0.2853, 36.0682, "Nakuru"),
    ("Bura Irrigation Gravity", "KES 1.2B", "IVRCL Infrastructure", -1.1667, 39.8333, "Tana River"),
    ("Tot-Kolowa Road", "KES 200M", "Kura", 1.0500, 35.7000, "Marakwet"),
    ("Kapenguria-Makutano Road", "KES 150M", "KeRRA", 1.2333, 35.1167, "West Pokot"),
    ("Mitihani House South C", "KES 2B", "KNEC", -1.3210, 36.8300, "Nairobi"),
    ("Kachibora-Kapcherop Road", "KES 300M", "TransNzoia Works", 0.9833, 35.3333, "Trans Nzoia"),
    ("Ahero Interchange Stalled", "KES 1B", "KenHA", -0.1667, 34.9167, "Kisumu"),
    ("Moi Uni Pension Tower", "KES 2.5B", "Moi University", 0.5167, 35.2833, "Eldoret"),
    ("Nyeri Science Park", "KES 800M", "Dedan Kimathi Uni", -0.3950, 36.9630, "Nyeri"),
    ("Kakamega Referral Hosp", "KES 3B", "Kakamega County", 0.2833, 34.7500, "Kakamega"),
    ("Ramisi-Shimoni Road", "KES 500M", "Kwale Works", -4.6000, 39.3833, "Kwale"),
    ("Chuka Stadium", "KES 250M", "Tharaka Nithi Govt", -0.3333, 37.6500, "Chuka")
]

# EXTEND TO 50
FULL_LIST = PROJECT_DATA + PROJECT_DATA[:5]

def create_tender_pdf(filename, project, budget, contractor, lat, lon, ward):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 700, f"PROJECT: {project}")
    c.drawString(50, 680, f"BUDGET: {budget}")
    c.drawString(50, 660, f"CONTRACTOR: {contractor}")
    c.drawString(50, 640, f"LOCATION: {ward}")
    
    # Hidden Data (Only Coordinates, NO STATUS)
    c.drawString(50, 600, f"LAT: {lat}")
    c.drawString(50, 580, f"LON: {lon}")
    
    c.save()
    print(f"Generated: {filename}")

if __name__ == "__main__":
    if not os.path.exists("tender_docs"): os.makedirs("tender_docs")
    for i, p in enumerate(FULL_LIST):
        safe_name = p[0].replace(" ", "_").replace("/", "-")
        fname = f"tender_docs/Tender_{i+1}_{safe_name}.pdf"
        create_tender_pdf(fname, p[0], p[1], p[2], p[3], p[4], p[5])