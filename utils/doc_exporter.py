from docx import Document
from docx.shared import Inches, Pt
from docx.oxml.ns import qn
import os


def export_to_docx(text: str, filename: str = "petition.docx") -> str:
    doc = Document()

    # Set page margins (1 inch all around)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Define a consistent paragraph style
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Times New Roman"
    font.size = Pt(12)

    # Apply formatting to each paragraph
    for para in text.strip().split("\n"):
        if para.strip() == "":
            doc.add_paragraph()
        else:
            p = doc.add_paragraph(para.strip())
            p.paragraph_format.first_line_indent = Inches(0.25)
            p.paragraph_format.space_after = Pt(8)

    # Save document
    os.makedirs("temp", exist_ok=True)
    output_path = os.path.join("temp", filename)
    doc.save(output_path)
    return output_path
