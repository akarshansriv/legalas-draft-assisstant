# Simplified uploader service that uses the consolidated document loader
from utils.document_loader import load_file_async
from fastapi import UploadFile
from typing import List

async def extract_text_from_file(file: UploadFile) -> str:
    """Extract text from uploaded file using consolidated loader"""
    return await load_file_async(file)

async def process_and_store_permanent_docs(files: List[UploadFile], collection):
    """Process and store permanent documents - simplified to use consolidated loader"""
    for file in files:
        text = await extract_text_from_file(file)
        if text.strip():
            collection.add(
                documents=[text],
                metadatas=[{"filename": file.filename}],
                ids=[file.filename],
            )

async def process_and_store_temp_docs(files: List[UploadFile]) -> List[str]:
    """Process temporary documents - simplified to use consolidated loader"""
    temp_docs = []
    for file in files:
        text = await extract_text_from_file(file)
        if text.strip():
            temp_docs.append(text)
    return temp_docs
