import pandas as pd
import random
import re
import numpy as np
import google.generativeai as genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from engine_c import run_full_audit

# --- 🔑 CONFIGURATION ---
GOOGLE_API_KEY = "" # Paste your key if you have it

# --- 🧠 CUSTOM STOP WORDS (Sheng + Swahili + English Fillers) ---
# These words will be mathematically ignored to find the signal in the noise.
CUSTOM_STOP_WORDS = [
    # English
    "the", "is", "at", "which", "on", "check", "verify", "audit", "show", "me",
    "tell", "about", "status", "project", "dam", "road", "stadium", "please", "help",
    "monitor", "report", "update", "hi", "hello", "hey",
    # Swahili
    "na", "je", "ni", "wa", "kwa", "katika", "za", "la", "ya", "nani", "gani",
    "iko", "wapi", "kuna", "hii", "hayo", "huyo", "yule", "ile", "kufanya",
    # Sheng / Slang
    "niaje", "sasa", "rada", "manze", "jo", "ati", "aki", "ebu", "cheki", "lete",
    "form", "kuna", "endaje", "vipi", "uko", "aje"
]

# --- PERSONA TEMPLATES ---
GREETINGS_SHENG = ["Jambo!", "Sasa!", "Niaje!", "Mambo!", "Oya!", "Radha!"]
VERDICTS_SHENG_GREEN = ["✅ *IKO SAWA!* Hii project inasonga.", "👍 *BIG UP:* Contractor ako site anachapa kazi."]
VERDICTS_SHENG_RED = ["🚨 *IMEBUMA!* Hii project ni hewa tupu.", "⚠️ *RED FLAG:* Satellite haioni kitu. Pesa imekunywa maji."]

def clean_text(text):
    """
    Standardizes text for the Vectorizer.
    """
    if not isinstance(text, str): return ""
    # Lowercase and remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    return text.strip()

def find_best_match_vectorized(user_query, db_path="central_database.csv"):
    """
    Uses TF-IDF Vectorization and Cosine Similarity to find the best match.
    This understands context better than simple keyword matching.
    """
    try:
        df = pd.read_csv(db_path)
        
        # 1. Prepare the "Corpus" (The Searchable Data)
        # We combine Project Name, Location, and Contractor into one searchable field
        df['Search_Corpus'] = df['Project'].fillna('') + " " + df['Location'].fillna('') + " " + df['Contractor'].fillna('')
        df['Search_Corpus'] = df['Search_Corpus'].apply(clean_text)
        
        cleaned_query = clean_text(user_query)
        
        # 2. Vectorize (Convert Text to Math)
        # TfidfVectorizer automatically weighs down common words (stop words)
        # and weighs up unique words (like "Kimwarer" or "Konza")
        vectorizer = TfidfVectorizer(stop_words=CUSTOM_STOP_WORDS)
        
        # Fit the model on our database + the user query (to ensure vocabulary match)
        corpus_list = df['Search_Corpus'].tolist()
        corpus_list.append(cleaned_query) # Add query to end temporarily
        
        tfidf_matrix = vectorizer.fit_transform(corpus_list)
        
        # 3. Calculate Similarity
        # Compare the Query (last item) against all Projects (items 0 to N)
        query_vec = tfidf_matrix[-1] 
        database_vecs = tfidf_matrix[:-1]
        
        cosine_scores = cosine_similarity(query_vec, database_vecs).flatten()
        
        # 4. Find the Winner
        best_score_index = cosine_scores.argmax()
        best_score = cosine_scores[best_score_index]
        
        print(f"   🔍 Query: '{cleaned_query}' | Best Match: '{df.iloc[best_score_index]['Project']}' | Score: {best_score:.4f}")
        
        # Threshold: If similarity is too low (e.g. < 0.15), it's probably garbage
        if best_score > 0.15:
            return df.iloc[best_score_index]
        else:
            return None
            
    except Exception as e:
        print(f"Vector Search Error: {e}")
        return None

def generate_gemini_response(match, verdict, score, user_text):
    """
    Uses Google Gemini for the conversation, or falls back to templates.
    """
    try:
        if not GOOGLE_API_KEY:
            return generate_manual_response(match, verdict, score)

        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = f"""
        Act as 'Mulika AI', a street-smart Kenyan infrastructure auditor. You speak in a mix of English and Nairobi Sheng.
        
        User Query: "{user_text}"
        
        Audit Data:
        - Project: {match['Project']}
        - Location: {match['Location']}
        - Contractor: {match['Contractor']}
        - Budget: {match['Budget']}
        - Verdict: {verdict}
        - Score: {score:.1f}%
        
        Instructions:
        1. Answer directly.
        2. Be brief (max 3 sentences).
        3. If RED FLAG: Use slang like "imebuma", "kula pesa", "hewa".
        4. If GREEN FLAG: Use slang like "iko chonjo", "form ni gani".
        5. Format using WhatsApp bolding (*text*).
        """
        
        response = model.generate_content(prompt)
        return response.text

    except:
        return generate_manual_response(match, verdict, score)

def generate_manual_response(match, verdict, score):
    greeting = random.choice(GREETINGS_SHENG)
    
    if verdict == "RED FLAG":
        status = random.choice(VERDICTS_SHENG_RED)
        icon = "❌"
    else:
        status = random.choice(VERDICTS_SHENG_GREEN)
        icon = "🟢"
    
    return f"""{greeting} *Mulika AI Report* 🛰️

*Project:* {match['Project']}
*Loc:* {match['Location']}
*Budget:* {match['Budget']}

*Verdict:* {icon} {verdict}
*Score:* {score:.1f}%

{status}"""

def process_whatsapp_query(user_text):
    print(f"🤖 Brain Processing: '{user_text}'")
    
    # USE THE ROBUST VECTOR SEARCH
    match = find_best_match_vectorized(user_text)
    
    if match is None:
        # Fallback: Try a super loose check or return error
        return {
            "text": "❌ *Zii!* Sijapata hiyo project kwa database.\nTry using the specific name, e.g., _'Check Arror Dam'_.",
            "has_media": False
        }
    
    # Run the Audit
    lat = match['Latitude']
    lon = match['Longitude']
    verdict, score, img1, img2 = run_full_audit(lat, lon, "Chat", "2023-01-01", "2024-01-01")
    
    # Generate Response
    response_text = generate_gemini_response(match, verdict, score, user_text)
    
    return {
        "text": response_text,
        "has_media": True,
        "img_before": img1,
        "img_after": img2
    }