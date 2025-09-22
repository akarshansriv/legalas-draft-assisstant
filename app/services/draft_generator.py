import os
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from app.services.rag_service import retrieve_context
from utils.doc_exporter import export_to_docx


with open("prompts/base_prompt.txt") as f:
    BASE_PROMPT = f.read()


def build_context_text(retrieved: list) -> str:
    if not retrieved:
        return ""
    parts = []
    for r in retrieved:
        parts.append(f"Source: {r['source']}\n{r['text']}")
    return "\n\n".join(parts)


def _load_style_reference(draft_type: str) -> str:
    """Return a short excerpt from the matching sample to guide structure."""
    if not draft_type:
        return ""
    mapping = {
        "writ_petition": "writ_petition_sample.pdf",
        "review_petition": "review_petition_sample.pdf",
        "curative_petition": "curative_petition_sample.pdf",
        "civil_suit": "civil_suit_sample.pdf",
        "bail_application_regular": "bail_application_regular_sample.pdf",
        "bail_application_anticipatory": "bail_application_anticipatory_sample.pdf",
    }
    # normalize
    normalized = draft_type.strip().lower().replace(" ", "_")
    filename = mapping.get(normalized)
    if not filename:
        # fallback heuristics
        if "writ" in normalized:
            filename = mapping["writ_petition"]
        elif "review" in normalized:
            filename = mapping["review_petition"]
        elif "curative" in normalized:
            filename = mapping["curative_petition"]
        elif "suit" in normalized or "civil" in normalized:
            filename = mapping["civil_suit"]
        elif "bail" in normalized and "regular" in normalized:
            filename = mapping["bail_application_regular"]
        elif "bail" in normalized and "anticipatory" in normalized:
            filename = mapping["bail_application_anticipatory"]
        else:
            return ""
    # Try new folder structure first, then fallback to flat structure
    folder_name = normalized.replace("_", " ")
    folder_path = os.path.join("sample_petitions", folder_name, filename)
    flat_path = os.path.join("sample_petitions", filename)
    
    for path in [folder_path, flat_path]:
        try:
            if path.lower().endswith('.docx'):
                # Load DOCX file
                from utils.document_loader import load_docx
                with open(path, "rb") as f:
                    text = load_docx(f.read()).strip()
            elif path.lower().endswith('.pdf'):
                # Load PDF file with OCR support using pymupdf4llm
                from utils.document_loader import load_pdf_pymupdf4llm
                with open(path, "rb") as f:
                    text = load_pdf_pymupdf4llm(f.read()).strip()
            else:
                # Load TXT file
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read().strip()
            # Use only the first ~2500 chars as style reference to avoid copying content
            return text[:2500]
        except Exception:
            continue
    return ""


def _extract_annexure_description(filename: str, content: str) -> str:
    """Extract a brief description for the annexure from filename or content."""
    # Clean filename
    clean_name = filename.replace(".pdf", "").replace(".docx", "").replace(".txt", "").replace("_", " ").replace("-", " ")
    
    # Try to extract meaningful information from filename
    if "letter" in clean_name.lower():
        return f"Copy of the letter {clean_name}"
    elif "deed" in clean_name.lower():
        return f"Copy of the {clean_name}"
    elif "order" in clean_name.lower():
        return f"Copy of the order {clean_name}"
    elif "notice" in clean_name.lower():
        return f"Copy of the notice {clean_name}"
    elif "judgement" in clean_name.lower() or "judgment" in clean_name.lower():
        return f"Copy of the judgement and order {clean_name}"
    elif "medical" in clean_name.lower():
        return f"Copy of the medical papers {clean_name}"
    elif "receipt" in clean_name.lower():
        return f"Copy of the receipts {clean_name}"
    elif "photo" in clean_name.lower():
        return f"Copy of the photographs {clean_name}"
    else:
        return f"Copy of the {clean_name}"


def generate_petition(data: dict):
    # data is dict from route
    query_for_retrieval = data.get("case_summary") or " ".join(
        data.get("key_dates", [])
    )
    
    # Get draft_type for context filtering
    draft_type = data.get("draft_type", "")
    
    # Retrieve context with draft_type filtering to get relevant sample petitions
    retrieved = retrieve_context(query_for_retrieval, top_k=6, draft_type=draft_type)
    context_text = build_context_text(retrieved)

    style_reference = _load_style_reference(draft_type)
    
    # Process annexure files
    annexure_files = data.get("annexure_files", [])
    annexure_info = ""
    if annexure_files:
        annexure_info = "\n\nANNEXURE INFORMATION:\n"
        for i, annexure in enumerate(annexure_files, 1):
            filename = annexure.get("source", f"Annexure_{i}")
            # Extract a brief description from the filename or content
            description = _extract_annexure_description(filename, annexure.get("text", ""))
            annexure_info += f"ANNEXURE NO. {i}: {description}\n"

    # Format multiple petitioners and respondents
    petitioners_list = data.get("petitioners", [])
    respondents_list = data.get("respondents", [])
    
    # Format petitioners
    if petitioners_list:
        if len(petitioners_list) == 1:
            petitioners_formatted = petitioners_list[0]
        else:
            petitioners_formatted = " AND ".join(petitioners_list)
    else:
        petitioners_formatted = "Petitioner"
    
    # Format respondents
    if respondents_list:
        if len(respondents_list) == 1:
            respondents_formatted = respondents_list[0]
        else:
            respondents_formatted = " AND ".join(respondents_list)
    else:
        respondents_formatted = "Respondent"

    filled_prompt = BASE_PROMPT.format(
        draft_type=data.get("draft_type"),
        petitioners=petitioners_formatted,
        respondents=respondents_formatted,
        court_name=data.get("court_name"),
        jurisdiction=data.get("jurisdiction"),
        case_type=data.get("case_type"),
        year=str(os.getenv("CURRENT_YEAR", "2025")),
        key_dates=", ".join(data.get("key_dates", [])),
        relief_sought=data.get("relief_sought", ""),
        legal_articles=", ".join(data.get("legal_articles", [])),
        rules_to_follow=", ".join(data.get("rules_to_follow", [])),
        precedents=", ".join(data.get("legal_articles", [])),
        case_summary=data.get("case_summary", ""),
        instructions=data.get("instructions", ""),
        notice_text=context_text + annexure_info,
        style_reference=style_reference,
    )

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_DRAFT_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": filled_prompt}],
        max_tokens=8000,
        temperature=0.2,
    )

    raw_text = response.choices[0].message.content

    # Post-process: replace literal \n sequences
    raw_text = raw_text.replace("\\n", "\n")

    # Cleanup: strip Markdown/bold/italics markers and backticks
    # 1) Remove bold markers
    raw_text = raw_text.replace("**", "")
    # 2) Remove any remaining single asterisks
    raw_text = raw_text.replace("*", "")
    # 3) Remove backticks
    raw_text = raw_text.replace("`", "")

    # Export to docx with key_dates for proper table population
    key_dates_list = data.get("key_dates", [])
    file_path = export_to_docx(raw_text, key_dates=key_dates_list)
    return {"petition": raw_text, "file_path": file_path}
