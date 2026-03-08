from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_tender_pdf(filename, project_title, budget, lat, lon):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "REPUBLIC OF KENYA")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 70, "MINISTRY OF ROADS & INFRASTRUCTURE")
    c.line(50, height - 80, 550, height - 80)

    # Tender Details
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 120, f"TENDER NOTICE: {project_title}")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 150, f"Budget Allocation: {budget}")
    c.drawString(50, height - 170, "Contractor: Zenith Paving Solutions Ltd")
    c.drawString(50, height - 190, "Scope: Tarmacking and Drainage Works (15KM)")
    c.drawString(50, height - 210, "Start Date: 10 Jan 2023")
    c.drawString(50, height - 230, "Completion Date: 10 Jan 2024")

    # HIDDEN LOCATION DATA (The AI looks for this)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 270, "SITE LOCATION DATA:")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 290, f"Latitude: {lat}")
    c.drawString(50, height - 310, f"Longitude: {lon}")
    c.drawString(50, height - 330, "Ward: Rumuruti Township")

    c.save()
    print(f"✅ Generated: {filename}")

if __name__ == "__main__":
    # Create the GHOST PROJECT (Rumuruti - Dry area, no road)
    create_tender_pdf("tender_ghost_road.pdf", 
                      "Rumuruti-Maralal Feeder Road", 
                      "KES 120,000,000", 
                      0.5186, 36.6578)