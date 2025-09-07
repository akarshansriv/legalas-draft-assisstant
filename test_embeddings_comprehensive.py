#!/usr/bin/env python3
"""
Comprehensive test script for embeddings.py
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    required_modules = [
        'gdown', 'chromadb', 'docx', 'tqdm', 'pathlib'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'docx':
                import docx
            elif module == 'chromadb':
                import chromadb
            elif module == 'gdown':
                import gdown
            elif module == 'tqdm':
                import tqdm
            elif module == 'pathlib':
                import pathlib
            print(f"✅ {module}: OK")
        except ImportError as e:
            print(f"❌ {module}: MISSING - {e}")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️  Missing modules: {missing_modules}")
        print("Install with: pip install " + " ".join(missing_modules))
        return False
    else:
        print("✅ All imports successful!")
        return True

def test_class_initialization():
    """Test GoogleDriveIngestionPipeline initialization"""
    print("\n🧪 Testing class initialization...")
    
    try:
        from embeddings import GoogleDriveIngestionPipeline
        
        # Test with default parameters
        pipeline1 = GoogleDriveIngestionPipeline("test_folder_id")
        assert pipeline1.folder_id == "test_folder_id"
        assert pipeline1.kb_store_dir == "kb_store_1"
        assert pipeline1.temp_dir == "./temp_download"
        print("✅ Default initialization: OK")
        
        # Test with custom parameters
        pipeline2 = GoogleDriveIngestionPipeline(
            "custom_folder_id", 
            kb_store_dir="custom_kb", 
            temp_dir="./custom_temp"
        )
        assert pipeline2.folder_id == "custom_folder_id"
        assert pipeline2.kb_store_dir == "custom_kb"
        assert pipeline2.temp_dir == "./custom_temp"
        print("✅ Custom initialization: OK")
        
        # Test URL construction
        expected_url = "https://drive.google.com/drive/folders/test_folder_id"
        assert pipeline1.folder_url == expected_url
        print("✅ URL construction: OK")
        
        return pipeline1
        
    except Exception as e:
        print(f"❌ Class initialization failed: {e}")
        return None

def test_chroma_client():
    """Test ChromaDB client creation"""
    print("\n🧪 Testing ChromaDB client...")
    
    try:
        from embeddings import GoogleDriveIngestionPipeline
        
        pipeline = GoogleDriveIngestionPipeline("test_folder")
        client = pipeline.get_chroma_client()
        
        # Test if client is created
        assert client is not None
        print("✅ ChromaDB client created: OK")
        
        # Test if client is reused
        client2 = pipeline.get_chroma_client()
        assert client is client2
        print("✅ Client reuse: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB client test failed: {e}")
        return False

def test_file_parsing():
    """Test file content parsing functionality"""
    print("\n🧪 Testing file parsing...")
    
    try:
        from embeddings import GoogleDriveIngestionPipeline
        
        pipeline = GoogleDriveIngestionPipeline("test_folder")
        
        # Create test files
        test_dir = Path("./test_files")
        test_dir.mkdir(exist_ok=True)
        
        # Test text file parsing
        txt_file = test_dir / "test.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("This is a test text file.")
        
        content = pipeline.parse_file_content(str(txt_file), ".txt")
        assert content == "This is a test text file."
        print("✅ Text file parsing: OK")
        
        # Test unknown file extension (fallback to text)
        unknown_file = test_dir / "test.unknown"
        with open(unknown_file, 'w', encoding='utf-8') as f:
            f.write("Unknown file content")
        
        content = pipeline.parse_file_content(str(unknown_file), ".unknown")
        assert content == "Unknown file content"
        print("✅ Unknown file parsing (fallback): OK")
        
        # Test error handling
        try:
            pipeline.parse_file_content("nonexistent_file.txt", ".txt")
            print("❌ Error handling: FAILED (should have raised exception)")
        except Exception:
            print("✅ Error handling: OK")
        
        # Cleanup test files
        import shutil
        shutil.rmtree(test_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ File parsing test failed: {e}")
        return False

def test_collection_operations():
    """Test ChromaDB collection operations"""
    print("\n🧪 Testing collection operations...")
    
    try:
        from embeddings import GoogleDriveIngestionPipeline
        
        # Use a test KB directory
        pipeline = GoogleDriveIngestionPipeline("test_folder", kb_store_dir="./test_kb")
        
        # Test collection listing (should be empty initially)
        collections = pipeline.list_collections()
        print(f"✅ List collections: OK (found {len(collections)} collections)")
        
        # Create a test collection by adding some data
        client = pipeline.get_chroma_client()
        test_collection = client.get_or_create_collection("test_collection")
        
        # Add test documents
        test_collection.add(
            documents=["Test document 1", "Test document 2"],
            metadatas=[{"type": "test1"}, {"type": "test2"}],
            ids=["doc1", "doc2"]
        )
        
        # Test collection stats
        stats = pipeline.get_collection_stats("test_collection")
        assert stats["name"] == "test_collection"
        assert stats["document_count"] == 2
        print("✅ Collection stats: OK")
        
        # Test querying
        results = pipeline.query_collection("test_collection", "document", n_results=1)
        assert results is not None
        assert len(results["documents"][0]) > 0
        print("✅ Collection query: OK")
        
        # Test updated collection listing
        collections = pipeline.list_collections()
        assert "test_collection" in collections
        print("✅ Updated collection list: OK")
        
        # Cleanup
        import shutil
        if os.path.exists("./test_kb"):
            shutil.rmtree("./test_kb")
        
        return True
        
    except Exception as e:
        print(f"❌ Collection operations test failed: {e}")
        return False

def test_folder_url_construction():
    """Test Google Drive folder URL construction"""
    print("\n🧪 Testing folder URL construction...")
    
    try:
        from embeddings import GoogleDriveIngestionPipeline
        
        test_cases = [
            ("1ABC123XYZ", "https://drive.google.com/drive/folders/1ABC123XYZ"),
            ("1C0vFjmqn3yGwNZrLDB4J9UJwhS_cVwwy", "https://drive.google.com/drive/folders/1C0vFjmqn3yGwNZrLDB4J9UJwhS_cVwwy"),
            ("folder_with_underscores", "https://drive.google.com/drive/folders/folder_with_underscores")
        ]
        
        for folder_id, expected_url in test_cases:
            pipeline = GoogleDriveIngestionPipeline(folder_id)
            assert pipeline.folder_url == expected_url
            print(f"✅ URL for {folder_id}: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ URL construction test failed: {e}")
        return False

def test_cleanup_functionality():
    """Test cleanup functionality"""
    print("\n🧪 Testing cleanup functionality...")
    
    try:
        from embeddings import GoogleDriveIngestionPipeline
        
        pipeline = GoogleDriveIngestionPipeline("test_folder", temp_dir="./test_cleanup")
        
        # Create test directory structure
        test_dir = Path("./test_cleanup")
        test_dir.mkdir(exist_ok=True)
        (test_dir / "subdir").mkdir(exist_ok=True)
        (test_dir / "test_file.txt").write_text("test content")
        (test_dir / "subdir" / "nested_file.txt").write_text("nested content")
        
        # Verify directory exists
        assert test_dir.exists()
        print("✅ Test directory created: OK")
        
        # Test cleanup
        pipeline.cleanup_temp_files()
        
        # Verify directory is removed
        assert not test_dir.exists()
        print("✅ Cleanup functionality: OK")
        
        # Test cleanup on non-existent directory (should not error)
        pipeline.cleanup_temp_files()
        print("✅ Cleanup non-existent directory: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Cleanup test failed: {e}")
        return False

def run_integration_test():
    """Run a simulated integration test (without actual Google Drive download)"""
    print("\n🧪 Running integration test simulation...")
    
    try:
        from embeddings import GoogleDriveIngestionPipeline
        
        # Create pipeline
        pipeline = GoogleDriveIngestionPipeline(
            "test_folder", 
            kb_store_dir="./integration_test_kb",
            temp_dir="./integration_test_temp"
        )
        
        # Create mock directory structure like what gdown would create
        temp_dir = Path("./integration_test_temp")
        temp_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different draft types
        (temp_dir / "writ_petition").mkdir(exist_ok=True)
        (temp_dir / "review_petition").mkdir(exist_ok=True)
        
        # Create mock documents
        (temp_dir / "writ_petition" / "sample1.txt").write_text("This is a writ petition sample.")
        (temp_dir / "writ_petition" / "sample2.txt").write_text("Another writ petition example.")
        (temp_dir / "review_petition" / "review_sample.txt").write_text("This is a review petition sample.")
        
        print("✅ Mock directory structure created: OK")
        
        # Process the mock files (skip the download part)
        client = pipeline.get_chroma_client()
        total_docs = 0
        
        for root, dirs, files in os.walk(pipeline.temp_dir):
            if root == pipeline.temp_dir:
                continue
            
            draft_type = os.path.basename(root).replace('_', ' ').strip().lower()
            collection_name = draft_type.replace(' ', '_').lower()
            collection = client.get_or_create_collection(collection_name)
            
            documents = []
            metadatas = []
            ids = []
            
            for file_name in files:
                if not file_name.endswith('.txt'):
                    continue
                
                file_path = os.path.join(root, file_name)
                content = pipeline.parse_file_content(file_path, ".txt")
                
                documents.append(content)
                metadatas.append({
                    "source": f"Sample {draft_type.title()} - {file_name}",
                    "draft_type": draft_type,
                    "file_name": file_name,
                    "file_type": ".txt"
                })
                ids.append(f"sample_{draft_type.replace(' ', '_')}_{Path(file_name).stem}")
            
            if documents:
                collection.add(documents=documents, metadatas=metadatas, ids=ids)
                total_docs += len(documents)
        
        print(f"✅ Processed {total_docs} mock documents: OK")
        
        # Test querying the collections
        collections = pipeline.list_collections()
        print(f"✅ Created collections: {collections}")
        
        for collection_name in collections:
            stats = pipeline.get_collection_stats(collection_name)
            print(f"✅ Collection '{collection_name}': {stats['document_count']} documents")
            
            # Test query
            results = pipeline.query_collection(collection_name, "petition", n_results=1)
            if results and results['documents'][0]:
                print(f"✅ Query test for '{collection_name}': OK")
        
        # Cleanup
        pipeline.cleanup_temp_files()
        import shutil
        if os.path.exists("./integration_test_kb"):
            shutil.rmtree("./integration_test_kb")
        
        print("✅ Integration test simulation: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting comprehensive tests for embeddings.py\n")
    
    test_results = []
    
    # Run all tests
    test_results.append(("Imports", test_imports()))
    test_results.append(("Class Initialization", test_class_initialization() is not None))
    test_results.append(("ChromaDB Client", test_chroma_client()))
    test_results.append(("File Parsing", test_file_parsing()))
    test_results.append(("Collection Operations", test_collection_operations()))
    test_results.append(("URL Construction", test_folder_url_construction()))
    test_results.append(("Cleanup Functionality", test_cleanup_functionality()))
    test_results.append(("Integration Simulation", run_integration_test()))
    
    # Print summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(test_results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests PASSED! embeddings.py is ready to use.")
        print("\n🚀 To test with real Google Drive data:")
        print("1. Make your Google Drive folder public")
        print("2. Run: python embeddings.py")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please fix the issues before using embeddings.py")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
