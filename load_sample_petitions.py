#!/usr/bin/env python3
"""
Script to load sample petitions into the permanent knowledge base
"""

import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from app.services.rag_service import ingest_documents

def load_sample_petitions():
    """Load sample petitions into the permanent knowledge base"""
    
    # Define the sample petitions directory
    sample_dir = "sample_petitions"

    docs = []

    # Prefer new structure: subfolders by draft_type
    try:
        entries = [e for e in os.listdir(sample_dir)]
    except FileNotFoundError:
        entries = []

    subdirs = [d for d in entries if os.path.isdir(os.path.join(sample_dir, d))]

    if subdirs:
        # Walk each draft_type folder, ingest all .txt files within
        for draft_folder in subdirs:
            petition_type = draft_folder.replace('_', ' ').strip().lower()
            folder_path = os.path.join(sample_dir, draft_folder)
            for name in os.listdir(folder_path):
                if not name.lower().endswith('.txt'):
                    continue
                file_path = os.path.join(folder_path, name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    docs.append({
                        "source": f"Sample {petition_type.title()} - {name}",
                        "text": content,
                        "draft_type": petition_type
                    })
                    print(f"✓ Loaded: {petition_type.title()} / {name}")
                except Exception as e:
                    print(f"✗ Error loading {file_path}: {e}")
    # else:
    #     # Backward-compatible fallback to flat files mapping
    #     sample_files = [
    #         ("writ_petition_sample.txt", "writ petition"),
    #         ("review_petition_sample.txt", "review petition"), 
    #         ("curative_petition_sample.txt", "curative petition"),
    #         ("civil_suit_sample.txt", "civil suit")
    #     ]

    #     for filename, petition_type in sample_files:
    #         file_path = os.path.join(sample_dir, filename)
            
    #         if os.path.exists(file_path):
    #             try:
    #                 with open(file_path, 'r', encoding='utf-8') as f:
    #                     content = f.read()
                    
    #                 docs.append({
    #                     "source": f"Sample {petition_type.title()}",
    #                     "text": content,
    #                     "draft_type": petition_type
    #                 })
                    
    #                 print(f"✓ Loaded: {petition_type.title()}")
                    
    #             except Exception as e:
    #                 print(f"✗ Error loading {filename}: {e}")
    #         else:
    #             print(f"✗ File not found: {filename}")
    
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