# Consolidated RAG Service
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any
import os

class RAGService:
    def __init__(self):
        self.embeddings = None
        self.permanent_store = None
        self.temp_store = None
        self.permanent_db_path = "./kb_store_1"
        self.temp_db_path = "./temp/chroma_db"
        
        # Ensure directories exist
        os.makedirs(self.permanent_db_path, exist_ok=True)
        os.makedirs(self.temp_db_path, exist_ok=True)
    
    def get_embeddings(self):
        """Get embeddings instance - lazy initialization"""
        if self.embeddings is None:
            self.embeddings = OpenAIEmbeddings()
        return self.embeddings
    
    def get_permanent_store(self):
        """Get or create permanent vector store"""
        if self.permanent_store is None:
            self.permanent_store = Chroma(
                persist_directory=self.permanent_db_path,
                embedding_function=self.get_embeddings(),
                collection_name="permanent_kb"
            )
        return self.permanent_store
    
    def get_temp_store(self):
        """Get or create temporary vector store"""
        if self.temp_store is None:
            self.temp_store = Chroma(
                persist_directory=self.temp_db_path,
                embedding_function=self.get_embeddings(),
                collection_name="temp_kb"
            )
        return self.temp_store
    
    def ingest_documents(self, docs: List[Dict[str, str]], permanent: bool = False):
        """Ingest documents into vector store"""
        if not docs:
            return
            
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100
        )
        
        split_docs = []
        for doc in docs:
            split_docs.extend(
                text_splitter.create_documents(
                    [doc["text"]], 
                    metadatas=[{
                        "source": doc.get("source", "unknown"),
                        "draft_type": doc.get("draft_type")
                    }]
                )
            )
        
        # Add to appropriate store
        if permanent:
            store = self.get_permanent_store()
        else:
            store = self.get_temp_store()
            
        store.add_documents(split_docs)
        store.persist()
    
    def retrieve_context(self, query: str, top_k: int = 5, draft_type: str = None) -> List[Dict[str, Any]]:
        """Retrieve context from both permanent and temporary stores with draft_type filtering"""
        results = []
        
        # Search permanent store
        if self.permanent_store:
            try:
                # Use metadata filter when draft_type provided
                chroma_filter = {"draft_type": draft_type} if draft_type else None
                perm_results = self.permanent_store.similarity_search(query, k=top_k, filter=chroma_filter)
                for doc in perm_results:
                    results.append({
                        "source": doc.metadata.get("source", "permanent_kb"),
                        "text": doc.page_content
                    })
            except Exception as e:
                print(f"Error searching permanent store: {e}")
        
        # Search temporary store
        if self.temp_store:
            try:
                temp_results = self.temp_store.similarity_search(query, k=top_k)
                for doc in temp_results:
                    results.append({
                        "source": doc.metadata.get("source", "temp_kb"),
                        "text": doc.page_content
                    })
            except Exception as e:
                print(f"Error searching temporary store: {e}")
        
        return results[:top_k]

# Global RAG service instance
rag_service = RAGService()

# Convenience functions for backward compatibility
def ingest_documents(docs: List[Dict[str, str]], permanent: bool = False):
    """Convenience function to ingest documents"""
    rag_service.ingest_documents(docs, permanent)

def retrieve_context(query: str, top_k: int = 5, draft_type: str = None) -> List[Dict[str, Any]]:
    """Convenience function to retrieve context with draft_type filtering"""
    return rag_service.retrieve_context(query, top_k, draft_type)

def get_permanent_vector_store():
    """Get the permanent vector store"""
    return rag_service.get_permanent_store()

def load_permanent_kb():
    """Load permanent KB documents - returns empty list since documents are already in vector store"""
    # The permanent KB documents are already stored in the ChromaDB vector store
    # and will be retrieved during context search, so we return an empty list
    # to avoid re-ingesting them
    return []
