import streamlit as st
import os
import datetime
from engine_a import extract_tender_details
from engine_c import run_full_audit

# --- CONFIGURATION ---
st.set_page_config(page_title="Mulika AI Dashboard", page_icon="🌍", layout="wide")

# --- STYLE (Dark Mode Govt Look) ---
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #262730;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.image("https://img.icons8.com/color/96/satellite-sending-signal.png", width=80)
st.sidebar.title("Mulika AI 🚀")
st.sidebar.success("System Online")

mode = st.sidebar.radio("Select Module:", ["New Audit Request", "View Satellite Archives", "System Settings"])

# --- MAIN PAGE ---
if mode == "New Audit Request":
    st.title("🌍 Mulika AI: National Infrastructure Auditor")

    # 1. UPLOAD
    st.header("📂 Step 1: Upload Tender Document")
    uploaded_file = st.file_uploader("Upload Tender PDF", type=["pdf"])

    if uploaded_file is not None:
        with open("temp_upload.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        with st.spinner("Reading Document..."):
            data = extract_tender_details("temp_upload.pdf")
        
        st.divider()
        col1, col2, col3 = st.columns(3)
        col1.metric("Project", data.get('name', 'Unknown'))
        col2.metric("Budget", data.get('budget', 'Unknown'))
        col3.metric("Location/Ward", data.get('location', 'Unknown'))
        
        # 2. MISSION CONTROL
        st.divider()
        st.subheader("📍 Step 2: Mission Control")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Confirm Coordinates:**")
            lat = st.number_input("Latitude", value=float(data.get('lat') or 0.5186), format="%.4f")
            lon = st.number_input("Longitude", value=float(data.get('lon') or 36.6578), format="%.4f")
        
        with c2:
            st.markdown("**Select Audit Timeframe:**")
            date_start = st.date_input("Start Date (Before)", datetime.date(2023, 1, 1))
            date_end = st.date_input("End Date (After)", datetime.date(2024, 1, 1))

        # 3. LAUNCH
        if st.button("🚀 LAUNCH SATELLITE AUDIT", type="primary"):
            st.divider()
            st.subheader("🛰️ Step 3: Satellite Verification Report")
            
            s_date = date_start.strftime("%Y-%m-%d")
            e_date = date_end.strftime("%Y-%m-%d")
            
            with st.spinner(f"Initiating Cloud Buster Protocol ({s_date} vs {e_date})..."):
                verdict, score, img1, img2 = run_full_audit(lat, lon, "Dashboard_Audit", s_date, e_date)
            
            col_a, col_b = st.columns(2)
            
            # FIXED: Removed 'use_column_width' warning by using 'use_container_width'
            if img1:
                col_a.image(img1, caption=f"📅 Baseline: {s_date}", use_container_width=True)
            else:
                col_a.error("Baseline Image Unavailable (Data Gap).")
                
            if img2:
                col_b.image(img2, caption=f"📅 Current: {e_date}", use_container_width=True)
            else:
                col_b.error("Current Image Unavailable (Data Gap).")
                
            st.divider()
            if verdict == "RED FLAG":
                st.error(f"🚨 **VERDICT: {verdict} DETECTED**")
                st.warning(f"**Evidence:** Only {score:.2f}% ground disturbance detected. Matches 'Ghost Project' profile.")
            elif verdict == "GREEN FLAG":
                st.success(f"✅ **VERDICT: {verdict}**")
                st.info(f"**Evidence:** Significant ground disturbance ({score:.2f}%) detected, indicating active construction.")
            else:
                st.error("System Error: Satellite connection failed.")

elif mode == "View Satellite Archives":
    st.title("🛰️ Satellite Archives")
    st.info("Archive module is under construction.")

elif mode == "System Settings":
    st.title("⚙️ System Settings")
    st.write("API Status: Connected")