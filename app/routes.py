from fastapi import APIRouter
from app.models.schema import PetitionInput
from app.services.draft_generator import generate_petition

router = APIRouter()


@router.post("/generate")
def draft_petition(input_data: PetitionInput):
    return generate_petition(input_data)
