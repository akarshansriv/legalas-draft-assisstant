#!/usr/bin/env python3
"""
Simple script to load sample petitions into ChromaDB without requiring OpenAI API key
"""

import os
import chromadb
from chromadb.config import Settings

def load_sample_petitions_simple():
    """Load sample petitions directly into ChromaDB"""
    
    # Create ChromaDB client
    client = chromadb.PersistentClient(path="./kb_store")
    
    # Get or create collection (align with RAG service name)
    collection = client.get_or_create_collection("permanent_kb")
    
    # Define the sample petitions directory
    sample_dir = "sample_petitions"

    documents = []
    metadatas = []
    ids = []

    # Prefer new structure: subfolders by draft_type
    try:
        entries = [e for e in os.listdir(sample_dir)]
    except FileNotFoundError:
        entries = []

    subdirs = [d for d in entries if os.path.isdir(os.path.join(sample_dir, d))]

    if subdirs:
        for draft_folder in subdirs:
            petition_type = draft_folder.replace('_', ' ').strip().lower()
            folder_path = os.path.join(sample_dir, draft_folder)
            for name in os.listdir(folder_path):
                if not (name.lower().endswith('.txt') or name.lower().endswith('.docx') or name.lower().endswith('.pdf')):
                    continue
                file_path = os.path.join(folder_path, name)
                try:
                    if name.lower().endswith('.docx'):
                        # Load DOCX file
                        from utils.document_loader import load_docx
                        with open(file_path, 'rb') as f:
                            content = load_docx(f.read())
                    elif name.lower().endswith('.pdf'):
                        # Load PDF file with OCR support using pymupdf4llm
                        from utils.document_loader import load_pdf_pymupdf4llm
                        with open(file_path, 'rb') as f:
                            content = load_pdf_pymupdf4llm(f.read())
                    else:
                        # Load TXT file
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    documents.append(content)
                    metadatas.append({"source": f"Sample {petition_type.title()} - {name}", "draft_type": petition_type})
                    ids.append(f"sample_{petition_type.replace(' ', '_')}_{os.path.splitext(name)[0]}")
                    print(f"✓ Loaded: {petition_type.title()} / {name}")
                except Exception as e:
                    print(f"✗ Error loading {file_path}: {e}")
    else:
        # Backward-compatible fallback to flat files mapping
        sample_files = [
            ("writ_petition_sample.txt", "writ petition"),
            ("review_petition_sample.txt", "review petition"), 
            ("curative_petition_sample.txt", "curative petition"),
            ("civil_suit_sample.txt", "civil suit")
        ]

        for filename, petition_type in sample_files:
            file_path = os.path.join(sample_dir, filename)
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    documents.append(content)
                    # Store draft_type explicitly for filtering
                    metadatas.append({"source": f"Sample {petition_type.title()}", "draft_type": petition_type})
                    ids.append(f"sample_{petition_type.replace(' ', '_')}")
                    
                    print(f"✓ Loaded: {petition_type.title()}")
                    
                except Exception as e:
                    print(f"✗ Error loading {filename}: {e}")
            else:
                print(f"✗ File not found: {filename}")
    
    # Add documents to collection
    if documents:
        try:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"\n✓ Successfully loaded {len(documents)} sample petitions into ChromaDB")
            print("\nSample petitions loaded:")
            for metadata in metadatas:
                print(f"  - {metadata['source']}")
        except Exception as e:
            print(f"✗ Error adding documents to collection: {e}")
    else:
        print("✗ No documents to load")

if __name__ == "__main__":
    print("Loading sample petitions into ChromaDB...\n")
    load_sample_petitions_simple()
    print("\nDone!") 