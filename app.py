import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
import requests
import json
import tempfile
from PIL import Image
import base64
from your_pdf_utils import generate_pdf_report  # You must have this function ready

# --- CONFIG ---
st.set_page_config(page_title="SCADA Well Analysis Assistant", layout="centered")

CSV_FILE = "scada_dataset.csv"
API_KEY = "AIzaSyD2ainAtqFa3NFX2R1f-zdsSLn-F7kfyuI"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_FILE)
    df['Well ID'] = df['Well ID'].astype(str).str.lower().str.strip()
    return df

# --- NORMALIZE ---
def normalize_well_id(well_id):
    digits = re.findall(r'\d+', well_id)
    return f"well {digits[0]}".lower() if digits else well_id.lower().strip()

def get_well_row(df, user_input):
    normalized = normalize_well_id(user_input)
    match = df[df['Well ID'] == normalized]
    return match.iloc[0] if not match.empty else None

# --- GEMINI PROMPT ---
def create_prompt(well):
    return f"""
You are an expert SCADA engineer. Analyze this data and give 3 sections:

WELL INFORMATION:
- Well ID: {well['Well ID']}
- Temperature: {well['Temperature']}°F
- Pressure: {well['Pressure']} PSI
- Flow Rate: {well['Flow Rate']} barrels/day
- Vibration: {well['Vibration']} Hz
- Humidity: {well['Humidity']}%
- Fault Detected: {well['Fault Detected']}
- Suggested Action: {well['Suggested Action']}

Respond with:
1. **Fault Diagnosis (5–10 lines)**
2. **Required Action (5–10 lines)**
3. **Conclusion (2–5 lines)**
"""

# --- GEMINI API CALL ---
def query_gemini(prompt):
    headers = {'Content-Type': 'application/json', 'X-goog-api-key': API_KEY}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 1024
        }
    }
    response = requests.post(GEMINI_URL, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        content = response.json()['candidates'][0]['content']['parts'][0]['text']
        return content
    return "❌ Gemini analysis failed."

# --- GRAPHS ---
def plot_graphs(well):
    fig, axs = plt.subplots(1, 3, figsize=(15, 4))
    axs[0].bar(['Temp'], [well['Temperature']])
    axs[0].set_title("Temperature (°F)")
    axs[1].bar(['Pressure'], [well['Pressure']])
    axs[1].set_title("Pressure (PSI)")
    axs[2].bar(['Vibration'], [well['Vibration']])
    axs[2].set_title("Vibration (Hz)")
    st.pyplot(fig)
    return fig

# --- EMBED LOGO ---
def get_image_base64(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
        return base64.b64encode(data).decode()

logo_base64 = get_image_base64("ongc_logo.png")

# --- HEADER HTML ---
# --- HEADER HTML ---
st.markdown(f"""
    <style>
        .header {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background-color: #8B0000;
            padding: 15px 20px;
            z-index: 1000;
            display: flex;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }}
        .header img {{
            height: 50px;
            margin-right: 15px;
        }}
        .header h1 {{
            font-size: 26px;
            color: white;
            margin: 0;
        }}
        .main-content {{
            margin-top: 100px; /* INCREASED FROM 80px TO 120px */
            padding: 1.5rem;
        }}
        #MainMenu, footer {{visibility: hidden;}}
        body {{ overflow-x: hidden; }}
    </style>
    <div class="header">
        <img src="data:image/png;base64,{logo_base64}" />
        <h1>ONGC SCADA Well Analysis Assistant</h1>
    </div>
    <div class="main-content">
""", unsafe_allow_html=True)

# --- MAIN APP START ---
st.title("🔍 SCADA Well Analysis Assistant")

df = load_data()

well_input = st.text_input("Enter Well ID (e.g., 100 or WELL 100):")

if well_input:
    well = get_well_row(df, well_input)
    if well is not None:
        st.subheader("📊 Well Sensor Data")
        st.table(well)

        st.subheader("📈 Parameter Graphs")
        graph_fig = plot_graphs(well)

        st.subheader("🤖 Gemini AI Fault Diagnosis")
        prompt = create_prompt(well)
        with st.spinner("Analyzing using Gemini..."):
            ai_result = query_gemini(prompt)
        st.text_area("Gemini Analysis", ai_result, height=400)

        if st.checkbox("📄 Generate PDF report?"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                generate_pdf_report(well, ai_result, graph_fig, tmp.name)
                st.success("PDF generated!")
                with open(tmp.name, "rb") as f:
                    st.download_button("📥 Download PDF", f, file_name="Well_Report.pdf")
    else:
        st.warning("Well ID not found. Try again.")

# Close floating div
st.markdown("</div>", unsafe_allow_html=True)
