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
        "writ_petition": "writ_petition_sample.txt",
        "review_petition": "review_petition_sample.txt",
        "curative_petition": "curative_petition_sample.txt",
        "civil_suit": "civil_suit_sample.txt",
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
        else:
            return ""
    path = os.path.join("sample_petitions", filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()
            # Use only the first ~2500 chars as style reference to avoid copying content
            return text[:2500]
    except Exception:
        return ""


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

    filled_prompt = BASE_PROMPT.format(
        draft_type=data.get("draft_type"),
        petitioner=data.get("petitioner"),
        respondent=data.get("respondent"),
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
        notice_text=context_text,
        style_reference=style_reference,
    )

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_DRAFT_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": filled_prompt}],
        max_tokens=2500,
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

    # Export to docx
    file_path = export_to_docx(raw_text)
    return {"petition": raw_text, "file_path": file_path}
