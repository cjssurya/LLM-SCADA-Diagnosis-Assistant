from fpdf import FPDF
import matplotlib.pyplot as plt

def generate_pdf_report(well, analysis, graph_fig, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_text_color(0)
    pdf.cell(200, 10, txt="SCADA Well Report", ln=1, align='C')

    # Well data
    pdf.set_font("Arial", size=11)
    pdf.ln(5)
    for key, val in well.items():
        pdf.cell(200, 8, f"{key}: {val}", ln=1)

    # Save and insert graph
    img_path = "temp_graph.png"
    graph_fig.savefig(img_path)
    pdf.image(img_path, x=30, y=pdf.get_y(), w=150)
    pdf.ln(80)

    # AI Response
    pdf.multi_cell(0, 10, analysis)

    pdf.output(filename)
