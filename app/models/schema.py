from pydantic import BaseModel
from typing import List, Optional


class PetitionInput(BaseModel):
    case_type: str
    court_name: str
    draft_type: str
    jurisdiction: str
    petitioner: str
    respondent: str
    case_summary: str
    key_dates: List[str]
    relief_sought: str
    legal_articles: List[str]
    rules_to_follow: List[str]
    precedents: List[str]
