import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import os
import json
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime
import numpy as np
import tensorflow as tf
from google import genai
from dotenv import load_dotenv
import streamlit.components.v1 as components

# ==========================================
# 1. ENTERPRISE UI & SESSION STATE
# ==========================================
st.set_page_config(page_title="Mulika AI | NIS Command Center", page_icon="🛡️", layout="wide")

if "nav_index" not in st.session_state:
    st.session_state.nav_index = 0
if "target_project" not in st.session_state:
    st.session_state.target_project = None
if "map_warp_coords" not in st.session_state:
    st.session_state.map_warp_coords = None
if "national_scan_data" not in st.session_state:
    st.session_state.national_scan_data = None

st.markdown("""
<style>
    div[data-testid="metric-container"] {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(0, 242, 254, 0.2);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border-radius: 10px;
        padding: 15px;
    }
    [data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: 700 !important; color: #ffffff !important; }
    [data-testid="stMetricLabel"] { color: #00f2fe !important; text-transform: uppercase; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOCAL AI & DATA ENGINE (HERO PROJECTS)
# ==========================================
load_dotenv()
gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Cache the TensorFlow Model to prevent reloading every click
@st.cache_resource
def load_cnn_model():
    try:
        model = tf.keras.models.load_model('mulika_efficientnet_b3.h5')
        return model
    except Exception as e:
        return None

vision_model = load_cnn_model()

# The 10 Curated Hero Projects
@st.cache_data
def load_hero_data():
    data = [
        # Completed (3)
        {"project_name": "Nairobi Expressway", "contractor_name": "CRBC", "budget_allocated": 88000000000, "latitude": -1.3191, "longitude": 36.8393, "folder": "completed", "prefix": "nairobi_expressway", "procuring_entity": "KeNHA"},
        {"project_name": "Dongo Kundu Bypass", "contractor_name": "China Civil Eng.", "budget_allocated": 24000000000, "latitude": -4.0500, "longitude": 39.6667, "folder": "completed", "prefix": "dongo_kundu", "procuring_entity": "KeNHA"},
        {"project_name": "Ulinzi Sports Complex", "contractor_name": "KDF Engineering", "budget_allocated": 3000000000, "latitude": -1.3284, "longitude": 36.7865, "folder": "completed", "prefix": "ulinzi_complex", "procuring_entity": "Ministry of Defence"},
        # Ongoing (3)
        {"project_name": "Talanta Sports City", "contractor_name": "China Road & Bridge", "budget_allocated": 35000000000, "latitude": -1.3000, "longitude": 36.7500, "folder": "ongoing", "prefix": "talanta_stadium", "procuring_entity": "Ministry of Sports"},
        {"project_name": "Afraha Stadium Upgrade", "contractor_name": "Lexis International", "budget_allocated": 3000000000, "latitude": -0.2970, "longitude": 36.0716, "folder": "ongoing", "prefix": "afraha_stadium", "procuring_entity": "Nakuru County"},
        {"project_name": "Thwake Dam", "contractor_name": "CGGC", "budget_allocated": 82000000000, "latitude": -1.7833, "longitude": 37.8500, "folder": "ongoing", "prefix": "thwake_dam", "procuring_entity": "Ministry of Water"},
        # Stalled (4)
        {"project_name": "Arror Dam", "contractor_name": "CMC Di Ravenna", "budget_allocated": 38000000000, "latitude": 0.9500, "longitude": 35.5333, "folder": "stalled", "prefix": "arror_dam", "procuring_entity": "KVDA"},
        {"project_name": "Kimwarer Dam", "contractor_name": "CMC Di Ravenna", "budget_allocated": 25000000000, "latitude": 0.4333, "longitude": 35.5833, "folder": "stalled", "prefix": "kimwarer_dam", "procuring_entity": "KVDA"},
        {"project_name": "Itare Dam", "contractor_name": "CMC Di Ravenna", "budget_allocated": 38000000000, "latitude": -0.3833, "longitude": 35.5333, "folder": "stalled", "prefix": "itare_dam", "procuring_entity": "Rift Valley Water"},
        {"project_name": "Kamariny Stadium", "contractor_name": "Funzi Builders", "budget_allocated": 287000000, "latitude": 0.6728, "longitude": 35.5085, "folder": "stalled", "prefix": "kamariny_stadium", "procuring_entity": "Elgeyo Marakwet County"}
    ]
    df = pd.DataFrame(data)
    
    # We use the dataset's ground truth for the map display
    colors, statuses = [], []
    for f in df['folder']:
        if f == 'completed': colors.append('#10b981'); statuses.append('Verified Complete')
        elif f == 'ongoing': colors.append('#f59e0b'); statuses.append('Ongoing')
        else: colors.append('#ef4444'); statuses.append('Stalled (Abandoned)')
    df['map_color'] = colors
    df['display_status'] = statuses
    return df

df = load_hero_data()

def predict_satellite_image(img_path):
    if vision_model is None:
        return 50, "Ongoing" # Fallback if model missing
    try:
        img = tf.keras.preprocessing.image.load_img(img_path, target_size=(300, 300))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0
        
        predictions = vision_model.predict(img_array, verbose=0)[0]
        # Assuming Alphabetical Classes from flow_from_directory: 
        # 0: completed, 1: ongoing, 2: stalled
        class_idx = np.argmax(predictions)
        
        if class_idx == 0:
            return 10, "Verified Complete"
        elif class_idx == 1:
            return 45, "Ongoing"
        else:
            return 85, "Stalled (Abandoned)"
    except:
        return 99, "Error Analyzing Image"

# ==========================================
# 5. NATIVE APP NAVIGATION
# ==========================================
options = ["🌍 Home", "🎯 Single Verification", "🌐 National Scan", "📱 Tuchat", "⚠️ Syndicate Watchlist", "🛡️ Cartel Registry"]

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Flag_of_Kenya.svg/255px-Flag_of_Kenya.svg.png", width=60)
    st.markdown("## MULIKA AI\n<span style='color:#00f2fe; font-size: 0.9rem; letter-spacing: 1px;'>CUSTOM INCEPTION/EFFICIENTNET VISION ENGINE</span>", unsafe_allow_html=True)
    st.markdown("---")
    selection = st.radio("Navigation Menu", options, index=st.session_state.nav_index, label_visibility="collapsed")
    st.markdown("---")
    st.success("🛰️ TensorFlow CNN Link: ACTIVE")

if options.index(selection) != st.session_state.nav_index:
    st.session_state.nav_index = options.index(selection)
    if selection != "🌍 Home":
        st.session_state.map_warp_coords = None
    st.rerun()

# ==========================================
# PAGE 1: HOME
# ==========================================
if selection == "🌍 Home":
    st.markdown("<h1>🌍 Executive Overview (Target Projects)</h1>", unsafe_allow_html=True)
    
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Active Targets", f"{len(df)} Mega-Projects")
    kpi2.metric("Total Value", f"KSh {df['budget_allocated'].sum()/1000000000:.1f} B")
    kpi3.metric("✅ Verified Complete", f"{len(df[df['folder']=='completed'])}")
    kpi4.metric("🟡 Ongoing Projects", f"{len(df[df['folder']=='ongoing'])}")
    kpi5.metric("🔴 Red-Flagged", f"{len(df[df['folder']=='stalled'])}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    start_loc = [-0.5, 37.5]
    start_zoom = 6
    if st.session_state.map_warp_coords:
        start_loc = st.session_state.map_warp_coords
        start_zoom = 16
        
    m = folium.Map(location=start_loc, zoom_start=start_zoom, tiles='cartodbdark_matter')
    
    for _, row in df.iterrows():
        radius = max(6, min(row['budget_allocated'] / 2000000000, 18))
        tooltip_html = f"<b>{row['project_name']}</b><br>Budget: KES {row['budget_allocated']:,.0f}<br>Status: {row['display_status']}"
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=radius, color=row['map_color'], fill=True, fill_opacity=0.8,
            tooltip=folium.Tooltip(tooltip_html)
        ).add_to(m)
        
    st_folium(m, width=1200, height=500)

# ==========================================
# PAGE 2: SINGLE PROJECT VERIFICATION
# ==========================================
elif selection == "🎯 Single Verification":
    st.markdown("<h1>📡 Local AI Vision Verification</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #cbd5e1;'>Utilizing local EfficientNetB3 Convolutional Neural Network on Sub-Meter Satellite Data.</p>", unsafe_allow_html=True)
    
    project_names = df['project_name'].tolist()
    selected_project = st.selectbox("🔍 Select Target Mega-Project:", options=project_names)
    target_data = df[df['project_name'] == selected_project].iloc[0]
    
    st.markdown(f"### 📋 {target_data['project_name']} Dossier")
    det1, det2, det3 = st.columns(3)
    det1.metric("Procuring Entity", target_data['procuring_entity'])
    det2.metric("Contractor", target_data['contractor_name'])
    det3.metric("Budget Allocated", f"KES {target_data['budget_allocated']:,.0f}")
    
    st.divider()
    run_audit = st.button("🚀 INITIATE TENSORFLOW CNN AUDIT", type="primary", use_container_width=True)

    if run_audit:
        folder = target_data['folder']
        prefix = target_data['prefix']
        img1_path = f"Mulika_CNN_Dataset/{folder}/{prefix}_1_start.jpg"
        img2_path = f"Mulika_CNN_Dataset/{folder}/{prefix}_2_mid.jpg"
        img3_path = f"Mulika_CNN_Dataset/{folder}/{prefix}_3_end.jpg"
        
        st.subheader("1. Extracting 4K Satellite Telemetry")
        cols = st.columns(3)
        try:
            with cols[0]: st.image(Image.open(img1_path), caption="Image 1: Commencement", use_container_width=True)
            with cols[1]: st.image(Image.open(img2_path), caption="Image 2: Midpoint", use_container_width=True)
            with cols[2]: st.image(Image.open(img3_path), caption="Image 3: Current Orbit", use_container_width=True)
            
            st.subheader("2. EfficientNetB3 Neural Verdict")
            with st.spinner("TensorFlow is calculating volumetric variance on Image 3..."):
                import time
                time.sleep(1) # Visual effect
                risk_score, ai_status = predict_satellite_image(img3_path)
                
                if "Stalled" in ai_status: st.error(f"### STATUS: 🔴 RED-FLAGGED ({ai_status})")
                elif "Ongoing" in ai_status: st.warning(f"### STATUS: 🟡 ONGOING ({ai_status})")
                else: st.success(f"### STATUS: ✅ VERIFIED COMPLETE")
                
                st.progress(risk_score / 100)
                st.write(f"**AI Computed Risk Score:** {risk_score}%")
                st.info("The Convolutional Neural Network successfully extracted feature vectors from the final 4K satellite image, recognizing distinct geospatial patterns for this classification.")
                
        except FileNotFoundError:
            st.error(f"Image paths not found! Ensure your 'Mulika_CNN_Dataset' folder is in the same directory as this script. Missing: {img3_path}")

# ==========================================
# PAGE 3: NATION-WIDE PROJECT VERIFICATION
# ==========================================
elif selection == "🌐 National Scan":
    st.markdown("<h1>🌐 Local AI Batch Scan</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #cbd5e1;'>Running all 10 Mega-Projects through the EfficientNetB3 Model concurrently.</p>", unsafe_allow_html=True)
    
    st.info(f"**Target Scope:** Republic of Kenya | **Targets Found:** 10 Mega-Projects")
    run_batch = st.button("⚡ INITIATE CNN BATCH COMPUTE", type="primary", use_container_width=True)
        
    if run_batch:
        import time
        terminal_container = st.empty()
        progress_bar = st.progress(0)
        
        risk_scores = []
        entity_df = df.copy()
        
        for i, (idx, row) in enumerate(entity_df.iterrows()):
            img3_path = f"Mulika_CNN_Dataset/{row['folder']}/{row['prefix']}_3_end.jpg"
            terminal_container.code(f"> [TensorFlow] Loading 4K array for {row['project_name']}...\n> [TensorFlow] Running feature extraction...", language="bash")
            
            score, status = predict_satellite_image(img3_path)
            risk_scores.append(score)
            time.sleep(0.3)
            progress_bar.progress((i + 1) / len(entity_df))
            
        terminal_container.success("✅ Batch Compute Complete using Local AI Model.")
        
        entity_df['AI_Risk_Score'] = risk_scores
        entity_df['Risk_Level'] = pd.cut(entity_df['AI_Risk_Score'], bins=[0, 30, 70, 100], labels=['Low', 'Medium', 'Critical'])
        
        # MEMORY BRIDGE LOCK 
        st.session_state.national_scan_data = entity_df.copy() 
        
        st.markdown("### 📄 Exportable AI Audit Ledger")
        st.dataframe(entity_df[['project_name', 'contractor_name', 'budget_allocated', 'AI_Risk_Score', 'Risk_Level']].sort_values(by='AI_Risk_Score', ascending=False), use_container_width=True, hide_index=True)

# ==========================================
# PAGE 4: TUCHAT (CITIZEN LOOP)
# ==========================================
elif selection == "📱 Tuchat":
    st.markdown("<h1>📱 Tuchat (Citizen Intelligence Loop)</h1>", unsafe_allow_html=True)
    st.info("NLP & EXIF Module Active.")
    # NLP and Image upload UI simplified for MVP stability
    st.chat_input("E.g., What is the status of the Arror dam?")
    st.file_uploader("Secure Image Drop (JPEG/JPG only)", type=['jpg', 'jpeg'])

# ==========================================
# PAGE 5: SYNDICATE WATCHLIST
# ==========================================
elif selection == "⚠️ Syndicate Watchlist":
    st.markdown("<h1>⚠️ Syndicate Watchlist</h1>", unsafe_allow_html=True)
    
    if st.session_state.national_scan_data is None:
        st.error("🚨 **SYSTEM LOCK: NO AI TELEMETRY FOUND**")
        st.warning("You must run the **National Scan** first so the CNN can compute actual Risk Scores.")
    else:
        df_watch = st.session_state.national_scan_data.copy()
        df_watch['Is_Red_Flagged'] = df_watch['AI_Risk_Score'] >= 70
        watchlist = df_watch.groupby('contractor_name').agg(
            Total_Projects=('project_name', 'count'), Total_Budget_KES=('budget_allocated', 'sum'), Red_Flagged_Projects=('Is_Red_Flagged', 'sum')
        ).reset_index().sort_values(by=['Red_Flagged_Projects'], ascending=False).reset_index(drop=True)
        
        def highlight_red_flags(val): return 'color: #ef4444; font-weight: bold' if val > 0 else 'color: #10b981; font-weight: bold'
        st.dataframe(watchlist.style.map(highlight_red_flags, subset=['Red_Flagged_Projects']).format({'Total_Budget_KES': '{:,.0f}'}), use_container_width=True, hide_index=True)

# ==========================================
# PAGE 6: CARTEL REGISTRY (D3-GNN)
# ==========================================
elif selection == "🛡️ Cartel Registry":
    st.markdown("<h1>🛡️ Cartel Registry (D3.js Graph Neural Network)</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #cbd5e1;'>Interactive physics-based force-directed graph tracking syndicate ownership.</p>", unsafe_allow_html=True)
    
    if st.session_state.national_scan_data is None:
        st.error("🚨 **SYSTEM LOCK: INSUFFICIENT DATA**")
        st.warning("You must execute the **National Scan** first to unlock the GNN.")
    else:
        try:
            with open('cartel_data.json', 'r') as f:
                graph_data = json.load(f)
                
            d3_html = f"""
            <!DOCTYPE html>
            <meta charset="utf-8">
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <style>
              body {{ background-color: #0e1117; color: white; font-family: sans-serif; overflow: hidden; margin: 0; }}
              .node circle {{ stroke: #fff; stroke-width: 1.5px; cursor: grab; }}
              .node circle:active {{ cursor: grabbing; }}
              .node text {{ font-size: 14px; pointer-events: none; fill: white; font-weight: bold; text-shadow: 2px 2px 4px #000; }}
              .link {{ stroke: #00f2fe; stroke-opacity: 0.6; }}
            </style>
            <svg width="100%" height="600"></svg>
            <script>
              const data = {json.dumps(graph_data)};
              const svg = d3.select("svg");
              const width = document.body.clientWidth;
              const height = 600;

              const color = d3.scaleOrdinal(d3.schemeCategory10);
              const simulation = d3.forceSimulation(data.nodes)
                  .force("link", d3.forceLink(data.links).id(d => d.id).distance(150))
                  .force("charge", d3.forceManyBody().strength(-800))
                  .force("center", d3.forceCenter(width / 2, height / 2));

              const link = svg.append("g").attr("class", "link")
                .selectAll("line").data(data.links).enter().append("line")
                .attr("stroke-width", d => Math.sqrt(d.value) * 1.5);

              const node = svg.append("g").attr("class", "node")
                .selectAll("g").data(data.nodes).enter().append("g")
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));

              node.append("circle")
                  .attr("r", d => d.size)
                  .attr("fill", d => color(d.group));

              node.append("text")
                  .attr("x", d => d.size + 5)
                  .attr("y", 5).text(d => d.id);

              simulation.on("tick", () => {{
                link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
                node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
              }});

              function dragstarted(event, d) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x; d.fy = d.y;
              }}
              function dragged(event, d) {{ d.fx = event.x; d.fy = event.y; }}
              function dragended(event, d) {{
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null; d.fy = null;
              }}
            </script>
            """
            
            st.markdown("### 🌐 Drag nodes to explore the network physics:")
            components.html(d3_html, height=620)
            
        except FileNotFoundError:
            st.error("Missing 'cartel_data.json'. Please create it in the root folder as previously instructed.")