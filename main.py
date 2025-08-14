import streamlit as st
from PIL import Image
import os

st.set_page_config(
    page_title="Mashreq FTP AI Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === App-wide background with readable content box (robust selectors) ===
import base64

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
        /* Optional: sidebar translucency to match */
        [data-testid="stSidebar"] > div:first-child {{
            background: rgba(255,255,255,0.65);
            backdrop-filter: blur({blur_px}px);
            -webkit-backdrop-filter: blur({blur_px}px);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

bg_path = os.path.join("assets", "background.jpg")
add_bg_with_overlay(bg_path)

# === Sidebar background image ===
def add_sidebar_bg(image_path):
    if not os.path.exists(image_path):
        st.warning(f"Sidebar image not found at: {image_path}")
        return
    import base64
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


# Divider line at the top
#st.markdown("---")

# Top logos
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    if os.path.exists(os.path.join("assets", "bank_logo.png")):
        st.image(Image.open(os.path.join("assets", "bank_logo.png")), width=80)
#with col3:
        #  if os.path.exists(os.path.join("assets", "oracle_logo.png")):
#     st.image(Image.open(os.path.join("assets", "oracle_logo.png")), width=60)

with col2:
    if os.path.exists(os.path.join("assets", "home_title.png")):
        st.image(Image.open(os.path.join("assets", "home_title.png")), width=1500)

# Centered title and subtitle
st.markdown(
    """
    <div style='text-align: center; margin-top: 20px;color: white;'>
        <h1>Mashreq FTP AI Analyzer</h1>
        <h3>Choose an option to begin:</h3>
    </div>
    """,
    unsafe_allow_html=True
)

# Custom button styling
st.markdown(
    """
    <style>
    .button-row {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin-top: 10px;
        color: white;
    }
    .spacer {
        width: 340px;
    }
    .stButton > button {
        font-size: 18px;
        padding: 0.75em 2em;
        border-radius: 8px;
        border: none;
        background-color: #0072C6;
        color: white;
        font-weight: bold;
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #005A9E;
    }
    </style>
    """,
    unsafe_allow_html=True
)



# Centered buttons using Streamlit columns
button_col1, button_col2, button_col3 = st.columns([1.4, 1, 2])
with button_col2:
    if st.button("🟢 Analysis"):
        st.switch_page("pages/1_Analysis.py")
with button_col3:
    if st.button("🟠 Modelling - Michal's FDI (To be coded) "):
        st.switch_page("pages/2_Modelling.py")


# --- Sidebar footer logos ---
left_logo = os.path.join("assets", "bank_logo_small.png")
right_logo = os.path.join("assets", "oracle_logo_small.png")
add_sidebar_footer_logos(left_logo, right_logo, left_width=56, right_width=108)