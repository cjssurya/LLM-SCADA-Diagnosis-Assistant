import streamlit as st
import base64
from PIL import Image
from dotenv import load_dotenv
from datetime import datetime
from io import BytesIO

from your_pdf_utils import generate_pdf_report
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

def render_header():
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
            <span>👤 Guest</span>
        </div>
    </div>
    <div class="main-content">
    """

# Always show header
st.markdown(render_header(), unsafe_allow_html=True)

# Dashboard
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

        # 📌 PDF Report Button
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
