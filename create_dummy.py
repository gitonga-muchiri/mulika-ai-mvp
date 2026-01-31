from reportlab.pdfgen import canvas

def create_fake_tender():
    c = canvas.Canvas("sample_tender.pdf")
    c.drawString(100, 800, "REPUBLIC OF KENYA")
    c.drawString(100, 780, "MINISTRY OF ROADS AND TRANSPORT")
    c.drawString(100, 750, "TENDER NOTICE: 2026/001")
    c.drawString(100, 700, "Project Title: Construction of Karatina-Nyeri Feeder Road")
    c.drawString(100, 680, "Location: Nyeri County")
    c.drawString(100, 660, "Budget: KES 50,000,000")
    c.drawString(100, 640, "Contractor: MegaBuild Ltd")
    c.drawString(100, 620, "Expected Completion: 15KM of Tarmac")
    c.save()
    print("sample_tender.pdf created!")

if __name__ == "__main__":
    create_fake_tender()