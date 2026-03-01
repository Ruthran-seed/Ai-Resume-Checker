import base64
import json
import os
import time
from datetime import datetime

import streamlit as st

# -------- USER AUTH --------
from auth import (
    create_user,
    login_with_credentials,
    save_user_profile,
    get_user_profile,
    is_profile_completed,
    user_exists,
    get_user_existence_info,
    get_user_email,
    change_password,
    reset_password_by_email,
    load_users
)

# -------- HOST --------
from host_auth import create_host, login_host, reset_host_password_by_email, change_host_password, load_hosts
from host_panel_modern import host_dashboard

# -------- APPLY FLOW --------
from apply_flow import apply_to_job

# -------- CHAT --------
from user_chat import user_chat_interface, user_ai_chatbot_interface
from host_chat import host_chat_interface, add_host_chat_button

# -------- SCORE & STATUS --------
try:
    from score_updater import calculate_resume_match
    from status_updater import get_application_status
except:
    pass

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Resume Matcher - Professional Job Matching Platform",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"About": "AI Resume Matcher - Smart Hiring Platform v1.0"}
)



# ---------------- IMAGE LOADER ----------------
def get_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

logo = get_base64("logo.png") if os.path.exists("logo.png") else None

# ---------------- JOB HELPERS ----------------
JOB_FILE = "jobs.json"
APPLICATIONS_FILE = "applications.json"

