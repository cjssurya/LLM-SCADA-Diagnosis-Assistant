import streamlit as st
import base64
from PIL import Image
from dotenv import load_dotenv
from datetime import datetime
from io import BytesIO

from auth_utils import get_user, verify_password, register_user
from your_pdf_utils import generate_pdf_report
from email_utils import send_email
from scada_utils import (
    load_data,
    get_well_row,
    create_prompt,
    query_gemini,
    plot_graphs
)

# Load environment variables
load_dotenv()

st.set_page_config(page_title="LLM-Powered SCADA Well Analysis", layout="wide")

def load_ongc_logo():
    with open("ongc_logo.png", "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

logo_base64 = load_ongc_logo()

def render_header(username):
    return f"""
    <style>
        .header {{
            position: fixed;
            top: 60px;
            left: 0;
            width: 100%;
            background-color: #8B0000;
            padding: 8px 20px;
            z-index: 1000;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }}
        .header-left {{
            display: flex;
            align-items: center;
        }}
        .header-left img {{
            height: 35px;
            margin-right: 15px;
        }}
        .header-left h1 {{
            font-size: 18px;
            color: white;
            margin: 0;
        }}
        .header-right {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        .header-right span {{
            color: white;
            font-size: 16px;
        }}
        .header-right button {{
            background-color: white;
            border: none;
            color: #8B0000;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }}
        .main-content {{
            margin-top: 40px;
            padding: 1.5rem;
            max-width: 100%;
        }}
        body {{
            margin: 0;
            padding: 0;
            overflow-x: hidden;
        }}
        #MainMenu, footer {{visibility: hidden;}}
    </style>
    <div class="header">
        <div class="header-left">
            <img src="data:image/png;base64,{logo_base64}" />
            <h1>ONGC SCADA Well Analysis Assistant</h1>
        </div>
        <div class="header-right">
            <span>👤 {username}</span>
            <form action="?logout=" method="get">
                <button type="submit">Logout</button>
            </form>
        </div>
    </div>
    <div class="main-content">
    """

# Session state initialization
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# Logout handler
if st.query_params.get("logout") == [""]:
    st.session_state.auth = False
    st.session_state.username = ""
    st.rerun()

# Always show header
if st.session_state.auth:
    st.markdown(render_header(st.session_state.username), unsafe_allow_html=True)
else:
    st.markdown(render_header("Guest"), unsafe_allow_html=True)

# Auth pages
if not st.session_state.auth:
    st.title("🔐 Login or Register")
    auth_mode = st.radio("Choose mode", ["Login", "Register"], horizontal=True)

    if auth_mode == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = get_user(username)
            if user and verify_password(password, user[3]):
                st.session_state.auth = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password.")

    elif auth_mode == "Register":
        name = st.text_input("Full Name")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Register"):
            if register_user(name, username, password):
                st.success("Registration successful. You can log in now.")
            else:
                st.error("Username already exists. Try another.")

# Dashboard page
else:
    st.subheader("🛠 SCADA Analysis Dashboard")
    st.write("Enter a Well ID to analyze SCADA sensor data.")

    well_input = st.text_input("Enter Well ID (e.g., 100 or WELL 100):")
    df = load_data()

    if well_input.strip() != "":
        well = get_well_row(df, well_input)
        if well is not None:
            st.subheader("📊 Well Sensor Data")
            st.table(well)

            st.subheader("📈 Sensor Graphs")
            fig = plot_graphs(well)
            st.pyplot(fig)

            st.subheader("🤖 Gemini Fault Diagnosis")
            prompt = create_prompt(well)

            with st.spinner("Analyzing with Gemini..."):
                result = query_gemini(prompt)

            st.markdown(
                f"""
                <div style='background-color:#f0f0f5; padding:20px; border-radius:10px; max-height:auto; overflow-y:auto; border:1px solid #ccc;'>
                <pre style='white-space:pre-wrap; font-size:15px; color:#333;'>{result}</pre>
                </div>
                """,
                unsafe_allow_html=True
            )

            # 📌 Download PDF Button (integrated with your_pdf_utils.py)
            if st.button("📄 Generate PDF Report"):
                buffer = BytesIO()
                generate_pdf_report(well, result, fig, buffer)
                buffer.seek(0)
                st.download_button(
                    label="⬇️ Download PDF",
                    data=buffer,
                    file_name=f"SCADA_Report_{well_input}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )

        else:
            st.warning("⚠️ Well ID not found. Please try again.")
