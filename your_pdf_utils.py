from fpdf import FPDF
import matplotlib.pyplot as plt
from io import BytesIO

def generate_pdf_report(well, analysis, graph_fig, buffer: BytesIO):
    pdf = FPDF()
    pdf.add_page()
    
    # Unicode font (make sure DejaVuSans.ttf is in your project folder)
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=12)
    
    pdf.set_text_color(0)
    pdf.cell(200, 10, txt="SCADA Well Report", ln=1, align='C')

    # Well data
    pdf.set_font("DejaVu", size=11)
    pdf.ln(5)
    for key, val in well.items():
        pdf.cell(200, 8, f"{key}: {val}", ln=1)

    # Save and insert graph
    img_path = "temp_graph.png"
    graph_fig.savefig(img_path)
    pdf.image(img_path, x=30, y=pdf.get_y(), w=150)
    pdf.ln(80)

    # AI Response (supports Unicode)
    pdf.multi_cell(0, 10, analysis)

    # Save PDF into BytesIO buffer
    pdf_bytes = pdf.output(dest="S").encode("latin1") if isinstance(pdf.output(dest="S"), str) else pdf.output(dest="S")
    buffer.write(pdf_bytes)
