#!/usr/bin/env python3
"""
Script to load sample petitions into the permanent knowledge base
"""

import os
from app.services.rag_service import ingest_documents

def load_sample_petitions():
    """Load sample petitions into the permanent knowledge base"""
    
    # Define the sample petitions directory
    sample_dir = "sample_petitions"
    
    # List of sample petition files
    sample_files = [
        "writ_petition_sample.txt",
        "review_petition_sample.txt", 
        "curative_petition_sample.txt",
        "civil_suit_sample.txt"
    ]
    
    docs = []
    
    # Load each sample petition
    for filename in sample_files:
        file_path = os.path.join(sample_dir, filename)
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract petition type from filename
                petition_type = filename.replace('_sample.txt', '').replace('_', ' ').title()
                
                docs.append({
                    "source": f"Sample {petition_type}",
                    "text": content
                })
                
                print(f"✓ Loaded: {petition_type}")
                
            except Exception as e:
                print(f"✗ Error loading {filename}: {e}")
        else:
            print(f"✗ File not found: {filename}")
    
    # Ingest documents into permanent knowledge base
    if docs:
        try:
            ingest_documents(docs, permanent=True)
            print(f"\n✓ Successfully loaded {len(docs)} sample petitions into permanent knowledge base")
            print("\nSample petitions loaded:")
            for doc in docs:
                print(f"  - {doc['source']}")
        except Exception as e:
            print(f"✗ Error ingesting documents: {e}")
    else:
        print("✗ No documents to load")

if __name__ == "__main__":
    print("Loading sample petitions into permanent knowledge base...\n")
    load_sample_petitions()
    print("\nDone!") 