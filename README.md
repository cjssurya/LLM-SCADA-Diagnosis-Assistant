# LLM-SCADA-Diagnosis-Assistant ⚙️🤖

LLM-SCADA-Diagnosis-Assistant is an AI-powered diagnostic assistant designed to analyze SCADA system data and provide intelligent insights for fault detection and operational analysis.  
The project integrates Large Language Models (LLMs) with industrial SCADA data to help engineers understand system behavior, identify anomalies, and generate human-readable explanations.

This project was developed as part of an industrial internship to explore the application of AI in real-time monitoring and diagnostics.

---

## 🚀 Key Features

- SCADA data analysis using historical sensor data
- AI-driven diagnostic insights using LLMs
- Interactive web interface built with Streamlit
- Automated report and explanation generation
- Visualization of trends and anomalies
- Modular utility-based design for scalability

---

## 🛠️ Tech Stack

### Programming & Frameworks
- Python
- Streamlit

### AI / Data Processing
- Large Language Models (LLMs)
- Pandas
- NumPy

### Visualization
- Matplotlib

### Data Storage
- CSV-based datasets (SCADA logs)

---

## 📂 Project Structure

LLM-SCADA-Diagnosis-Assistant/
├── .devcontainer/ # Development container configuration
├── .streamlit/ # Streamlit configuration
├── app.py # Main Streamlit application
├── auth_utils.py # Authentication utilities (currently disabled)
├── email_utils.py # Email-related helper functions
├── scada_utils.py # SCADA data processing utilities
├── your_pdf_utils.py # PDF generation utilities
├── test_db.py # Database testing script
├── requirements.txt # Project dependencies
├── scada_dataset.csv # Sample SCADA dataset
├── ongc_logo.png # Branding asset
├── temp_graph.png # Generated visualization output
└── README.md

yaml
Copy code

---

## ⚙️ Installation & Setup

1. Clone the repository
   ```bash
   git clone https://github.com/cjssurya/LLM-SCADA-Diagnosis-Assistant.git
Navigate to the project directory

bash
Copy code
cd LLM-SCADA-Diagnosis-Assistant
Install required dependencies

bash
Copy code
pip install -r requirements.txt
Run the application

bash
Copy code
streamlit run app.py
Open your browser and visit

arduino
Copy code
http://localhost:8501
