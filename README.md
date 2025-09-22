# 🏛️ Legalas Draft Assistant

An AI-powered legal drafting tool that helps automate the creation of legal documents using advanced language models and retrieval-augmented generation (RAG) capabilities.

## 🎯 Overview

Legalas Draft Assistant is a comprehensive platform designed to streamline legal document creation by leveraging:
- **AI-powered document generation** using state-of-the-art language models
- **Knowledge base integration** with ChromaDB for efficient document retrieval
- **Google Drive integration** for seamless document management
- **Multiple document format support** (PDF, DOCX, TXT, DOC)
- **Specialized legal templates** for various petition types

## ✨ Features

### 🤖 AI-Powered Drafting
- Automated generation of legal documents
- Context-aware content creation
- Template-based document structuring
- Multi-format output support

### 📚 Knowledge Base Management
- **ChromaDB Integration**: Efficient vector storage and retrieval
- **Document Ingestion Pipeline**: Automated processing of legal documents
- **Partitioned Collections**: Organized by document types (writ petitions, civil suits, etc.)
- **Smart Search**: Semantic search across legal precedents

### ☁️ Cloud Integration
- **Google Drive Sync**: Direct folder downloading and processing
- **AWS Integration**: Cloud storage and processing capabilities
- **Real-time Updates**: Automatic synchronization of document changes

### 🔧 Document Processing
- **Multi-format Support**: PDF, DOCX, DOC, TXT, DOCS, DOX
- **Intelligent Parsing**: Content extraction with format preservation
- **Batch Processing**: Handle multiple documents simultaneously
- **Error Handling**: Robust processing with detailed error reporting

## 🏗️ Architecture

```
├── app/                          # Main application
│   ├── main.py                  # FastAPI application entry point
│   ├── routes.py                # API routes definition
│   ├── models/                  # Data models and schemas
│   └── services/                # Business logic services
│       ├── bedrock_service.py   # AWS Bedrock integration
│       ├── draft_generator.py   # Document generation logic
│       ├── knowledge_base.py    # KB management
│       ├── rag_service.py       # RAG implementation
│       └── uploader.py          # File upload handling
├── embeddings.py                # Google Drive ingestion pipeline
├── streamlit_app.py            # Streamlit web interface
├── utils/                       # Utility functions
├── prompts/                     # AI prompt templates
├── rules/                       # Legal drafting rules
└── sample_petitions/           # Template documents
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)
- Google Drive API credentials (optional)
- AWS credentials (for cloud features)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/akarshansriv/legalas-draft-assisstant.git
   cd legalas-draft-assisstant
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv legalas
   source legalas/bin/activate  # On Windows: legalas\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

### Configuration

Create a `.env` file with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# AWS Configuration  
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=your_aws_region

# ChromaDB Configuration
CHROMA_DB_PATH=./kb_store_1

# Google Drive (Optional)
GOOGLE_DRIVE_CREDENTIALS=./credentials.json
```

## 💻 Usage

### 1. Web Interface (Streamlit)

Launch the interactive web interface:

```bash
streamlit run streamlit_app.py
```

Navigate to `http://localhost:8501` to access the web interface.

### 2. API Server (FastAPI)

Start the FastAPI server:

```bash
python app/main.py
```

API documentation will be available at `http://localhost:8000/docs`

### 3. Document Ingestion Pipeline

Process documents from Google Drive:

```python
from embeddings import GoogleDriveIngestionPipeline

# Initialize pipeline with Google Drive folder ID
pipeline = GoogleDriveIngestionPipeline("your_folder_id")

# Run the complete ingestion process
success = pipeline.run_pipeline()

# Query the knowledge base
results = pipeline.query_collection("writ_petition", "legal precedent")
```

### 4. Standalone Processing

Process local documents:

```bash
python load_sample_petitions.py
```

## 📁 Document Types Supported

### Input Formats
- **PDF** (.pdf) - Portable Document Format
- **Word Documents** (.docx, .doc, .docs, .dox) - Microsoft Word formats
- **Text Files** (.txt, .text) - Plain text documents

### Legal Document Types
- **Writ Petitions** - Constitutional remedy applications
- **Civil Suits** - Civil litigation documents  
- **Curative Petitions** - Supreme Court curative petitions
- **Review Petitions** - Review applications
- **Bail Applications** - Bail petition templates

## 🔍 API Endpoints

### Document Generation
```
POST /generate-draft
Content-Type: application/json

{
  "document_type": "writ_petition",
  "client_details": {...},
  "case_details": {...}
}
```

### Knowledge Base Query
```
GET /query/{collection_name}?q=search_term&limit=5
```

### Document Upload
```
POST /upload
Content-Type: multipart/form-data
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Test embeddings and ChromaDB integration
python test_embeddings_comprehensive.py

# Test document loading
python test_load_sample_petition.py

# Test embeddings functionality
python test_embeddings.py
```

## 📊 Knowledge Base Collections

The system organizes documents into specialized collections:

- `writ_petition` - Writ petition documents and precedents
- `civil_suit` - Civil litigation materials  
- `curative_petition` - Curative petition examples
- `review_petition` - Review petition templates
- `bail_application` - Bail application formats

## 🔧 Development

### Adding New Document Types

1. Create sample documents in `sample_petitions/new_type/`
2. Update the ingestion pipeline to recognize the new type
3. Add corresponding prompts in `prompts/`
4. Update the API routes to handle the new document type

### Extending AI Capabilities

1. Modify prompt templates in `prompts/`
2. Update the generation logic in `app/services/draft_generator.py`
3. Add new rules in `rules/` directory
4. Test with the new document types

## 🛠️ Configuration

### ChromaDB Settings
```python
# Customize ChromaDB configuration
client = PersistentClient(
    path="./kb_store_1",
    settings=Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="./kb_store_1"
    )
)
```

### AI Model Configuration
```python
# Configure the language model
model_config = {
    "model_name": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000
}
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

For support, email support@legalas.ai or join our [Discord community](https://discord.gg/legalas).

## 🙏 Acknowledgments

- OpenAI for GPT models
- ChromaDB for vector database capabilities
- Streamlit for the web interface framework
- FastAPI for the robust API framework
- The legal tech community for inspiration and feedback

---

**Built with ❤️ for the legal community**
