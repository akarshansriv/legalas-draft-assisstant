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
    
    # Get or create collection
    collection = client.get_or_create_collection("permanent_kb")
    
    # Define the sample petitions directory
    sample_dir = "sample_petitions"
    
    # List of sample petition files with their types
    sample_files = [
        ("writ_petition_sample.txt", "writ petition"),
        ("review_petition_sample.txt", "review petition"), 
        ("curative_petition_sample.txt", "curative petition"),
        ("civil_suit_sample.txt", "civil suit")
    ]
    
    documents = []
    metadatas = []
    ids = []
    
    # Load each sample petition
    for filename, petition_type in sample_files:
        file_path = os.path.join(sample_dir, filename)
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Add to collections
                documents.append(content)
                metadatas.append({"source": f"Sample {petition_type.title()}", "type": petition_type})
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