from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from utils.document_loader import load_file_async
from utils.rag import RAGIndex
from app.services.draft_generator import generate_petition
from app.services.rag_service import ingest_documents, get_permanent_vector_store, load_permanent_kb

router = APIRouter()


@router.post("/ingest")
async def ingest(files: List[UploadFile] = File(...)):
    """
    Permanently ingest uploaded documents into the KB
    """
    docs = []
    for f in files:
        try:
            text = await load_file_async(f)
            docs.append({"source": f.filename, "text": text})
        except Exception as e:
            # Skip unreadable files
            continue
    if not docs:
        return JSONResponse({"message": "No valid files to ingest"}, status_code=400)

    ingest_documents(
        docs, permanent=True
    )  # Make sure ingest_documents stores permanently
    return JSONResponse({"message": f"{len(docs)} documents ingested successfully"})


@router.post("/generate")
async def generate(
    draft_type: str = Form(...),
    petitioner: str = Form(...),
    respondent: str = Form(...),
    court_name: str = Form(...),
    jurisdiction: str = Form(...),
    case_type: str = Form(...),
    key_dates: str = Form(""),
    relief_sought: str = Form(""),
    legal_articles: str = Form(""),
    rules_to_follow: str = Form(""),
    case_summary: str = Form(""),
    files: Optional[List[UploadFile]] = File(None),
    download: bool = Form(True),
):
    # 1) Load permanent KB docs into the RAG index
    permanent_docs = (
        load_permanent_kb()
    )  # This function should return list of {source, text}
    if permanent_docs:
        ingest_documents(permanent_docs)

    # 2) Ingest uploaded reference documents into the RAG index
    docs = []
    if files:
        for f in files:
            try:
                text = await load_file_async(f)
                docs.append({"source": f.filename, "text": text})
            except Exception:
                # skip unreadable files
                continue
    if docs:
        ingest_documents(docs)

    # 3) Build payload for generator
    payload = {
        "draft_type": draft_type,
        "petitioner": petitioner,
        "respondent": respondent,
        "court_name": court_name,
        "jurisdiction": jurisdiction,
        "case_type": case_type,
        "key_dates": [d.strip() for d in key_dates.split(",") if d.strip()],
        "relief_sought": relief_sought,
        "legal_articles": [a.strip() for a in legal_articles.split(",") if a.strip()],
        "rules_to_follow": [r.strip() for r in rules_to_follow.split(",") if r.strip()],
        "case_summary": case_summary,
    }

    # 4) Generate draft and return DOCX or JSON
    result = generate_petition(payload)
    if download and result.get("file_path"):
        return FileResponse(path=result["file_path"], filename="petition.docx")
    return JSONResponse({"petition": result.get("petition", "")})