def load_jobs():
    if os.path.exists(JOB_FILE):
        try:
            with open(JOB_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def load_applications():
    if os.path.exists(APPLICATIONS_FILE):
        try:
            with open(APPLICATIONS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def count_user_applications(user_id):
    apps = load_applications()
    count = 0
    for job_id, applicants in apps.items():
        if user_id in applicants:
            count += 1
    return count

def get_user_applications(user_id):
    """Get all applications for a user with job details"""
    apps = load_applications()
    jobs = load_jobs()
    user_apps = []
    
    for job_id, applicants in apps.items():
        if user_id in applicants:
            user_apps.append({
                "job_id": job_id,
                "job_title": jobs.get(job_id, {}).get("title", "Unknown Job"),
                "status": applicants[user_id].get("status", "Applied"),
                "score": applicants[user_id].get("score"),
                "applied_at": applicants[user_id].get("applied_at", "N/A")
            })
    
    return user_apps

# ---------------- GLOBAL STYLING ----------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&display=swap');

[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4,
[data-testid="stAppViewContainer"] h5,
[data-testid="stAppViewContainer"] h6,
[data-testid="stAppViewContainer"] .stMarkdown h1,
[data-testid="stAppViewContainer"] .stMarkdown h2,
[data-testid="stAppViewContainer"] .stMarkdown h3,
[data-testid="stAppViewContainer"] .stMarkdown h4,
[data-testid="stAppViewContainer"] .stMarkdown h5,
[data-testid="stAppViewContainer"] .stMarkdown h6,
[data-testid="stAppViewContainer"] .stTitle,
[data-testid="stAppViewContainer"] .stHeader {{
    font-family: "Cormorant Garamond", "Times New Roman", serif;
    letter-spacing: 0.9px;
    text-transform: uppercase;
    font-weight: 800 !important;
    text-shadow: 0 2px 16px rgba(0, 0, 0, 0.28);
    text-align: center !important;
    display: block;
    width: fit-content;
    max-width: 94%;
    margin-left: auto !important;
    margin-right: auto !important;
    padding: 8px 18px;
    border-radius: 14px;
    border: 1px solid rgba(194, 225, 255, 0.35);
    background: linear-gradient(120deg, rgba(255,255,255,0.10), rgba(255,255,255,0.05));
    box-shadow: 0 8px 18px rgba(7, 18, 35, 0.28);
}}

[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] .stMarkdown h1 {{
    color: #FFEA00 !important;
}}

[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] .stMarkdown h2 {{
    color: #FF8AE2 !important;
}}

[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] .stMarkdown h3 {{
    color: #83FFD7 !important;
}}

[data-testid="stAppViewContainer"] h4,
[data-testid="stAppViewContainer"] .stMarkdown h4 {{
    color: #8FC8FF !important;
}}

[data-testid="stAppViewContainer"] h5,
[data-testid="stAppViewContainer"] .stMarkdown h5 {{
    color: #FFC17A !important;
}}

[data-testid="stAppViewContainer"] h6,
[data-testid="stAppViewContainer"] .stMarkdown h6 {{
    color: #D7B3FF !important;
}}

[data-testid="stAppViewContainer"] {{
    /* Joyful AI-inspired background */
    background:
        radial-gradient(circle at 8% 12%, rgba(0, 245, 255, 0.22) 0%, rgba(0, 245, 255, 0) 34%),
        radial-gradient(circle at 88% 14%, rgba(255, 110, 199, 0.24) 0%, rgba(255, 110, 199, 0) 32%),
        radial-gradient(circle at 22% 84%, rgba(140, 255, 178, 0.22) 0%, rgba(140, 255, 178, 0) 34%),
        radial-gradient(circle at 82% 82%, rgba(255, 214, 102, 0.20) 0%, rgba(255, 214, 102, 0) 30%),
        repeating-linear-gradient(135deg, rgba(255,255,255,0.05) 0 2px, rgba(255,255,255,0) 2px 20px),
        repeating-radial-gradient(circle at 18% 28%, rgba(255, 255, 255, 0.08) 0 1px, rgba(255, 255, 255, 0) 1px 22px),
        linear-gradient(130deg, #0e1a34 0%, #192b52 30%, #1c295e 55%, #15385a 100%);
    min-height: 100vh;
}}
.logo {{
    text-align: center;
    margin-top: 30px;
}}
.logo img {{
    width: 140px;
    height: 140px;
    border-radius: 50%;
    object-fit: cover;
    background: white;
}}
h1, h2, p {{ color: white; text-align: center; }}
/* Ensure all buttons are visible on light backgrounds and are high-contrast */
button, .stButton>button, form button, .stButton>button[role="button"] {{
    background: linear-gradient(120deg, #5CAEFF, #7A7BFF) !important;
    color: #ffffff !important; /* high-contrast text */
    font-weight: 700 !important;
    border-radius: 12px !important;
    height: 3em !important;
    border: 1px solid rgba(255,255,255,0.28) !important;
    box-shadow: 0 8px 18px rgba(0,0,0,0.24) !important;
    transition: background-color 0.12s ease, transform 0.06s ease !important;
}}

.stButton:nth-of-type(6n+1) > button {{
    background: linear-gradient(120deg, #53B8FF, #6D8BFF) !important;
}}
.stButton:nth-of-type(6n+2) > button {{
    background: linear-gradient(120deg, #00D4FF, #00B894) !important;
}}
.stButton:nth-of-type(6n+3) > button {{
    background: linear-gradient(120deg, #FF7AB6, #B46CFF) !important;
}}
.stButton:nth-of-type(6n+4) > button {{
    background: linear-gradient(120deg, #FFB347, #FF7F6B) !important;
}}
.stButton:nth-of-type(6n+5) > button {{
    background: linear-gradient(120deg, #7EE787, #3ECF8E) !important;
}}
.stButton:nth-of-type(6n) > button {{
    background: linear-gradient(120deg, #8EC5FF, #3FD5FF) !important;
}}

/* Slightly darker hover/focus to indicate interactivity */
button:hover, .stButton>button:hover, button:focus, .stButton>button:focus {{
    filter: brightness(1.06) saturate(1.08) !important;
    transform: translateY(-1px) scale(1.01) !important;
}}

/* Make code/pre blocks use a dark background so white text is readable */
pre, code, .stCodeBlock pre, .stCodeBlock code {{
    background: rgba(0,0,0,0.7) !important;
    color: #ffffff !important;
    padding: 8px !important;
    border-radius: 6px !important;
}}

/* Ensure text inside any card-like white box is dark for readability */
.stAppViewContainer div[style*="background: white"],
.stCard, .css-1d391kg, .css-1y4p8pa {{






    
    color: #111111 !important;
}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
[data-testid="stHeader"] {
    background: transparent !important;
}
[data-testid="stAppViewContainer"] .block-container {
    max-width: 100% !important;
    padding-top: 4rem !important;
    padding-left: 1.2rem !important;
    padding-right: 1.2rem !important;
}

/* Premium shell look */
[data-testid="stAppViewContainer"] .block-container > div {
    background: linear-gradient(145deg, rgba(10, 18, 35, 0.58), rgba(22, 34, 62, 0.44));
    border: 1px solid rgba(170, 208, 255, 0.22);
    border-radius: 18px;
    padding: 12px;
    box-shadow: 0 18px 40px rgba(2, 8, 23, 0.34);
    backdrop-filter: blur(10px);
}

/* Inputs / text areas / select boxes */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input {
    background: linear-gradient(145deg, rgba(255,255,255,0.10), rgba(255,255,255,0.04)) !important;
    border: 1px solid rgba(170, 208, 255, 0.36) !important;
    border-radius: 12px !important;
    color: #f8fbff !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 6px 18px rgba(5, 14, 30, 0.28);
}

[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: rgba(107, 203, 255, 0.88) !important;
    box-shadow: 0 0 0 3px rgba(80, 185, 255, 0.20) !important;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    backdrop-filter: blur(8px);
}

/* Tabs and expanders */
[data-testid="stTabs"] button {
    border-radius: 10px !important;
    border: 1px solid rgba(170, 208, 255, 0.24) !important;
    margin-right: 6px !important;
}

[data-testid="stExpander"] {
    border: 1px solid rgba(170, 208, 255, 0.22) !important;
    border-radius: 12px !important;
    background: rgba(10, 20, 36, 0.40) !important;
}

/* Better table/dataframe readability */
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    border: 1px solid rgba(170, 208, 255, 0.24);
    border-radius: 12px;
    overflow: hidden;
}

/* Nicer scrollbar */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}
::-webkit-scrollbar-track {
    background: rgba(255,255,255,0.06);
    border-radius: 8px;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, rgba(124, 182, 255, 0.8), rgba(90, 132, 255, 0.8));
    border-radius: 8px;
}
::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, rgba(146, 198, 255, 0.92), rgba(110, 152, 255, 0.92));
}
</style>
""", unsafe_allow_html=True)


def apply_device_mode_styles(device_mode):
    if device_mode == "mobile":
        st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] .block-container {
            padding-top: 1.1rem !important;
            padding-left: 0.55rem !important;
            padding-right: 0.55rem !important;
            max-width: 560px !important;
            margin: 0 auto !important;
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 10% 12%, rgba(0, 255, 209, 0.16), rgba(0, 255, 209, 0) 35%),
                radial-gradient(circle at 85% 10%, rgba(168, 92, 255, 0.19), rgba(168, 92, 255, 0) 38%),
                radial-gradient(circle at 18% 86%, rgba(72, 161, 255, 0.14), rgba(72, 161, 255, 0) 40%),
                linear-gradient(145deg, #060b14 0%, #0b1322 48%, #111a2f 100%) !important;
        }

        [data-testid="stHeader"] {
            background: rgba(5, 10, 20, 0.92) !important;
            border-bottom: 1px solid rgba(66, 244, 231, 0.28) !important;
            backdrop-filter: blur(8px);
        }

        [data-testid="stAppViewContainer"] h1,
        [data-testid="stAppViewContainer"] h2,
        [data-testid="stAppViewContainer"] h3,
        [data-testid="stAppViewContainer"] h4,
        [data-testid="stAppViewContainer"] h5,
        [data-testid="stAppViewContainer"] h6,
        [data-testid="stAppViewContainer"] .stMarkdown h1,
        [data-testid="stAppViewContainer"] .stMarkdown h2,
        [data-testid="stAppViewContainer"] .stMarkdown h3,
        [data-testid="stAppViewContainer"] .stMarkdown h4,
        [data-testid="stAppViewContainer"] .stMarkdown h5,
        [data-testid="stAppViewContainer"] .stMarkdown h6 {
            font-family: "Cormorant Garamond", "Times New Roman", serif !important;
            text-transform: uppercase !important;
            letter-spacing: 0.9px !important;
            font-weight: 800 !important;
            text-shadow: 0 0 16px rgba(0, 255, 209, 0.28) !important;
            text-align: center !important;
            display: block !important;
            width: fit-content !important;
            max-width: 94% !important;
            margin-left: auto !important;
            margin-right: auto !important;
            margin-bottom: 10px !important;
            padding: 8px 18px !important;
            border-radius: 14px !important;
            border: 1px solid rgba(66, 244, 231, 0.35) !important;
            background: linear-gradient(120deg, rgba(9, 20, 40, 0.86), rgba(18, 33, 58, 0.78)) !important;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.30) !important;
        }

        h1, h2, h3, h4, h5, h6, p, span, label, li, small, div {
            color: #e7f3ff !important;
        }

        [data-testid="stAppViewContainer"] .block-container > div {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            backdrop-filter: none !important;
        }

        [data-testid="stAppViewContainer"] div[style*="background:"] {
            background: linear-gradient(145deg, rgba(11, 23, 44, 0.88), rgba(16, 30, 56, 0.78)) !important;
            color: #e7f3ff !important;
            border: 1px solid rgba(66, 244, 231, 0.25) !important;
            border-radius: 12px !important;
            box-shadow: 0 8px 18px rgba(0,0,0,0.28) !important;
            backdrop-filter: blur(8px) !important;
        }

        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        [data-testid="stNumberInput"] input,
        [data-testid="stDateInput"] input {
            background: linear-gradient(145deg, rgba(16, 28, 52, 0.95), rgba(12, 22, 42, 0.90)) !important;
            color: #dff5ff !important;
            border: 1px solid rgba(83, 170, 255, 0.38) !important;
            border-radius: 10px !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 4px 14px rgba(5, 10, 20, 0.35) !important;
        }

        [data-testid="stTextInput"] input:focus,
        [data-testid="stTextArea"] textarea:focus,
        [data-testid="stNumberInput"] input:focus {
            border-color: rgba(66, 244, 231, 0.92) !important;
            box-shadow: 0 0 0 2px rgba(66, 244, 231, 0.18), 0 0 18px rgba(66, 244, 231, 0.24) !important;
        }

        .stButton > button {
            height: 2.8em !important;
            font-size: 0.94rem !important;
            border-radius: 10px !important;
            border: 1px solid rgba(66, 244, 231, 0.48) !important;
            background: linear-gradient(130deg, #1f6fff, #00c8ff) !important;
            color: #ffffff !important;
            font-weight: 800 !important;
            box-shadow: 0 8px 16px rgba(6, 16, 34, 0.40), 0 0 14px rgba(31, 111, 255, 0.30) !important;
        }

        .stButton > button:hover {
            background: linear-gradient(130deg, #2f7fff, #00d8ff) !important;
            transform: translateY(-1px) !important;
            filter: none !important;
        }

        [data-testid="stAppViewContainer"] .stMarkdown,
        [data-testid="stAlert"],
        [data-testid="stExpander"],
        [data-testid="stDataFrame"],
        [data-testid="stTable"] {
            background: linear-gradient(145deg, rgba(10, 20, 38, 0.88), rgba(14, 24, 46, 0.80)) !important;
            border: 1px solid rgba(84, 166, 255, 0.28) !important;
            border-radius: 12px !important;
            box-shadow: 0 8px 16px rgba(0,0,0,0.30) !important;
            color: #e7f3ff !important;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(160deg, rgba(8,14,28,0.98), rgba(12,20,36,0.98)) !important;
        }

        [data-testid="stAppViewContainer"] h1,
        [data-testid="stAppViewContainer"] .stMarkdown h1 {
            font-size: 1.28rem !important;
            color: #5ef9ff !important;
        }
        [data-testid="stAppViewContainer"] h2,
        [data-testid="stAppViewContainer"] .stMarkdown h2 {
            font-size: 1.12rem !important;
            color: #7ecbff !important;
        }
        [data-testid="stAppViewContainer"] h3,
        [data-testid="stAppViewContainer"] .stMarkdown h3 {
            font-size: 1rem !important;
            color: #8de8ff !important;
        }
        p, li, label, .stCaption {
            font-size: 0.91rem !important;
            color: #d3e9ff !important;
            text-align: left !important;
        }

        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(255,255,255,0.04);
        }
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, rgba(0, 200, 255, 0.85), rgba(95, 98, 255, 0.85));
            border-radius: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
    elif device_mode == "pc":
        st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] .block-container {
            max-width: 100% !important;
            padding-top: 4rem !important;
            padding-left: 1.4rem !important;
            padding-right: 1.4rem !important;
        }
        [data-testid="stHeader"] {
            background: transparent !important;
            border-bottom: none !important;
        }
        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 8% 12%, rgba(0, 245, 255, 0.22) 0%, rgba(0, 245, 255, 0) 34%),
                radial-gradient(circle at 88% 14%, rgba(255, 110, 199, 0.24) 0%, rgba(255, 110, 199, 0) 32%),
                radial-gradient(circle at 22% 84%, rgba(140, 255, 178, 0.22) 0%, rgba(140, 255, 178, 0) 34%),
                radial-gradient(circle at 82% 82%, rgba(255, 214, 102, 0.20) 0%, rgba(255, 214, 102, 0) 30%),
                linear-gradient(130deg, #0e1a34 0%, #192b52 30%, #1c295e 55%, #15385a 100%) !important;
        }
        </style>
        """, unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
defaults = {
    "page": "welcome",
    "issued_user_id": None,
    "issued_password": None,
    "show_credentials": False,
    "user_id": None,
    "device_mode": None
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

apply_device_mode_styles(st.session_state.device_mode)
is_mobile = st.session_state.device_mode == "mobile"


def render_page_heading(title, subtitle):
    mobile_mode = st.session_state.get("device_mode") == "mobile"
    if mobile_mode:
        st.markdown(f"""
        <div style="
            background: linear-gradient(145deg, rgba(10, 20, 38, 0.9), rgba(14, 26, 48, 0.82));
            border: 1px solid rgba(66, 244, 231, 0.32);
            border-radius: 16px;
            padding: 16px 14px;
            margin: 0 0 16px 0;
            box-shadow: 0 10px 20px rgba(0,0,0,0.30);
            text-align: center;
        ">
            <div style="
                font-size: 1.35rem;
                font-weight: 900;
                letter-spacing: 0.9px;
                text-transform: uppercase;
                line-height: 1.2;
                margin-bottom: 6px;
                color: #5ef9ff;
                text-shadow: 0 0 14px rgba(94, 249, 255, 0.35);
            ">{title}</div>
            <div style="
                font-size: 0.93rem;
                color: #d3e9ff;
                line-height: 1.5;
                font-weight: 700;
                letter-spacing: 0.2px;
                text-align: center;
            ">{subtitle}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="
            background: linear-gradient(130deg, rgba(92,174,255,0.22), rgba(168,85,247,0.20), rgba(16,185,129,0.15));
            border: 1px solid rgba(170, 208, 255, 0.45);
            border-radius: 16px;
            padding: 18px 22px;
            margin: 0 0 22px 0;
            box-shadow: 0 14px 30px rgba(8, 20, 40, 0.33);
            text-align: center;
        ">
            <div style="
                font-size: 2rem;
                font-weight: 900;
                letter-spacing: 1.4px;
                text-transform: uppercase;
                line-height: 1.15;
                margin-bottom: 7px;
                background: linear-gradient(90deg, #FFEA00 0%, #83FFD7 45%, #8FC8FF 75%, #D7B3FF 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 3px 22px rgba(90, 170, 255, 0.35);
            ">{title}</div>
            <div style="
                font-size: 1.02rem;
                color: #ecf4ff;
                line-height: 1.55;
                font-weight: 700;
                letter-spacing: 0.25px;
                text-align: center;
            ">{subtitle}</div>
        </div>
        """, unsafe_allow_html=True)

# ================= WELCOME =================
if st.session_state.page == "welcome":
    st.markdown(f"""
    <div class="logo"><img src="data:image/png;base64,{logo}"></div>
    <h1>AI Resume Platform</h1>
    <p>Smart hiring powered by Artificial Intelligence</p>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:40vh'></div>", unsafe_allow_html=True)
    if st.button("🚀 Enter Platform", use_container_width=True):
        st.session_state.page = "device_setup"; st.rerun()

# ================= DEVICE SETUP (SECOND PAGE) =================
elif st.session_state.page == "device_setup":
    render_page_heading("CHOOSE YOUR DEVICE VIEW", "Pick the layout that matches your device for better readability.")

    if is_mobile:
        col1 = st.container()
        col2 = st.container()
    else:
        col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.1); padding: 26px; border-radius: 15px; text-align: center; backdrop-filter: blur(10px); min-height: 210px;">
            <h3 style="color: #7BB6FF; margin-bottom: 12px;">🖥️ PC / Laptop</h3>
            <p style="color: #d0d0d0; font-size: 14px; line-height: 1.6;">
                Wider layout with full spacing and larger panels. Best for desktop/laptop screens.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Use PC View", use_container_width=True, key="device_pc"):
            st.session_state.device_mode = "pc"
            st.session_state.page = "role"
            st.rerun()

    with col2:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.1); padding: 26px; border-radius: 15px; text-align: center; backdrop-filter: blur(10px); min-height: 210px;">
            <h3 style="color: #A8D5BA; margin-bottom: 12px;">📱 Mobile</h3>
            <p style="color: #d0d0d0; font-size: 14px; line-height: 1.6;">
                Compact layout with tighter spacing and smaller text for mobile screens.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Use Mobile View", use_container_width=True, key="device_mobile"):
            st.session_state.device_mode = "mobile"
            st.session_state.page = "role"
            st.rerun()

    if st.button("⬅️ Back", use_container_width=True, key="device_back"):
        st.session_state.page = "welcome"
        st.rerun()

# ================= ROLE =================
elif st.session_state.page == "role":
    render_page_heading("SELECT YOUR ROLE", "Choose how you'd like to use our platform")
    
    if is_mobile:
        col1 = st.container()
        col2 = st.container()
    else:
        col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; text-align: center; backdrop-filter: blur(10px);">
            <h3 style="color: #7BB6FF; margin-bottom: 15px;">👤 Job Seeker</h3>
            <p style="color: #d0d0d0; font-size: 14px; line-height: 1.6;">
                Browse job opportunities, upload your resume, and get AI-powered matching recommendations tailored to your skills.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Continue as Job Seeker", use_container_width=True, key="user_btn"):
            st.session_state.page = "user_entry"; st.rerun()
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; text-align: center; backdrop-filter: blur(10px);">
            <h3 style="color: #A8D5BA; margin-bottom: 15px;">🏢 Employer</h3>
            <p style="color: #d0d0d0; font-size: 14px; line-height: 1.6;">
                Post job openings, review candidate profiles, and leverage AI analytics to find the perfect match for your team.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Continue as Employer", use_container_width=True, key="host_btn"):
            st.session_state.page = "host_auth"; st.rerun()

# ================= USER ENTRY =================
elif st.session_state.page == "user_entry":
    st.markdown("""
    <div style="background: linear-gradient(120deg, rgba(92,174,255,0.20), rgba(168,85,247,0.18), rgba(16,185,129,0.12)); border:1px solid rgba(170, 208, 255, 0.35); border-radius:16px; padding:18px 22px; margin-bottom:18px;">
        <h2 style="margin:0;">Job Seeker Portal</h2>
        <p style="font-size: 15px; color: #eaf2ff; margin:8px 0 0 0;">Create your account in 1 minute and start applying with AI-powered matching.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: rgba(255,255,255,0.08); border:1px solid rgba(170, 208, 255, 0.30); border-radius:14px; padding:14px 16px; margin-bottom:16px;">
        <div style="color:#d8eaff; font-weight:700; margin-bottom:6px;">Quick Steps</div>
        <div style="color:#f4f8ff; font-size:14px; line-height:1.7;">1) Create account  •  2) Save credentials  •  3) Complete profile  •  4) Upload resume</div>
    </div>
    """, unsafe_allow_html=True)
    
    if is_mobile:
        col1 = st.container()
        col2 = st.container()
    else:
        col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.10); padding: 34px; border-radius: 16px; text-align: center; backdrop-filter: blur(12px); border: 1px solid rgba(123, 182, 255, 0.45); box-shadow: 0 10px 24px rgba(30, 70, 130, 0.25); min-height: 275px; display:flex; flex-direction:column; justify-content:center;">
            <h3 style="color: #7BB6FF; margin-bottom: 10px; font-size: 30px;">🆕</h3>
            <h4 style="color: #F2F7FF; margin-bottom: 12px;">Create Account</h4>
            <p style="color: #dfe8f6; font-size: 14px; line-height: 1.65; margin-bottom: 20px;">
                New user? Start here with email, user ID, and password. Your dashboard and profile will be ready instantly.
            </p>
            <div style="color:#b9d8ff; font-size:12px; font-weight:600;">Recommended for first-time users</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📝 Create New Account", use_container_width=True, key="create_btn"):
            st.session_state.page = "signup"; st.rerun()
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.10); padding: 34px; border-radius: 16px; text-align: center; backdrop-filter: blur(12px); border: 1px solid rgba(168, 213, 186, 0.45); box-shadow: 0 10px 24px rgba(20, 90, 80, 0.22); min-height: 275px; display:flex; flex-direction:column; justify-content:center;">
            <h3 style="color: #A8D5BA; margin-bottom: 10px; font-size: 30px;">🔐</h3>
            <h4 style="color: #F2F7FF; margin-bottom: 12px;">Sign In</h4>
            <p style="color: #dfe8f6; font-size: 14px; line-height: 1.65; margin-bottom: 20px;">
                Already have an account? Continue to your dashboard, profile, applications, and messages.
            </p>
            <div style="color:#b8f0d0; font-size:12px; font-weight:600;">Use existing credentials</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔑 Sign Into Account", use_container_width=True, key="login_btn"):
            st.session_state.page = "login"; st.rerun()
    
# ================= SIGNUP =================
elif st.session_state.page == "signup":
    st.markdown("""
    <style>
    .signup-main {
        border-radius: 18px;
        border: 1px solid rgba(165, 215, 255, 0.35);
        background: linear-gradient(125deg, rgba(92,174,255,0.23), rgba(124,58,237,0.16), rgba(16,185,129,0.12));
        padding: 20px 22px;
        margin-bottom: 16px;
        box-shadow: 0 12px 24px rgba(20, 38, 74, 0.28);
    }
    .signup-side {
        border-radius: 14px;
        padding: 16px;
        border: 1px solid rgba(165, 215, 255, 0.30);
        background: rgba(255,255,255,0.08);
        min-height: 325px;
    }
    .signup-point {
        border-radius: 10px;
        border: 1px solid rgba(180, 222, 255, 0.25);
        background: rgba(255,255,255,0.05);
        padding: 10px 12px;
        margin: 8px 0;
    }
    .signup-form-shell {
        border-radius: 14px;
        border: 1px solid rgba(165, 215, 255, 0.30);
        background: rgba(10, 20, 38, 0.52);
        padding: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="signup-main">
        <h2 style="margin:0; color:#ffffff;">Create Account</h2>
        <p style="margin:8px 0 0 0; color:#eaf4ff;">Organized onboarding for job seekers with fast setup and secure credentials.</p>
    </div>
    """, unsafe_allow_html=True)

    if is_mobile:
        left_col = st.container()
        right_col = st.container()
    else:
        left_col, right_col = st.columns([1, 1.6])

    with left_col:
        st.markdown("""
        <div class="signup-side">
            <h4 style="margin:0 0 10px 0; color:#E5F2FF;">Why create account?</h4>
            <div class="signup-point"><strong style="color:#BEE0FF;">🎯 Better Matching</strong><br><span style="color:#e7f1ff; font-size:13px;">Get AI-powered job suggestions based on your profile.</span></div>
            <div class="signup-point"><strong style="color:#BEE0FF;">⚡ Fast Apply</strong><br><span style="color:#e7f1ff; font-size:13px;">Apply to multiple roles quickly after setup.</span></div>
            <div class="signup-point"><strong style="color:#BEE0FF;">🔐 Secure Access</strong><br><span style="color:#e7f1ff; font-size:13px;">Use your credentials to access dashboard and updates.</span></div>
            <div style="margin-top:10px; color:#D2E9FF; font-size:13px; line-height:1.7;">
                <strong>Requirements:</strong><br>
                • Valid email address<br>
                • User ID: 4-15 chars (a-z, 0-9, _)<br>
                • Password: 6-20 chars with letters + numbers
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        st.markdown("<div class='signup-form-shell'>", unsafe_allow_html=True)
        with st.form("signup_form"):
            st.markdown("<h4 style='margin:0 0 8px 0; color:#EAF4FF;'>Account Details</h4>", unsafe_allow_html=True)
            if is_mobile:
                top_c1 = st.container()
                top_c2 = st.container()
            else:
                top_c1, top_c2 = st.columns(2)
            with top_c1:
                email = st.text_input("Email", placeholder="your.email@example.com", help="Enter your active email address")
            with top_c2:
                user_id = st.text_input("Create User ID", placeholder="john_doe123", help="4-15 characters (letters, numbers, _)")

            st.markdown("<h4 style='margin:8px 0 8px 0; color:#EAF4FF;'>Security</h4>", unsafe_allow_html=True)
            if is_mobile:
                pass_c1 = st.container()
                pass_c2 = st.container()
            else:
                pass_c1, pass_c2 = st.columns(2)
            with pass_c1:
                password = st.text_input("Create Password", type="password", placeholder="MyPass123", help="6-20 chars, must have letters & numbers")
            with pass_c2:
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="MyPass123")

            st.caption("After signup, save your credentials and login to complete your profile.")
            submit_btn = st.form_submit_button("✅ Create Account", use_container_width=True)
        
            if submit_btn:
                email_clean = email.strip().lower()
                user_id_clean = user_id.strip()
                password_clean = password.strip()
                confirm_password_clean = confirm_password.strip()

                if not email_clean or "@" not in email_clean:
                    st.error("❌ Please enter a valid email address")
                elif password_clean != confirm_password_clean:
                    st.error("❌ Passwords do not match")
                else:
                    with st.spinner("🔄 Creating your account..."):
                        result = create_user(email_clean, user_id_clean, password_clean)
                        time.sleep(0.5)
                    if result[0] is None:
                        st.error(f"❌ {result[1]}")
                    else:
                        st.session_state.issued_user_id = result[0]
                        st.session_state.issued_password = result[1]
                        st.session_state.show_credentials = True
                        st.session_state.page = "login"
                        st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("⬅️ Back", use_container_width=True):
        st.session_state.page = "user_entry"; st.rerun()
    
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ================= LOGIN =================
elif st.session_state.page == "login":
    st.markdown("<h2>Login</h2>", unsafe_allow_html=True)
    if st.session_state.show_credentials:
        st.success("🎉 Account Created Successfully")
        st.warning("⚠️ IMPORTANT: Save your credentials below. You will need them to login later!")
        # Dark-styled credentials box for readability
        creds_html = f"""
        <div style='background: rgba(0,0,0,0.75); padding: 16px; border-radius: 10px; display:flex; gap:12px; align-items:center; justify-content:center;'>
            <div style='flex:1; text-align:center;'>
                <div style='color:#7BB6FF; font-weight:700; margin-bottom:6px;'>Your User ID</div>
                <pre style='background:transparent; color:#fff; font-size:14px; padding:8px; border-radius:6px; margin:0;'>{st.session_state.issued_user_id}</pre>
            </div>
            <div style='flex:1; text-align:center;'>
                <div style='color:#7BB6FF; font-weight:700; margin-bottom:6px;'>Your Password</div>
                <pre style='background:transparent; color:#fff; font-size:14px; padding:8px; border-radius:6px; margin:0;'>{st.session_state.issued_password}</pre>
            </div>
        </div>
        """
        st.markdown(creds_html, unsafe_allow_html=True)
        st.info("💡 Tip: Copy your User ID and Password to a safe place before proceeding")
    
    with st.form("login_form"):
        user_id = st.text_input("User ID", placeholder="e.g., USER1234", help="Enter your User ID")
        password = st.text_input("Password", type="password", placeholder="Enter your password", help="Enter your password")
        submit_btn = st.form_submit_button("Login", use_container_width=True)
        
        if submit_btn:
            # Strip whitespace from inputs to avoid login issues
            user_id_clean = user_id.strip()
            password_clean = password.strip()
            
            # Validate inputs are not empty
            if not user_id_clean or not password_clean:
                st.error("❌ Please enter both User ID and Password")
            else:
                with st.spinner("🔐 Authenticating..."):
                    user = login_with_credentials(user_id_clean, password_clean)
                    time.sleep(0.3)
                if user:
                    st.session_state.user_id = user_id_clean
                    st.session_state.show_credentials = False  # Clear credentials after successful login
                    st.session_state.page = "dashboard" if is_profile_completed(user_id_clean) else "profile_setup"
                    st.rerun()
                else:
                    # Help user debug why login failed
                    exists, email = get_user_existence_info(user_id_clean)
                    st.error("❌ Invalid credentials. Please check your User ID and Password carefully.")
                    
                    if not exists:
                        st.warning(f"⚠️ User ID '{user_id_clean}' does not exist in our system.")
                        st.info("Did you mean to create a new account instead? Go back and select 'Create New Account'")
                    else:
                        st.warning(f"ℹ️ User ID exists (Email: {email}), but the password is incorrect.")
                        st.info("💡 Password is case-sensitive. Make sure you typed it exactly as shown.")
    
    st.markdown("<div style='text-align: center; margin: 20px 0;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔑 Forgot Password?", use_container_width=True):
            st.session_state.page = "forgot_password"; st.rerun()
    
    if st.button("⬅️ Back", use_container_width=True):
        st.session_state.show_credentials = False
        st.session_state.page = "user_entry"; st.rerun()

# ================= PROFILE SETUP =================
elif st.session_state.page == "profile_setup":
    existing_profile = {}
    if st.session_state.user_id:
        existing_profile = get_user_profile(st.session_state.user_id) or {}

    existing_exp = int(existing_profile.get("experience_years", 0) or 0)

    field_checks = [
        existing_profile.get("name"),
        existing_profile.get("phone"),
        existing_profile.get("city"),
        existing_profile.get("qualification"),
        existing_profile.get("headline"),
        existing_profile.get("current_role"),
        existing_exp > 0,
        existing_profile.get("bio"),
        existing_profile.get("linkedin"),
        existing_profile.get("skills"),
        existing_profile.get("avatar")
    ]
    completion_pct = int((sum(1 for item in field_checks if item) / len(field_checks)) * 100)

    st.markdown("""
    <style>
    .profile-hero {
        border-radius: 18px;
        padding: 20px 24px;
        border: 1px solid rgba(138, 180, 248, 0.35);
        background: linear-gradient(130deg, rgba(92,174,255,0.22) 0%, rgba(124,58,237,0.20) 45%, rgba(16,185,129,0.16) 100%);
        margin-bottom: 14px;
        box-shadow: 0 12px 26px rgba(12, 22, 34, 0.30);
    }
    .profile-chip {
        display: inline-block;
        margin: 6px 8px 0 0;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid rgba(255,255,255,0.28);
        background: rgba(255,255,255,0.12);
        color: #E9F4FF;
    }
    .profile-card {
        border-radius: 14px;
        padding: 14px 16px;
        border: 1px solid rgba(123, 182, 255, 0.28);
        background: linear-gradient(160deg, rgba(123, 182, 255, 0.12), rgba(99, 102, 241, 0.10));
        margin-bottom: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='profile-hero'>
        <h2 style='margin:0; color:#ffffff;'>Build a Standout Profile</h2>
        <p style='margin:6px 0 2px 0; color:#E3EEFF;'>Create a polished profile that helps recruiters evaluate you faster.</p>
        <span class='profile-chip'>✨ Professional Look</span>
        <span class='profile-chip'>🎯 Better Match Quality</span>
        <span class='profile-chip'>📈 Completion: {completion_pct}%</span>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""
        <div class='profile-card'>
            <div style='color:#B8D8FF; font-size:12px; font-weight:700;'>PROFILE COMPLETION</div>
            <div style='color:#ffffff; font-size:26px; font-weight:800;'>{completion_pct}%</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class='profile-card'>
            <div style='color:#B8D8FF; font-size:12px; font-weight:700;'>ACCOUNT</div>
            <div style='color:#ffffff; font-size:16px; font-weight:700;'>User: {st.session_state.user_id}</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        skills_count = len(existing_profile.get("skills", [])) if existing_profile.get("skills") else 0
        st.markdown(f"""
        <div class='profile-card'>
            <div style='color:#B8D8FF; font-size:12px; font-weight:700;'>SKILLS ADDED</div>
            <div style='color:#ffffff; font-size:26px; font-weight:800;'>{skills_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with st.form("profile_setup_form"):
        left_col, right_col = st.columns([1.25, 1])

        with left_col:
            st.markdown("<h4 style='color:#A9D0FF; margin-bottom:8px;'>👤 Personal Information</h4>", unsafe_allow_html=True)
            name = st.text_input("Full Name", value=existing_profile.get("name", ""), placeholder="Enter your full name")
            phone = st.text_input("Phone", value=existing_profile.get("phone", ""), placeholder="e.g. +91 98765 43210")
            city = st.text_input("City", value=existing_profile.get("city", ""), placeholder="Your current city")
            qualification = st.text_input("Qualification", value=existing_profile.get("qualification", ""), placeholder="e.g. B.Tech, MBA")
            headline = st.text_input(
                "Professional Headline",
                value=existing_profile.get("headline", ""),
                placeholder="e.g. Data Analyst | Python | Power BI | Excel"
            )
            current_role = st.text_input(
                "Current Role",
                value=existing_profile.get("current_role", ""),
                placeholder="e.g. Software Engineer / Fresher"
            )
            experience_years = st.number_input(
                "Experience (Years)",
                min_value=0,
                max_value=40,
                value=existing_exp,
                step=1
            )

        with right_col:
            st.markdown("<h4 style='color:#A9D0FF; margin-bottom:8px;'>🖼️ Profile Picture</h4>", unsafe_allow_html=True)
            avatar_preview = existing_profile.get("avatar")
            if avatar_preview and os.path.exists(avatar_preview):
                st.image(avatar_preview, width=170, caption="Current profile picture")
            avatar_file = st.file_uploader(
                "Upload profile picture",
                type=["png", "jpg", "jpeg"],
                accept_multiple_files=False,
                help="Use a clear headshot for a professional impression"
            )
            st.markdown("<h4 style='color:#A9D0FF; margin:14px 0 8px 0;'>🌐 Professional Links</h4>", unsafe_allow_html=True)
            linkedin = st.text_input(
                "LinkedIn URL",
                value=existing_profile.get("linkedin", ""),
                placeholder="https://www.linkedin.com/in/your-profile"
            )
            github = st.text_input(
                "GitHub URL",
                value=existing_profile.get("github", ""),
                placeholder="https://github.com/your-username"
            )
            portfolio = st.text_input(
                "Portfolio URL",
                value=existing_profile.get("portfolio", ""),
                placeholder="https://yourportfolio.com"
            )

        address = st.text_area(
            "Address",
            value=existing_profile.get("address", ""),
            placeholder="Add your current address",
            height=90
        )
        bio = st.text_area(
            "Professional Summary",
            value=existing_profile.get("bio", ""),
            placeholder="Write a short summary about your experience, strengths, and career goals",
            height=120
        )
        skills_val = ", ".join(existing_profile.get("skills", [])) if existing_profile.get("skills") else ""
        skills = st.text_input(
            "Skills (comma separated)",
            value=skills_val,
            placeholder="Python, Data Analysis, Communication, Problem Solving"
        )
        pref_col1, pref_col2, pref_col3 = st.columns(3)
        with pref_col1:
            preferred_role = st.text_input(
                "Preferred Role",
                value=existing_profile.get("preferred_role", ""),
                placeholder="e.g. Backend Developer"
            )
        with pref_col2:
            preferred_location = st.text_input(
                "Preferred Location",
                value=existing_profile.get("preferred_location", ""),
                placeholder="e.g. Bengaluru / Remote"
            )
        with pref_col3:
            notice_period = st.text_input(
                "Notice Period",
                value=existing_profile.get("notice_period", ""),
                placeholder="e.g. Immediate / 30 Days"
            )

        submit_profile = st.form_submit_button("💾 Save Profile", use_container_width=True)

        if submit_profile:
            if not name.strip() or not phone.strip() or not city.strip() or not qualification.strip():
                st.error("❌ Please fill Full Name, Phone, City, and Qualification")
            else:
                with st.spinner("💾 Saving your profile..."):
                    avatar_path = existing_profile.get("avatar")
                    if avatar_file is not None:
                        os.makedirs("uploads", exist_ok=True)
                        _, ext = os.path.splitext(avatar_file.name)
                        avatar_path = f"uploads/{st.session_state.user_id}{ext}"
                        with open(avatar_path, "wb") as f:
                            f.write(avatar_file.getbuffer())

                    save_user_profile(st.session_state.user_id, {
                        "name": name.strip(),
                        "phone": phone.strip(),
                        "address": address.strip(),
                        "city": city.strip(),
                        "qualification": qualification.strip(),
                        "headline": headline.strip(),
                        "current_role": current_role.strip(),
                        "experience_years": int(experience_years),
                        "linkedin": linkedin.strip(),
                        "github": github.strip(),
                        "portfolio": portfolio.strip(),
                        "bio": bio.strip(),
                        "skills": [s.strip() for s in skills.split(",") if s.strip()],
                        "preferred_role": preferred_role.strip(),
                        "preferred_location": preferred_location.strip(),
                        "notice_period": notice_period.strip(),
                        "avatar": avatar_path
                    })
                    time.sleep(0.5)
                st.success("✅ Profile saved")
                st.session_state.page = "dashboard"; st.rerun()

# ================= DASHBOARD =================
elif st.session_state.page == "dashboard":
    profile = get_user_profile(st.session_state.user_id) or {}
    display_name = profile.get("name") or st.session_state.user_id
    apps_count = count_user_applications(st.session_state.user_id)
    profile_status = "Complete" if is_profile_completed(st.session_state.user_id) else "Incomplete"

    st.markdown("""
    <style>
    .stButton > button {
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.24) !important;
        border-radius: 14px !important;
        height: 3.1em !important;
        font-weight: 700 !important;
        letter-spacing: 0.2px !important;
        box-shadow: 0 10px 20px rgba(14, 25, 45, 0.24) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    .stButton > button::after {
        content: "";
        position: absolute;
        top: -60%;
        left: -20%;
        width: 60%;
        height: 220%;
        background: linear-gradient(90deg, rgba(255,255,255,0.35), rgba(255,255,255,0));
        transform: rotate(18deg);
        opacity: 0.35;
    }
    .stButton > button:hover {
        transform: translateY(-1px) scale(1.01) !important;
        box-shadow: 0 12px 24px rgba(14, 25, 45, 0.30) !important;
    }
    .stButton > button:active {
        transform: translateY(0) scale(0.99) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background: rgba(255,255,255,0.04); border: 1px solid rgba(123, 182, 255, 0.18); padding: 18px 22px; border-radius: 14px; margin-bottom: 18px;'>
        <div style='display:flex; align-items:center; justify-content:space-between; gap:12px;'>
            <div>
                <h2 style='margin:0; color:#ffffff;'>Welcome, {display_name}</h2>
                <p style='margin:4px 0 0 0; color:#c9d4e3;'>Manage applications, resumes, and messages in one place.</p>
            </div>
            <div style='text-align:right;'>
                <div style='color:#7BB6FF; font-weight:700; font-size:14px;'>Account</div>
                <div style='color:#ffffff; font-size:13px;'>User ID: {st.session_state.user_id}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div style='background: rgba(123, 182, 255, 0.08); border: 1px solid rgba(123, 182, 255, 0.22); padding: 16px; border-radius: 12px;'>
            <div style='color:#7BB6FF; font-weight:700; font-size:13px;'>Applications</div>
            <div style='color:#ffffff; font-size:24px; font-weight:700;'>{apps_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style='background: rgba(123, 182, 255, 0.08); border: 1px solid rgba(123, 182, 255, 0.22); padding: 16px; border-radius: 12px;'>
            <div style='color:#7BB6FF; font-weight:700; font-size:13px;'>Profile Status</div>
            <div style='color:#ffffff; font-size:24px; font-weight:700;'>{profile_status}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div style='background: rgba(123, 182, 255, 0.08); border: 1px solid rgba(123, 182, 255, 0.22); padding: 16px; border-radius: 12px;'>
            <div style='color:#7BB6FF; font-weight:700; font-size:13px;'>Messages</div>
            <div style='color:#ffffff; font-size:24px; font-weight:700;'>Inbox</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#7BB6FF; margin-bottom:8px;'>Quick Actions</h3>", unsafe_allow_html=True)

    r1c1, r1c2, r1c3 = st.columns(3)
    with r1c1:
        if st.button("💼 View Jobs", use_container_width=True):
            st.session_state.page = "view_jobs"; st.rerun()
    with r1c2:
        if st.button("📄 Upload Resume", use_container_width=True):
            st.session_state.page = "upload_resume"; st.rerun()
    with r1c3:
        if st.button("💬 Messages", use_container_width=True):
            st.session_state.page = "user_chat"; st.rerun()

    r2c1, r2c2, r2c3 = st.columns(3)
    with r2c1:
        if st.button("👤 My Profile", use_container_width=True):
            st.session_state.page = "profile_view"; st.rerun()
    with r2c2:
        if st.button("✏️ Edit Profile", use_container_width=True):
            st.session_state.page = "profile_setup"; st.rerun()
    with r2c3:
        if st.button("🔐 Change Password", use_container_width=True):
            st.session_state.page = "change_password"; st.rerun()

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#7BB6FF; margin-bottom:8px;'>Account</h3>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        for k in defaults:
            st.session_state[k] = defaults[k]
        st.rerun()

# ================= VIEW JOBS =================
elif st.session_state.page == "view_jobs":
    st.markdown("<h2>Available Jobs</h2>", unsafe_allow_html=True)
    jobs = load_jobs()
    if not jobs:
        st.info("No jobs available")
    else:
        for job_id, job in jobs.items():
            with st.expander(f"💼 {job['title']}"):
                st.markdown(f"**📍 Location:** {job.get('location', 'N/A')}")
                st.markdown(f"**📝 Description:**\n{job.get('description', 'N/A')}")
                keywords = job.get("keywords", [])
                if keywords:
                    st.markdown(f"**🔑 Keywords:** {', '.join(keywords)}")
                
                st.markdown("---")
                if st.button(f"Apply for {job_id}", use_container_width=True, key=f"apply_{job_id}"):
                    resume_path = f"resumes/{st.session_state.user_id}.pdf"
                    if not os.path.exists(resume_path):
                        st.error("❌ Please upload your resume first")
                    else:
                        with st.spinner("📤 Submitting your application..."):
                            ok = apply_to_job(job_id, st.session_state.user_id, resume_path)
                            time.sleep(0.5)
                        if ok:
                            st.success("✅ Applied successfully!")
                            st.balloons()
                        else:
                            st.warning("⚠️ You have already applied for this job")
    
    st.markdown("---")
    if st.button("⬅️ Back to Dashboard", use_container_width=True):
        st.session_state.page = "dashboard"; st.rerun()

# ================= UPLOAD RESUME =================
elif st.session_state.page == "upload_resume":
    st.markdown("<h2>Upload Resume</h2>", unsafe_allow_html=True)
    resume = st.file_uploader("Upload PDF", type=["pdf"])
    if resume:
        with st.spinner("📤 Uploading your resume..."):
            os.makedirs("resumes", exist_ok=True)
            with open(f"resumes/{st.session_state.user_id}.pdf", "wb") as f:
                f.write(resume.getbuffer())
            time.sleep(0.5)
        st.success("✅ Resume uploaded successfully!")
    if st.button("⬅️ Back", use_container_width=True):
        st.session_state.page = "dashboard"; st.rerun()

# ================= PROFILE VIEW =================
elif st.session_state.page == "profile_view":
    profile = get_user_profile(st.session_state.user_id) or {}

    st.markdown("""
    <style>
    .profile-view-hero {
        border-radius: 18px;
        padding: 22px;
        border: 1px solid rgba(110, 168, 254, 0.30);
        background: linear-gradient(120deg, rgba(92,174,255,0.22), rgba(168,85,247,0.18), rgba(16,185,129,0.14));
        margin-bottom: 16px;
    }
    .profile-panel {
        border-radius: 14px;
        border: 1px solid rgba(123,182,255,0.25);
        background: rgba(14, 25, 39, 0.70);
        padding: 16px;
        min-height: 210px;
    }
    .skill-pill {
        display:inline-block;
        margin:4px 8px 4px 0;
        padding:6px 11px;
        border-radius:999px;
        background:linear-gradient(90deg, rgba(92,174,255,0.24), rgba(16,185,129,0.24));
        border:1px solid rgba(167, 210, 255, 0.30);
        color:#EAF4FF;
        font-size:12px;
        font-weight:600;
    }
    </style>
    """, unsafe_allow_html=True)

    if not profile:
        st.warning("⚠️ Your profile is not set up yet.")
        if st.button("✨ Complete Profile", use_container_width=True):
            st.session_state.page = "profile_setup"; st.rerun()
    else:
        st.markdown("""
        <div class='profile-view-hero'>
            <h2 style='margin:0; color:#ffffff;'>My Professional Profile</h2>
            <p style='margin:6px 0 0 0; color:#E3EEFF;'>Keep your details updated to improve job matching and recruiter visibility.</p>
        </div>
        """, unsafe_allow_html=True)

        top_left, top_right = st.columns([1, 3])
        with top_left:
            avatar = profile.get("avatar")
            if avatar and os.path.exists(avatar):
                st.image(avatar, width=180)
            else:
                st.markdown(
                    """
                    <div style='height:180px; border-radius:14px; border:1px dashed rgba(167,210,255,0.4); display:flex; align-items:center; justify-content:center; color:#B8D8FF; background:rgba(92,174,255,0.08);'>
                        No Photo
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with top_right:
            st.markdown(f"### {profile.get('name', 'N/A')}")
            if profile.get("headline"):
                st.markdown(f"<p style='margin:0; color:#B7D7FF; font-weight:600;'>{profile.get('headline')}</p>", unsafe_allow_html=True)
            st.caption(f"User ID: {st.session_state.user_id}")
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            info_c1, info_c2, info_c3 = st.columns(3)
            with info_c1:
                st.markdown("**Phone**")
                st.write(profile.get("phone", "N/A"))
                st.markdown("**City**")
                st.write(profile.get("city", "N/A"))
            with info_c2:
                st.markdown("**Qualification**")
                st.write(profile.get("qualification", "N/A"))
                st.markdown("**Address**")
                st.write(profile.get("address", "N/A"))
            with info_c3:
                st.markdown("**Current Role**")
                st.write(profile.get("current_role", "N/A"))
                st.markdown("**Experience**")
                st.write(f"{profile.get('experience_years', 0)} years")

        link_col1, link_col2, link_col3 = st.columns(3)
        with link_col1:
            st.markdown("**LinkedIn**")
            st.write(profile.get("linkedin") or "N/A")
        with link_col2:
            st.markdown("**GitHub**")
            st.write(profile.get("github") or "N/A")
        with link_col3:
            st.markdown("**Portfolio**")
            st.write(profile.get("portfolio") or "N/A")

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        panel_left, panel_right = st.columns(2)
        with panel_left:
            st.markdown("<div class='profile-panel'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color:#A9D0FF; margin-top:0;'>🧠 Skills</h4>", unsafe_allow_html=True)
            skills = profile.get("skills", [])
            if skills:
                skills_html = "".join([f"<span class='skill-pill'>{s}</span>" for s in skills])
                st.markdown(skills_html, unsafe_allow_html=True)
            else:
                st.info("No skills added yet")
            st.markdown("</div>", unsafe_allow_html=True)

        with panel_right:
            st.markdown("<div class='profile-panel'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color:#A9D0FF; margin-top:0;'>🎯 Career Preferences</h4>", unsafe_allow_html=True)
            st.markdown(f"**Preferred Role:** {profile.get('preferred_role', 'N/A')}")
            st.markdown(f"**Preferred Location:** {profile.get('preferred_location', 'N/A')}")
            st.markdown(f"**Notice Period:** {profile.get('notice_period', 'N/A')}")
            st.markdown("<h4 style='color:#A9D0FF; margin-top:14px;'>📝 Summary</h4>", unsafe_allow_html=True)
            st.write(profile.get("bio") or "N/A")
            st.markdown("</div>", unsafe_allow_html=True)

    a1, a2 = st.columns(2)
    with a1:
        if st.button("✏️ Edit Profile", use_container_width=True):
            st.session_state.page = "profile_setup"; st.rerun()
    with a2:
        if st.button("⬅️ Back to Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"; st.rerun()

# ================= USER CHAT =================
elif st.session_state.page == "user_chat":
    user_chat_interface()
    if st.button("⬅️ Back to Dashboard", use_container_width=True):
        st.session_state.page = "dashboard"
        st.session_state.user_chat_page = "inbox"
        st.session_state.current_conversation = None
        st.rerun()

# ================= CHANGE PASSWORD =================
elif st.session_state.page == "change_password":
    st.markdown("<h2>Change Password</h2>", unsafe_allow_html=True)
    
    with st.form("change_password_form"):
        st.write("Create a new custom password for your account")
        old_password = st.text_input("Current Password", type="password", placeholder="Enter your current password")
        new_password = st.text_input("New Password", type="password", placeholder="Enter your new password")
        confirm_password = st.text_input("Confirm New Password", type="password", placeholder="Confirm your new password")
        submit_btn = st.form_submit_button("Update Password", use_container_width=True)
        
        if submit_btn:
            old_password_clean = old_password.strip()
            new_password_clean = new_password.strip()
            confirm_password_clean = confirm_password.strip()
            
            # Validation
            if not old_password_clean or not new_password_clean or not confirm_password_clean:
                st.error("❌ Please fill in all fields")
            elif new_password_clean != confirm_password_clean:
                st.error("❌ New passwords do not match")
            elif len(new_password_clean) < 4:
                st.error("❌ New password must be at least 4 characters long")
            else:
                # Try to change password
                with st.spinner("🔄 Updating your password..."):
                    result = change_password(st.session_state.user_id, old_password_clean, new_password_clean)
                    time.sleep(0.5)
                if result:
                    st.success("✅ Password changed successfully!")
                    st.info("💡 You can now login with your new password")
                else:
                    st.error("❌ Current password is incorrect")
    
    if st.button("⬅️ Back to Dashboard", use_container_width=True):
        st.session_state.page = "dashboard"; st.rerun()

# ================= FORGOT PASSWORD =================
elif st.session_state.page == "forgot_password":
    st.markdown("<h2>Forgot Password</h2>", unsafe_allow_html=True)
    st.write("Recover your account by resetting your password with your email address")
    
    tab1, tab2 = st.tabs(["Reset Password", "Find Your ID"])
    
    with tab1:
        st.info("""
        🔐 **Password Reset Process:**
        1. Enter your email address
        2. We'll generate a temporary password
        3. Use it to login
        4. Change it to your custom password in your dashboard
        """)
        
        with st.form("forgot_password_form"):
            email = st.text_input("Email Address", placeholder="your.email@example.com", help="Enter the email associated with your account")
            submit_btn = st.form_submit_button("Reset Password", use_container_width=True)
            
            if submit_btn:
                email_clean = email.strip().lower()
                if not email_clean or "@" not in email_clean:
                    st.error("❌ Please enter a valid email address")
                else:
                    with st.spinner("🔄 Resetting your password..."):
                        user_id, new_password = reset_password_by_email(email_clean)
                        time.sleep(0.5)
                    if user_id:
                        st.success("✅ Password Reset Successfully!")
                        st.markdown("---")
                        
                        creds_html = f"""
                        <div style='background: linear-gradient(135deg, rgba(56, 116, 184, 0.22), rgba(123, 182, 255, 0.12)); padding: 20px; border-radius: 12px; border: 2px solid rgba(123, 182, 255, 0.35);'>
                            <div style='text-align: center; margin-bottom: 15px;'>
                                <span style='color: #7BB6FF; font-weight: 700; font-size: 16px;'>🔐 Your Temporary Credentials</span>
                            </div>
                            <div style='display: flex; gap: 15px;'>
                                <div style='flex: 1; text-align: center; background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px;'>
                                    <div style='color: #7BB6FF; font-weight: 700; margin-bottom: 8px; font-size: 12px;'>USER ID</div>
                                    <pre style='background: transparent; color: #fff; font-size: 15px; padding: 0; margin: 0; word-wrap: break-word;'><strong>{user_id}</strong></pre>
                                </div>
                                <div style='flex: 1; text-align: center; background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px;'>
                                    <div style='color: #7BB6FF; font-weight: 700; margin-bottom: 8px; font-size: 12px;'>TEMPORARY PASSWORD</div>
                                    <pre style='background: transparent; color: #fff; font-size: 15px; padding: 0; margin: 0; word-wrap: break-word;'><strong>{new_password}</strong></pre>
                                </div>
                            </div>
                        </div>
                        """
                        st.markdown(creds_html, unsafe_allow_html=True)
                        
                        st.warning("⚠️ **IMPORTANT STEPS:**")
                        st.markdown("""
                        1. **Copy** your User ID and Temporary Password above
                        2. **Go back** to login page
                        3. **Login** with your User ID and this temporary password
                        4. **Navigate** to Dashboard → Change Password
                        5. **Create** a custom password you'll remember
                        """)
                    else:
                        st.error("❌ No account found with this email address")
                        st.info("💡 Please check that you entered the correct email address associated with your account")
    
    with tab2:
        st.info("""
        👤 **Find Your User ID:**
        If you remember your email but forgot your User ID, enter it below to retrieve your ID.
        """)
        
        user_email = st.text_input("Enter your email address:", placeholder="your.email@example.com", key="email_lookup", help="We'll find your User ID")
        
        if st.button("Find My User ID", use_container_width=True):
            user_email_clean = user_email.strip().lower()
            if not user_email_clean or "@" not in user_email_clean:
                st.error("❌ Please enter a valid email address")
            else:
                users = load_users()
                found = False
                for user_id, user_data in users.items():
                    if user_data.get("email") == user_email_clean:
                        st.success(f"✅ Account Found!")
                        
                        id_html = f"""
                        <div style='background: linear-gradient(135deg, rgba(56, 116, 184, 0.22), rgba(123, 182, 255, 0.12)); padding: 20px; border-radius: 12px; border: 2px solid rgba(123, 182, 255, 0.35); text-align: center;'>
                            <div style='color: #7BB6FF; font-weight: 700; margin-bottom: 12px;'>Your User ID</div>
                            <pre style='background: rgba(0,0,0,0.3); color: #fff; padding: 12px; border-radius: 8px; font-size: 18px; margin: 0;'><strong>{user_id}</strong></pre>
                        </div>
                        """
                        st.markdown(id_html, unsafe_allow_html=True)
                        
                        st.markdown("---")
                        st.info("💡 Now go to the **Reset Password** tab above to reset your password")
                        found = True
                        break
                
                if not found:
                    st.error("❌ No account found with this email address")
    
    if st.button("⬅️ Back to Login", use_container_width=True):
        st.session_state.page = "login"; st.rerun()

# ================= HOST AUTH =================
elif st.session_state.page == "host_auth":
    st.markdown("""
    <div style='text-align:center'>
      <h2 style='margin-bottom:6px;'>Host Portal</h2>
      <p style='color:#e0e0e0;margin-top:0;'>Manage your job postings and review candidates with AI-assist tools</p>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1.1, 1])

    with left:
        st.markdown("""
        <div style='background: rgba(255,255,255,0.06); padding:20px; border-radius:12px;'>
            <h3 style='color:#A8D5BA; margin-bottom:8px;'>Why use Host Portal?</h3>
            <ul style='color:#d0d0d0; line-height:1.6;'>
                <li>Post and manage job openings quickly</li>
                <li>Review candidate resumes and AI match scores</li>
                <li>Invite candidates and track applications in one place</li>
            </ul>
            <hr style='border-color: rgba(255,255,255,0.06);'/>
            <p style='color:#d0d0d0;'>Need help? Contact support at <strong style='color:#fff;'>support@airesume.example</strong></p>
        </div>
        """, unsafe_allow_html=True)

    with right:
        tab1, tab2 = st.tabs(["Sign In", "Create Host"])

        with tab1:
            with st.form("host_login_form"):
                hid = st.text_input("Host ID", placeholder="e.g., HOST1234")
                pwd = st.text_input("Password", type="password", placeholder="Enter your password")
                submit = st.form_submit_button("Sign In", use_container_width=True)
                if submit:
                    hid_clean = (hid or "").strip()
                    pwd_clean = (pwd or "").strip()
                    if not hid_clean or not pwd_clean:
                        st.error("Please enter both Host ID and Password")
                    else:
                        with st.spinner("🔐 Authenticating host..."):
                            result = login_host(hid_clean, pwd_clean)
                            time.sleep(0.3)
                        if result:
                            st.success("✅ Signed in successfully")
                            st.session_state.current_host_id = hid_clean
                            st.session_state.page = "host_dashboard"; st.rerun()
                        else:
                            st.error("Invalid host credentials")
            
            st.markdown("<div style='text-align: center; margin: 20px 0;'></div>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔑 Forgot Password?", use_container_width=True, key="host_forgot_pwd"):
                    st.session_state.page = "host_forgot_password"; st.rerun()

        with tab2:
            st.info("""
            📋 **Requirements:**
            - **Admin Access Key**: Required for security (contact administrator)
            - **Host ID**: 4-15 characters (letters, numbers, underscore only)
            - **Password**: 6-20 characters (must include at least 1 letter and 1 number)
            """)
            
            with st.form("host_create_form"):
                admin_key = st.text_input("Admin Access Key", type="password", placeholder="Enter admin access key", help="Contact administrator for the access key")
                email = st.text_input("Official Email", placeholder="admin@company.com")
                host_id = st.text_input("Create Host ID", placeholder="company_name123", help="4-15 characters (letters, numbers, _)")
                password = st.text_input("Create Password", type="password", placeholder="SecurePass123", help="6-20 chars, must have letters & numbers")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="SecurePass123")
                create = st.form_submit_button("Create Host Account", use_container_width=True)
                
                if create:
                    admin_key_clean = (admin_key or "").strip()
                    email_clean = (email or "").strip().lower()
                    host_id_clean = (host_id or "").strip()
                    password_clean = (password or "").strip()
                    confirm_password_clean = (confirm_password or "").strip()
                    
                    # Validate inputs
                    if not admin_key_clean:
                        st.error("❌ Please enter the Admin Access Key")
                    elif not email_clean or "@" not in email_clean:
                        st.error("❌ Please enter a valid email address")
                    elif password_clean != confirm_password_clean:
                        st.error("❌ Passwords do not match")
                    else:
                        hid_new, result_msg = create_host(email_clean, host_id_clean, password_clean, admin_key_clean)
                        if hid_new:
                            st.success("✅ Host account created successfully!")
                            creds_html = f"""
                            <div style='background: rgba(0,0,0,0.75); padding: 16px; border-radius: 10px; display:flex; gap:12px; align-items:center; justify-content:center;'>
                                <div style='flex:1; text-align:center;'>
                                    <div style='color:#A8D5BA; font-weight:700; margin-bottom:6px;'>Your Host ID</div>
                                    <pre style='background:transparent; color:#fff; font-size:14px; padding:8px; border-radius:6px; margin:0;'>{hid_new}</pre>
                                </div>
                                <div style='flex:1; text-align:center;'>
                                    <div style='color:#A8D5BA; font-weight:700; margin-bottom:6px;'>Your Password</div>
                                    <pre style='background:transparent; color:#fff; font-size:14px; padding:8px; border-radius:6px; margin:0;'>{result_msg}</pre>
                                </div>
                            </div>
                            """
                            st.markdown(creds_html, unsafe_allow_html=True)
                            st.info("💡 Save your credentials. You can now sign in with your Host ID and Password")
                        else:
                            st.error(f"{result_msg}")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    if st.button("⬅️ Back to Roles", use_container_width=True):
        st.session_state.page = "role"; st.rerun()

# ================= HOST FORGOT PASSWORD =================
elif st.session_state.page == "host_forgot_password":
    st.markdown("<h2>Forgot Host Password</h2>", unsafe_allow_html=True)
    st.write("Recover your host account by resetting your password with your email address")
    
    tab1, tab2 = st.tabs(["Reset Password", "Find Your Host ID"])
    
    with tab1:
        st.info("""
        🔐 **Password Reset Process:**
        1. Enter your email address
        2. We'll generate a temporary password
        3. Use it to sign in
        4. Change it to your custom password
        """)
        
        with st.form("host_forgot_password_form"):
            email = st.text_input("Email Address", placeholder="admin@company.com", help="Enter the email associated with your host account", key="host_email_reset")
            submit_btn = st.form_submit_button("Reset Password", use_container_width=True)
            
            if submit_btn:
                email_clean = email.strip().lower()
                if not email_clean or "@" not in email_clean:
                    st.error("❌ Please enter a valid email address")
                else:
                    host_id, new_password = reset_host_password_by_email(email_clean)
                    if host_id:
                        st.success("✅ Password Reset Successfully!")
                        st.markdown("---")
                        
                        creds_html = f"""
                        <div style='background: linear-gradient(135deg, rgba(31, 107, 79, 0.2), rgba(168, 213, 186, 0.1)); padding: 20px; border-radius: 12px; border: 2px solid rgba(168, 213, 186, 0.3);'>
                            <div style='text-align: center; margin-bottom: 15px;'>
                                <span style='color: #A8D5BA; font-weight: 700; font-size: 16px;'>🔐 Your Temporary Credentials</span>
                            </div>
                            <div style='display: flex; gap: 15px;'>
                                <div style='flex: 1; text-align: center; background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px;'>
                                    <div style='color: #A8D5BA; font-weight: 700; margin-bottom: 8px; font-size: 12px;'>HOST ID</div>
                                    <pre style='background: transparent; color: #fff; font-size: 15px; padding: 0; margin: 0; word-wrap: break-word;'><strong>{host_id}</strong></pre>
                                </div>
                                <div style='flex: 1; text-align: center; background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px;'>
                                    <div style='color: #A8D5BA; font-weight: 700; margin-bottom: 8px; font-size: 12px;'>TEMPORARY PASSWORD</div>
                                    <pre style='background: transparent; color: #fff; font-size: 15px; padding: 0; margin: 0; word-wrap: break-word;'><strong>{new_password}</strong></pre>
                                </div>
                            </div>
                        </div>
                        """
                        st.markdown(creds_html, unsafe_allow_html=True)
                        
                        st.warning("⚠️ **IMPORTANT STEPS:**")
                        st.markdown("""
                        1. **Copy** your Host ID and Temporary Password above
                        2. **Go back** to the Host Portal
                        3. **Sign In** with your Host ID and this temporary password
                        4. **Navigate** to Host Dashboard → Change Password (if available)
                        5. **Create** a custom password you'll remember
                        """)
                    else:
                        st.error("❌ No host account found with this email address")
                        st.info("💡 Please check that you entered the correct email address associated with your host account")
    
    with tab2:
        st.info("""
        👤 **Find Your Host ID:**
        If you remember your email but forgot your Host ID, enter it below to retrieve your ID.
        """)
        
        host_email = st.text_input("Enter your email address:", placeholder="admin@company.com", key="host_email_lookup", help="We'll find your Host ID")
        
        if st.button("Find My Host ID", use_container_width=True):
            host_email_clean = host_email.strip().lower()
            if not host_email_clean or "@" not in host_email_clean:
                st.error("❌ Please enter a valid email address")
            else:
                hosts = load_hosts()
                found = False
                for host_id, host_data in hosts.items():
                    if host_data.get("email") == host_email_clean:
                        st.success(f"✅ Host Account Found!")
                        
                        id_html = f"""
                        <div style='background: linear-gradient(135deg, rgba(31, 107, 79, 0.2), rgba(168, 213, 186, 0.1)); padding: 20px; border-radius: 12px; border: 2px solid rgba(168, 213, 186, 0.3); text-align: center;'>
                            <div style='color: #A8D5BA; font-weight: 700; margin-bottom: 12px;'>Your Host ID</div>
                            <pre style='background: rgba(0,0,0,0.3); color: #fff; padding: 12px; border-radius: 8px; font-size: 18px; margin: 0;'><strong>{host_id}</strong></pre>
                        </div>
                        """
                        st.markdown(id_html, unsafe_allow_html=True)
                        
                        st.markdown("---")
                        st.info("💡 Now go to the **Reset Password** tab above to reset your password")
                        found = True
                        break
                
                if not found:
                    st.error("❌ No host account found with this email address")
    
    if st.button("⬅️ Back to Host Portal", use_container_width=True):
        st.session_state.page = "host_auth"; st.rerun()

# ================= HOST DASHBOARD =================
elif st.session_state.page == "host_dashboard":
    host_dashboard()
