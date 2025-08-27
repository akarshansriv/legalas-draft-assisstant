# Simplified knowledge base service that uses the consolidated RAG service
from app.services.rag_service import get_permanent_vector_store

def load_permanent_kb():
    """Load permanent KB - now handled by the consolidated RAG service"""
    # The permanent KB is now managed by the RAG service
    # This function is kept for backward compatibility
    return []

def get_permanent_vector_store():
    """Get the permanent vector store from the consolidated RAG service"""
    return get_permanent_vector_store()
