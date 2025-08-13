# scada_utils.py
import pandas as pd
import re
import requests
import matplotlib.pyplot as plt

# Constants
CSV_FILE = "scada_dataset.csv"
API_KEY = "AIzaSyD2ainAtqFa3NFX2R1f-zdsSLn-F7kfyuI"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Load CSV
def load_data():
    df = pd.read_csv(CSV_FILE)
    df['Well ID'] = df['Well ID'].astype(str).str.lower().str.strip()
    return df

# Normalize Well ID
def normalize_well_id(well_id):
    digits = re.findall(r'\d+', well_id)
    return f"well {digits[0]}".lower() if digits else well_id.lower().strip()

# Find Well Row
def get_well_row(df, user_input):
    normalized = normalize_well_id(user_input)
    match = df[df['Well ID'] == normalized]
    return match.iloc[0] if not match.empty else None

# Create prompt for Gemini
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

# Gemini API call
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
    response = requests.post(GEMINI_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    return "❌ Gemini analysis failed."

# Plot graphs
def plot_graphs(well):
    fig, axs = plt.subplots(1, 3, figsize=(15, 4))
    axs[0].bar(['Temp'], [well['Temperature']])
    axs[0].set_title("Temperature (°F)")
    axs[1].bar(['Pressure'], [well['Pressure']])
    axs[1].set_title("Pressure (PSI)")
    axs[2].bar(['Vibration'], [well['Vibration']])
    axs[2].set_title("Vibration (Hz)")
    return fig
