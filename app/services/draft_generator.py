import openai
from app.services.formatter import format_petition
from fastapi.responses import FileResponse
from app.services.rule_engine import get_required_sections

with open("prompts/base_prompt.txt") as f:
    BASE_PROMPT = f.read()


def generate_petition(data):
    filled_prompt = BASE_PROMPT.format(
        case_type=data.case_type,
        court_name=data.court_name,
        draft_type=data.draft_type,
        jurisdiction=data.jurisdiction,
        petitioner=data.petitioner,
        respondent=data.respondent,
        case_summary=data.case_summary,
        key_dates=", ".join(data.key_dates),
        relief_sought=data.relief_sought,
        legal_articles=", ".join(data.legal_articles),
        rules_to_follow=", ".join(data.rules_to_follow),
        precedents=", ".join(data.precedents),
    )

    response = openai.ChatCompletion.create(
        model="gpt-4", messages=[{"role": "user", "content": filled_prompt}]
    )

    raw_text = response["choices"][0]["message"]["content"]
    breakpoint()
    output_path = format_petition(raw_text, data.case_type)
    return FileResponse(
        path=output_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="my_document.docx",  # This is the download name
    )
