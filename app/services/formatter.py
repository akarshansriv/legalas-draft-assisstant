from utils.doc_exporter import export_to_docx


def format_petition(text: str, case_type: str) -> str:
    # Optionally parse text and structure into headings
    return export_to_docx(text)
