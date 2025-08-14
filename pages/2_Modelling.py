import streamlit as st
import pandas as pd
from functions.data_loader import load_client_data
from functions.ftp_rules import load_rules, detect_policy_violations
from functions.langchain_llm import query_llm
from PIL import Image
import os
import base64

st.set_page_config(page_title="Modelling", page_icon="🟠", layout="wide")

# === App-wide background with readable content box (robust selectors) ===
def add_bg_with_overlay(image_path, overlay_rgba="rgba(255,255,255,0.82)", blur_px=6):
    if not os.path.exists(image_path):
        st.warning(f"Background image not found at: {image_path}")
        return
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        /* App background */
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }}
        /* Remove default header background */
        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0);
        }}
        /* Main content overlay card */
        .main .block-container {{
            background: {overlay_rgba};
            backdrop-filter: blur({blur_px}px);
            -webkit-backdrop-filter: blur({blur_px}px); /* Safari */
            border-radius: 12px;
            padding: 2rem 2rem 2.5rem 2rem;
        }}
        /* Optional: sidebar translucency to match + positioning for footer */
        [data-testid="stSidebar"] > div:first-child {{
            background: rgba(255,255,255,0.65);
            backdrop-filter: blur({blur_px}px);
            -webkit-backdrop-filter: blur({blur_px}px);
            position: relative;            /* Allow absolute footer anchoring */
            padding-bottom: 84px;          /* Space for footer logos */
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

bg_path = os.path.join("assets", "background.jpg")
add_bg_with_overlay(bg_path, overlay_rgba="rgba(0,0,0,0.60)", blur_px=6)

# === Sidebar background image ===
def add_sidebar_bg(image_path):
    if not os.path.exists(image_path):
        st.warning(f"Sidebar image not found at: {image_path}")
        return
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] > div:first-child {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            position: relative;     /* Allow absolute footer anchoring */
            padding-bottom: 84px;   /* Space so content doesn't overlap logos */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

sidebar_bg_path = os.path.join("assets", "sidebar_bg.jpg")
add_sidebar_bg(sidebar_bg_path)

# === Sidebar footer logos helper ===
def add_sidebar_footer_logos(left_logo_path, right_logo_path, left_width=56, right_width=56, gap_px=10):
    if not (os.path.exists(left_logo_path) or os.path.exists(right_logo_path)):
        return

    def _b64(p):
        if not os.path.exists(p):
            return None
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode()

    left_b64 = _b64(left_logo_path)
    right_b64 = _b64(right_logo_path)

    st.sidebar.markdown(f"""
        <style>
        /* Footer container pinned to sidebar bottom */
        [data-testid="stSidebar"] .sidebar-footer {{
            position: absolute;
            left: 12px;
            right: 12px;
            bottom: -430px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: {gap_px}px;
            padding: 8px 10px;
            border-radius: 10px;
            background: rgba(0,0,0,0.99);
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(400px);
        }}
        [data-testid="stSidebar"] .sidebar-footer img {{
            display: block;
            height: auto;
            object-fit: contain;
        }}
        </style>
        <div class="sidebar-footer">
            {f'<img src="data:image/png;base64,{left_b64}" width="{left_width}px" />' if left_b64 else ''}
            {f'<img src="data:image/png;base64,{right_b64}" width="{right_width}px" />' if right_b64 else ''}
        </div>
    """, unsafe_allow_html=True)

# --- Sidebar footer logos ---
left_logo = os.path.join("assets", "bank_logo_small.png")
right_logo = os.path.join("assets", "oracle_logo_small.png")
add_sidebar_footer_logos(left_logo, right_logo, left_width=56, right_width=108)

# Top logos
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    if os.path.exists(os.path.join("assets", "bank_logo.png")):
        st.image(Image.open(os.path.join("assets", "bank_logo.png")), width=60)
with col3:
    if os.path.exists(os.path.join("assets", "oracle_logo.png")):
        st.image(Image.open(os.path.join("assets", "oracle_logo.png")), width=60)

with col2:
    if os.path.exists(os.path.join("assets", "home_title.png")):
        st.image(Image.open(os.path.join("assets", "home_title.png")), width=800)

# Sidebar Navigation
st.sidebar.title("Navigation")
if st.sidebar.button("🏠 Go to Home"):
    st.switch_page("main.py")
if st.sidebar.button("🟢 Go to Analysis"):
    st.switch_page("pages/1_Analysis.py")

# Page Header
st.title("🟠 Modelling Page")
st.markdown("This page will host ML models to estimate FTP rates")

# Placeholder for model results
st.markdown("### 🔧 Model Output")
st.info("Model integration coming soon.")
