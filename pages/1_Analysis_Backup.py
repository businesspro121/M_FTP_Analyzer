import streamlit as st
import pandas as pd
from functions.data_loader import load_client_data
from functions.ftp_rules import load_rules, detect_policy_violations
from functions.langchain_llm import query_llm
from PIL import Image
import os

st.set_page_config(page_title="Analysis", page_icon="🟢", layout="wide")

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
add_bg_with_overlay(bg_path, overlay_rgba="rgba(0,0,0,0.60)", blur_px=6)

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


# === Make spinner text white ===
st.markdown(
    """
    <style>
    [data-testid="stSpinner"] > div > div {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)



# Force success text to white, regardless of Streamlit version
st.markdown(
    """
    <style>
    /* Target all success boxes by their green border color */
    .stAlert {
        color: white !important;
    }
    .stAlert p, .stAlert div {
        color: white !important;
    }
    /* Specifically override the green-tinted text Streamlit sets */
    .stAlert[data-baseweb="notification"] {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Top logos ---
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    logo_path = os.path.join("assets", "bank_logo.png")
    if os.path.exists(logo_path):
        st.image(Image.open(logo_path), width=80)
#with col3:
    #  logo_path = os.path.join("assets", "oracle_logo.png")
        #  if os.path.exists(logo_path):
#    st.image(Image.open(logo_path), width=60)
with col2:
    title_path = os.path.join("assets", "home_title.png")
    if os.path.exists(title_path):
        st.image(Image.open(title_path), width=1500)

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
if st.sidebar.button("🏠 Go to Home"):
    st.switch_page("main.py")
if st.sidebar.button("🟠 Go to Modelling"):
    st.switch_page("pages/2_Modelling.py")

# --- Page Header ---
# --- Page Header ---
st.markdown(
    """
    <h1 style='color: white;'>🟢 Analysis Page</h1>
    <p style='color: white;'>
        This page loads the FTP data and connects to Oracle OCI LLM for anomaly detection.
    </p>
    """,
    unsafe_allow_html=True
)

# --- Load Excel File ---
file_path = "input_data/ClientFTPData.xlsx"
try:
    df = load_client_data(file_path)
    st.success(f"Loaded {len(df)} rows from FTP data.")
    st.dataframe(df)
    # Clear stale question on data reload
    st.session_state.pop("user_question", None)
except Exception as e:
    st.error(f"Failed to load data: {e}")
    df = None

# --- Run Policy Violation Check ---
violations_df = pd.DataFrame()
if df is not None:
    st.markdown(
        "<h3 style='color: white;'>🔍 Policy Violation Check</h3>",
        unsafe_allow_html=True
    )

    rules = load_rules()
    violations_df = detect_policy_violations(df, rules)

    if violations_df.empty:
        st.success("✅ No violations found in FTP data.")
    else:
        st.error(f"⚠️ {len(violations_df)} violations detected.")
        st.dataframe(violations_df)

# --- Suggested Questions ---
st.markdown(
    "<h3 style='color: white; text-shadow: 1px 1px 3px rgba(0,0,0,0.6);'>💬 Ask a question about the data</h3>",
    unsafe_allow_html=True
)

suggestions = [
    "What are the anomalies in FTP rates?",
    "How many violations/anomalies detected per policy category? - Provide a table",
    "Which entries violate policy rules?",
    "Which policies are being tested?"

]
for q in suggestions:
    if st.button(q):
        st.session_state["user_question"] = q

custom_question = st.text_input(
    label="",
    placeholder="Type your own question here..."
)
st.markdown(
    "<label style='color: white; font-weight: 500;'>Or type your own question:</label>",
    unsafe_allow_html=True
)

if custom_question:
    st.session_state["user_question"] = custom_question

# --- Optional: Max violations control ---
if not violations_df.empty:
    max_v = st.sidebar.number_input(
        "Max violations to send to LLM (0 = all)",
        min_value=0, value=0, step=1
    )
    max_v = None if max_v == 0 else max_v
else:
    max_v = None

# --- LLM response ---
if "user_question" in st.session_state and df is not None:
    if violations_df.empty:
        st.info("ℹ️ No violations to analyse.")
    else:
        st.markdown(
            f"<p style='color: white;'><strong>You asked:</strong> {st.session_state['user_question']}</p>",
            unsafe_allow_html=True
        )
        with st.spinner("Thinking..."):
            try:
                response = query_llm(
                    violations_df,
                    st.session_state["user_question"],
                    max_violations=max_v
                )
                st.markdown(
                    f"<h3 style='color: white;'>🧠 LLM Responded</h3><div style='color: white;'>{response}</div>",
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.error(f"LLM query failed: {e}")
