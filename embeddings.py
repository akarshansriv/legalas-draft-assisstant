import os
import gdown
import shutil
from pathlib import Path
from tqdm import tqdm
from chromadb import PersistentClient
from docx import Document

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: PyPDF2 not available. PDF files will be skipped.")


class GoogleDriveIngestionPipeline:
    """A pipeline to download and ingest documents from Google Drive into ChromaDB"""
    
    def __init__(self, folder_id, kb_store_dir='kb_store_1', temp_dir='./temp_download'):
        """
        Initialize the pipeline
        
        Args:
            folder_id (str): Google Drive folder ID
            kb_store_dir (str): Directory to store ChromaDB
            temp_dir (str): Temporary directory for downloads
        """
        self.folder_id = folder_id
        self.kb_store_dir = kb_store_dir
        self.temp_dir = temp_dir
        self.folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
        self.client = None
        
    def get_chroma_client(self):
        """Get ChromaDB client"""
        if not self.client:
            self.client = PersistentClient(path=self.kb_store_dir)
        return self.client

    def download_folder_from_drive(self):
        """Download entire folder from Google Drive using gdown"""
        print("Downloading folder from Google Drive...")
        try:
            # Clean up any existing temp directory
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            
            # Download the entire folder
            gdown.download_folder(self.folder_url, output=self.temp_dir, quiet=False)
            
            # Verify the download was successful
            if os.path.exists(self.temp_dir):
                print("✓ Folder downloaded successfully!")
                return True
            else:
                print("✗ Download failed - no files were downloaded")
                return False
                
        except Exception as e:
            print(f"✗ Error downloading folder: {e}")
            print("\nMake sure the Google Drive folder is publicly shared (anyone with link can view)")
            return False

    def parse_file_content(self, file_path, file_extension):
        """Parse content based on file extension"""
        try:
            ext = file_extension.lower()
            
            if ext in ['.docx', '.doc', '.docs', '.dox']:
                # Microsoft Word documents (all variants)
                doc = Document(file_path)
                return "\n".join([para.text for para in doc.paragraphs])
                
            elif ext in ['.txt', '.text']:
                # Text files
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
                    
            elif ext == '.pdf':
                # PDF files
                if not PDF_AVAILABLE:
                    raise Exception("PyPDF2 not available for PDF processing")
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return text
                    
            else:
                # Try to read as plain text for any other extension
                print(f"Warning: Unknown file extension '{ext}', attempting to read as text...")
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
                    
        except Exception as e:
            raise Exception(f"Error parsing file: {e}")

    def cleanup_temp_files(self):
        """Clean up temporary downloaded files"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print("✓ Temporary files cleaned up")

    def run_pipeline(self):
        """Main pipeline to download and ingest documents"""
        print("Starting document ingestion pipeline...\n")
        
        # Download folder from Google Drive
        if not self.download_folder_from_drive():
            print("Failed to download folder. Exiting.")
            return False
        
        # Get ChromaDB client
        client = self.get_chroma_client()
        total_docs = 0
        
        # Process downloaded files
        for root, dirs, files in os.walk(self.temp_dir):
            # Get the draft type from the subdirectory name
            if root == self.temp_dir:
                continue  # Skip root directory
            
            draft_type = os.path.basename(root).replace('_', ' ').strip().lower()
            
            # Create collection for this draft type
            collection_name = draft_type.replace(' ', '_').lower()
            collection = client.get_or_create_collection(collection_name)
            
            documents = []
            metadatas = []
            ids = []
            
            print(f"\nProcessing {draft_type} files...")
            
            for file_name in tqdm(files, desc=f"Loading {draft_type}"):
                file_path = os.path.join(root, file_name)
                file_extension = Path(file_name).suffix
                
                # Skip non-document files - Updated to support more formats
                supported_extensions = ['.txt', '.text', '.docx', '.doc', '.docs', '.dox', '.pdf']
                if file_extension.lower() not in supported_extensions:
                    print(f"Skipping {file_name} - unsupported format (supported: {', '.join(supported_extensions)})")
                    continue
                
                try:
                    content = self.parse_file_content(file_path, file_extension)
                    
                    documents.append(content)
                    metadatas.append({
                        "source": f"Sample {draft_type.title()} - {file_name}",
                        "draft_type": draft_type,
                        "file_name": file_name,
                        "file_type": file_extension.lower()
                    })
                    ids.append(f"sample_{draft_type.replace(' ', '_')}_{Path(file_name).stem}")
                    
                    print(f"✓ Loaded: {draft_type.title()} / {file_name}")
                    
                except Exception as e:
                    print(f"✗ Error loading {file_name}: {e}")
            
            # Add documents to ChromaDB collection
            if documents:
                try:
                    collection.add(
                        documents=documents,
                        metadatas=metadatas,
                        ids=ids
                    )
                    total_docs += len(documents)
                    print(f"✓ Successfully loaded {len(documents)} documents into collection '{collection_name}'")
                except Exception as e:
                    print(f"✗ Error adding documents to collection '{collection_name}': {e}")
        
        # Cleanup temporary files
        self.cleanup_temp_files()
        
        if total_docs > 0:
            print(f"\n✅ Successfully processed {total_docs} documents into partitioned ChromaDB!")
            print(f"Knowledge base stored in: {self.kb_store_dir}")
            return True
        else:
            print("\n❌ No documents were processed")
            return False

    def query_collection(self, collection_name, query_text, n_results=5):
        """Query a specific collection"""
        try:
            client = self.get_chroma_client()
            collection = client.get_collection(collection_name)
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results
        except Exception as e:
            print(f"Error querying collection '{collection_name}': {e}")
            return None

    def list_collections(self):
        """List all available collections"""
        try:
            client = self.get_chroma_client()
            collections = client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            print(f"Error listing collections: {e}")
            return []

    def get_collection_stats(self, collection_name):
        """Get statistics for a collection"""
        try:
            client = self.get_chroma_client()
            collection = client.get_collection(collection_name)
            count = collection.count()
            return {"name": collection_name, "document_count": count}
        except Exception as e:
            print(f"Error getting stats for collection '{collection_name}': {e}")
            return None

if __name__ == "__main__":
    # Check if gdown is installed
    try:
        import gdown
    except ImportError:
        print("gdown is not installed. Please install it with:")
        print("pip install gdown")
        exit(1)
    
    # Example usage - test with local folder first
    # folder_id = "1C0vFjmqn3yGwNZrLDB4J9UJwhS_cVwwy"
    # pipeline = GoogleDriveIngestionPipeline(folder_id)
    # pipeline.run_pipeline()
    
    # Working Google Drive folder - Updated with correct folder ID
    folder_id = "1D6f47bL_whHVgscUochFh3QF_WgcFU_U"
    pipeline = GoogleDriveIngestionPipeline(folder_id)
    
    print("\n" + "="*60)
    print("TESTING GOOGLE DRIVE INGESTION PIPELINE")
    print("="*60)
    success = pipeline.run_pipeline()
    
    if success:
        print("\n" + "="*60)
        print("SUCCESS! 🎉")
        print("="*60)
        print("✅ Google Drive folder downloaded successfully")
        print("✅ Documents processed and stored in ChromaDB")
        print("✅ Pipeline is ready for production use")
        
        # Show available collections
        collections = pipeline.list_collections()
        print(f"\n📚 Available collections: {collections}")
        
        # Show collection stats
        for collection_name in collections:
            stats = pipeline.get_collection_stats(collection_name)
            if stats:
                print(f"   {collection_name}: {stats['document_count']} documents")
    else:
        print("\n❌ Pipeline failed - check Google Drive folder sharing settings")
    
    # Comment out the test code since we now have the working version
    # print("Testing with local sample_petitions folder...")
    # class LocalTestPipeline(GoogleDriveIngestionPipeline):
    #     def download_folder_from_drive(self):
    #         """Override to use local folder instead"""
    #         print("Using local sample_petitions folder...")
    #         self.temp_dir = "./sample_petitions"  # Use existing local folder
    #         return True
    print("\nDone!")