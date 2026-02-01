import streamlit as st
import pandas as pd
import os
import datetime
import time
from engine_e import run_batch_processor
from engine_a import extract_tender_details
from engine_c import run_full_audit
from engine_nlp import process_whatsapp_query
from database_manager import build_central_database

# --- CONFIGURATION ---
st.set_page_config(page_title="Mulika AI Platform", page_icon="🌍", layout="wide")

if 'current_view' not in st.session_state: st.session_state.current_view = "Home"
if 'audit_target' not in st.session_state: st.session_state.audit_target = None
if 'chat_history' not in st.session_state: st.session_state.chat_history = []

def navigate_to(page_name):
    st.session_state.current_view = page_name
    st.rerun()

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .mission-card { background-color: #1e2130; border: 1px solid #30334e; border-radius: 10px; padding: 20px; text-align: center; }
    .mission-card:hover { transform: scale(1.02); border-color: #4CAF50; }
    
    /* TUCHAT STYLING */
    .chat-container {
        background-color: #111b21; /* WhatsApp Dark BG */
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #30334e;
    }
    .chat-bubble-user {
        background-color: #005c4b;
        color: white;
        padding: 12px 18px;
        border-radius: 12px 12px 0px 12px;
        text-align: right;
        max-width: 70%;
        margin-left: auto;
        margin-bottom: 8px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.2);
    }
    .chat-bubble-bot {
        background-color: #202c33;
        color: white;
        padding: 12px 18px;
        border-radius: 12px 12px 12px 0px;
        text-align: left;
        max-width: 80%;
        margin-bottom: 8px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/satellite.png", width=70)
    st.title("MULIKA AI 🛡️")
    st.markdown("**System Level:** Enterprise")
    st.divider()
    menu = ["Home", "Live Operations", "Batch Report", "Tuchat", "Blacklist Registry"]
    try: ix = menu.index(st.session_state.current_view)
    except: ix = 0
    sel = st.radio("Navigation:", menu, index=ix)
    if sel != st.session_state.current_view: st.session_state.current_view = sel; st.rerun()
    st.divider(); st.info("Status: 🟢 System Online")

# HOME
if st.session_state.current_view == "Home":
    st.title("🌍 MULIKA AI: National Infrastructure Monitor")
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.markdown("""<div class="mission-card"><h3>📡 Live Operations</h3><p>Single Target Verification</p></div>""", unsafe_allow_html=True)
        if st.button("🚀 LAUNCH LIVE"): navigate_to("Live Operations")
    with c2:
        st.markdown("""<div class="mission-card"><h3>🏭 Batch Report</h3><p>National Scan Engine</p></div>""", unsafe_allow_html=True)
        if st.button("⏳ ENTER WAR ROOM"): navigate_to("Batch Report")
    with c3:
        st.markdown("""<div class="mission-card"><h3>📱 Tuchat</h3><p>Citizen Reporting Tool</p></div>""", unsafe_allow_html=True)
        if st.button("💬 OPEN CHAT"): navigate_to("Tuchat")

# LIVE OPS
elif st.session_state.current_view == "Live Operations":
    st.title("📡 Live Operations")
    if os.path.exists("central_database.csv"):
        try:
            df = pd.read_csv("central_database.csv")
            if 'Project' in df.columns:
                proj_list = df['Project'].tolist()
                with st.expander("🔍 Search Database", expanded=True):
                    sel = st.selectbox("Find Project:", ["Select..."] + proj_list)
                    if sel != "Select...":
                        rec = df[df['Project'] == sel].iloc[0]
                        st.session_state.audit_target = {
                            "name": rec.get('Project'), "budget": rec.get('Budget'),
                            "loc": rec.get('Location'), "lat": rec.get('Latitude'),
                            "lon": rec.get('Longitude')
                        }
                        st.rerun()
        except: pass

    tgt = st.session_state.audit_target if st.session_state.audit_target else {"name": "None", "budget": "-", "loc": "-", "lat": 0.51, "lon": 36.6}
    c1, c2, c3 = st.columns(3)
    c1.metric("Project", tgt['name']); c2.metric("Budget", tgt['budget']); c3.metric("Location", tgt['loc'])
    st.subheader("📍 Mission Control")
    ca, cb = st.columns(2)
    with ca: lat = st.number_input("Lat", value=float(tgt['lat']), format="%.4f"); lon = st.number_input("Lon", value=float(tgt['lon']), format="%.4f")
    with cb: d1 = st.date_input("Start", datetime.date(2023,1,1)); d2 = st.date_input("End", datetime.date(2024,1,1))
    
    if st.button("🚀 LAUNCH AUDIT", type="primary"):
        with st.spinner("Connecting..."):
            verdict, score, i1, i2 = run_full_audit(lat, lon, "Live", str(d1), str(d2))
        if verdict == "RED FLAG": st.error(f"🚨 RED FLAG ({score:.1f}%)")
        else: st.success(f"✅ GREEN FLAG ({score:.1f}%)")
        ic1, ic2 = st.columns(2)
        if i1: ic1.image(i1, caption="Historical Baseline")
        if i2: ic2.image(i2, caption="Current Feed")

# BATCH
elif st.session_state.current_view == "Batch Report":
    st.title("🏭 Batch Report")
    if st.button("🔴 START BATCH"):
        with st.spinner("Scanning..."): run_batch_processor()
        st.success("Done!"); time.sleep(1); st.rerun()
    if os.path.exists("batch_audit_results.csv"):
        df = pd.read_csv("batch_audit_results.csv"); df.index += 1
        st.dataframe(df[['Project', 'Verdict', 'Score']], use_container_width=True)
        st.subheader("Gallery")
        for i, row in df.iterrows():
            with st.expander(f"{row['Project']} ({row['Verdict']})"):
                c1, c2 = st.columns(2)
                try: c1.image(row['Img_Before']); c2.image(row['Img_After'])
                except: st.warning("Image missing")

# TUCHAT (PURE CHAT - NO WHATSAPP FEATURES)
elif st.session_state.current_view == "Tuchat":
    st.title("📱 Tuchat: Citizen Interface")
    
    chat_container = st.container(height=500)
    
    if not st.session_state.chat_history:
        st.session_state.chat_history.append({"role": "bot", "text": "👋 Jambo! Welcome to Tuchat. \nAsk me about any project, e.g., 'Check Ruringu Stadium'."})

    with chat_container:
        for msg in st.session_state.chat_history:
            role_class = "chat-bubble-user" if msg['role'] == "user" else "chat-bubble-bot"
            st.markdown(f"""<div class="{role_class}">{msg['text']}</div>""", unsafe_allow_html=True)
            
            if msg.get('has_media'):
                c1, c2 = st.columns(2)
                c1.image(msg['img_before'], caption="Baseline", use_container_width=True)
                c2.image(msg['img_after'], caption="Current", use_container_width=True)

    with st.form("chat_form", clear_on_submit=True):
        col_in, col_btn = st.columns([6, 1])
        txt = col_in.text_input("Type your message...", placeholder="Check Ruringu Stadium...")
        sub = col_btn.form_submit_button("➤")
        
        if sub and txt:
            st.session_state.chat_history.append({"role": "user", "text": txt})
            with st.spinner("Mulika AI is analyzing satellite data..."): 
                res = process_whatsapp_query(txt)
            
            bot_msg = {"role": "bot", "text": res['text'], "has_media": res['has_media']}
            if res['has_media']: 
                bot_msg['img_before'] = res['img_before']
                bot_msg['img_after'] = res['img_after']
            
            st.session_state.chat_history.append(bot_msg)
            st.rerun()

# BLACKLIST
elif st.session_state.current_view == "Blacklist Registry":
    st.title("⚖️ Blacklist Registry")
    if os.path.exists("contractor_blacklist.csv"): st.table(pd.read_csv("contractor_blacklist.csv"))
    else: st.info("Empty.")