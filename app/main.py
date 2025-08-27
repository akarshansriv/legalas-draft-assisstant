from fastapi import FastAPI, UploadFile, File, Form
from app.routes import router
import os
from dotenv import load_dotenv
import chromadb

load_dotenv()

# Create ChromaDB persistent client for permanent KB
PERSISTENT_KB_PATH = "./kb_store"
os.makedirs(PERSISTENT_KB_PATH, exist_ok=True)
chroma_client = chromadb.PersistentClient(path=PERSISTENT_KB_PATH)

# Make collections available to routes
app = FastAPI()
app.state.permanent_kb = chroma_client.get_or_create_collection("permanent_kb")

# Include routes
app.include_router(router)
