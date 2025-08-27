import os
import pickle
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import numpy as np
from tqdm import tqdm
from typing import List
from pathlib import Path

# FAISS
import faiss

EMB_MODEL = "text-embedding-3-small"  # or any available embedding model
INDEX_PATH = "temp/faiss_index.bin"
DOC_STORE_PATH = "temp/doc_store.pkl"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


# Simplified RAG wrapper that uses the consolidated RAG service
from app.services.rag_service import RAGService, ingest_documents, retrieve_context

# Create a global RAG service instance for backward compatibility
rag_service = RAGService()

class RAGIndex:
    """Wrapper class for backward compatibility"""
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.rag_service = rag_service
    
    def build(self, docs, permanent=False):
        """Build index using consolidated service"""
        self.rag_service.ingest_documents(docs, permanent)
    
    def query(self, query_text, top_k=3):
        """Query using consolidated service"""
        results = self.rag_service.retrieve_context(query_text, top_k)
        # Convert to expected format
        return [{"source": r["source"], "text": r["text"]} for r in results]
    
    def ingest_documents(self, docs):
        """Ingest documents using consolidated service"""
        self.rag_service.ingest_documents(docs)
    
    def retrieve_context(self, query: str, top_k: int = 5):
        """Retrieve context using consolidated service"""
        return self.rag_service.retrieve_context(query, top_k)

# Convenience functions for backward compatibility
def get_embedding(text: str):
    """Get embedding using consolidated service"""
    return rag_service.embeddings.embed_query(text)

def chunk_text(text: str, size=800, overlap=100):
    """Chunk text - kept for backward compatibility"""
    tokens = text.split()
    chunks = []
    i = 0
    while i < len(tokens):
        chunk = tokens[i : i + size]
        chunks.append(" ".join(chunk))
        i += size - overlap
    return chunks
