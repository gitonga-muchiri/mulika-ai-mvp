# 🌍 Mulika AI: The Digital Auditor

**"Trust, but Verify."**

Mulika AI is an autonomous oversight system designed to bridge the gap between government budget allocation and physical infrastructure reality in Kenya.

## 🚀 Features (MVP)
* **Engine A (Document Intelligence):** Extracts project location and budget from Tender PDFs.
* **Engine B (Satellite Verification):** Fetches real-time Sentinel-2 satellite imagery of project sites.
* **Engine C (Red Flag Logic):** Uses Computer Vision to compare "Before" and "After" images.
    * *Result:* Automatically detects if ground disturbance (construction) matches the reported budget.
* **Interface:** Fully functional **WhatsApp Chatbot** for citizen access.

## 🛠️ Technology Stack
* **Backend:** Python (Flask)
* **Satellite Data:** Sentinel Hub API (Copernicus Data)
* **Computer Vision:** OpenCV & NumPy
* **Frontend:** Twilio API (WhatsApp)

## 📸 Usage
1.  User sends `Audit [Project Name]` to the bot.
2.  System analyzes the location.
3.  System returns a **RED FLAG** or **GREEN FLAG** verdict based on ground truth.
