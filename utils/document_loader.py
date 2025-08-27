from io import BytesIO
from pdfminer.high_level import extract_text
from docx import Document
import PyPDF2
from fastapi import UploadFile
from typing import Union

def load_pdf(file_bytes: bytes) -> str:
    """Load PDF using pdfminer for better text extraction"""
    with BytesIO(file_bytes) as f:
        text = extract_text(f)
    return text

def load_pdf_pypdf2(file_bytes: bytes) -> str:
    """Load PDF using PyPDF2 as fallback"""
    pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
    return "\n".join(
        page.extract_text() for page in pdf_reader.pages if page.extract_text()
    )

def load_docx(file_bytes: bytes) -> str:
    """Load DOCX files"""
    with BytesIO(file_bytes) as f:
        doc = Document(f)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
    return "\n".join(full_text)

def load_txt(file_bytes: bytes) -> str:
    """Load text files"""
    return file_bytes.decode("utf-8", errors="replace")

def load_file(file: Union[UploadFile, any]) -> str:
    """Load file content - handles both UploadFile and file-like objects"""
    if hasattr(file, 'filename') and hasattr(file, 'file'):
        # UploadFile object
        ext = file.filename.split('.')[-1].lower()
        raw = file.file.read()
    else:
        # File-like object
        ext = getattr(file, 'name', '').split('.')[-1].lower()
        raw = file.read()
    
    if ext in ['pdf']:
        try:
            return load_pdf(raw)
        except Exception:
            # Fallback to PyPDF2
            return load_pdf_pypdf2(raw)
    elif ext in ['docx', 'doc']:
        return load_docx(raw)
    elif ext in ['txt']:
        return load_txt(raw)
    else:
        return raw.decode('utf-8', errors='replace')

async def load_file_async(file: UploadFile) -> str:
    """Async version of load_file for UploadFile objects"""
    ext = file.filename.split('.')[-1].lower()
    raw = await file.read()
    
    if ext in ['pdf']:
        try:
            return load_pdf(raw)
        except Exception:
            # Fallback to PyPDF2
            return load_pdf_pypdf2(raw)
    elif ext in ['docx', 'doc']:
        return load_docx(raw)
    elif ext in ['txt']:
        return load_txt(raw)
    else:
        return raw.decode('utf-8', errors='replace')