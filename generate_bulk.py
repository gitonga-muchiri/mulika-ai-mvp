from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import random

# DATABASE OF 10 PROJECTS (5 Ghost, 5 Real)
projects = [
    # GHOST PROJECTS (Red Flags)
    {"name": "Rumuruti Feeder Road", "budget": "KES 120M", "lat": 0.5186, "lon": 36.6578, "ward": "Rumuruti", "type": "GHOST"},
    {"name": "Wajir Water Pan", "budget": "KES 45M", "lat": 1.7471, "lon": 40.0573, "ward": "Wajir East", "type": "GHOST"},
    {"name": "Turkana Irrigation Scheme", "budget": "KES 80M", "lat": 3.1167, "lon": 35.6000, "ward": "Lodwar", "type": "GHOST"},
    {"name": "Kilifi Youth Center", "budget": "KES 30M", "lat": -3.6333, "lon": 39.8500, "ward": "Kilifi North", "type": "GHOST"},
    {"name": "Marsabit Solar Grid", "budget": "KES 200M", "lat": 2.3333, "lon": 37.9833, "ward": "Marsabit Central", "type": "GHOST"},
    
    # REAL PROJECTS (Green Flags - Nairobi/Mombasa)
    {"name": "Nairobi Expressway Exit", "budget": "KES 500M", "lat": -1.3622, "lon": 36.9317, "ward": "Mlolongo", "type": "REAL"},
    {"name": "Thika Superhighway Maintenance", "budget": "KES 50M", "lat": -1.2667, "lon": 36.8333, "ward": "Ruaraka", "type": "REAL"},
    {"name": "Mombasa Port Berth 19", "budget": "KES 1.2B", "lat": -4.0435, "lon": 39.6682, "ward": "Likoni", "type": "REAL"},
    {"name": "Kisumu Port Refurb", "budget": "KES 300M", "lat": -0.1000, "lon": 34.7500, "ward": "Kisumu Central", "type": "REAL"},
    {"name": "Konza City Data Center", "budget": "KES 800M", "lat": -1.6961, "lon": 37.1852, "ward": "Konza", "type": "REAL"}
]

def create_pdf(p):
    filename = f"Tender_{p['name'].replace(' ', '_')}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "REPUBLIC OF KENYA - TENDER NOTICE")
    c.line(50, 740, 500, 740)
    
    # Body
    c.setFont("Helvetica", 12)
    c.drawString(50, 700, f"TENDER NOTICE: {p['name']}")
    c.drawString(50, 680, f"Budget Allocation: {p['budget']}")
    c.drawString(50, 660, f"Ward: {p['ward']}")
    c.drawString(50, 640, "Contractor: MULTI-SCOPE CONSTRUCTION LTD")
    
    # Hidden Data
    c.drawString(50, 600, "SITE GEOLOCATION:")
    c.drawString(50, 580, f"Latitude: {p['lat']}")
    c.drawString(50, 560, f"Longitude: {p['lon']}")
    
    c.save()
    print(f"Generated: {filename}")

if __name__ == "__main__":
    for p in projects:
        create_pdf(p)