# RAG System with ChromaDB & Gemini AI

A modern FastAPI application providing a RAG (Retrieval-Augmented Generation) system with file upload, ChromaDB integration, and Gemini AI for intelligent document-based conversations.

## 🎯 Project Purpose

This system supports the following workflow:
1. **File Upload**: Upload PDF, TXT, DOCX, image files
2. **ChromaDB Integration**: Add files to vector database
3. **Gemini AI Integration**: AI-powered question-answer system
4. **RAG System**: Document-based intelligent responses

## 🏗️ Architecture

The project follows hexagonal architecture (clean architecture) principles:

```
app/
├── core/                    # Core business logic and configuration
│   ├── config.py          # Application settings
│   ├── dependencies.py    # Dependency injection
│   ├── exceptions.py      # Custom exception classes
│   └── logging.py         # Logging configuration
├── domain/                 # Domain layer
│   ├── document_entities.py      # Document entities
│   ├── document_repositories.py # Document repository interfaces
│   ├── rag_entities.py          # RAG entities
│   └── rag_repositories.py      # RAG repository interfaces
├── application/            # Application layer
│   └── use_cases.py       # Business use cases
├── infrastructure/         # Infrastructure layer
│   ├── chroma_repository.py    # ChromaDB implementation
│   ├── embedding_service.py    # Embedding service
│   ├── file_processor.py      # File processing
│   ├── gemini_adapter.py      # Gemini AI adapter
│   └── redis.py               # Redis cache
└── presentation/          # Presentation layer
    ├── chat/              # Chat controller and DTOs
    ├── documents/         # Document controller and DTOs
    ├── error_handler.py   # Error handling
    └── middleware.py      # Middleware components
```

## 🚀 Features

### 📁 File Management
- **Multi-format Support**: PDF, TXT, DOCX, XLSX, PPTX, Images (PNG, JPG, etc.)
- **File Upload**: RESTful API for single and multiple file uploads
- **Content Extraction**: Automatic text extraction from various file types
- **OCR Support**: Text extraction from images using Tesseract
- **Batch Processing**: Bulk file processing with metadata support
- **File Validation**: File type and size validation
- **List Documents**: View all uploaded documents with metadata

#### Supported File Types
- **Documents**: PDF, TXT, DOCX, DOC
- **Spreadsheets**: XLSX, XLS
- **Presentations**: PPTX, PPT
- **Images**: PNG, JPG, JPEG, GIF, BMP, TIFF (with OCR)
- **File Size Limits**: 50MB for documents, 10MB for images

### 🧠 ChromaDB Vector Database
- **Vector Storage**: Store documents as vectors
- **Similarity Search**: Search for similar content with configurable thresholds
- **Metadata Filtering**: Filter by metadata
- **Persistent Storage**: Persistent data storage
- **Collection Management**: Collection management
- **RAG Context**: Intelligent document retrieval for AI responses

### 🤖 Gemini AI Integration
- **Context-Aware Responses**: Document-based responses using RAG
- **RAG Implementation**: Retrieval-Augmented Generation with similarity scoring
- **Configurable Thresholds**: Adjustable similarity thresholds for document inclusion
- **Multilingual Support**: Support for multiple languages in embeddings

### 🔧 Technical Features
- **Hexagonal Architecture**: Clean architecture principles with proper separation of concerns
- **Domain-Driven Design**: Separate domain entities and repository interfaces
- **Dependency Injection**: Proper dependency management
- **FastAPI**: Modern, fast web framework with automatic documentation
- **Docker**: Containerization with multi-service setup
- **Comprehensive Error Handling**: JSON error responses for all scenarios
- **Middleware**: Logging, security, rate limiting, and error handling
- **Testing**: Test coverage with Pytest

## 🛠️ Technologies

- **Python 3.11+**
- **FastAPI** - Web framework
- **ChromaDB** - Vector database
- **Google Gemini AI** - Generative AI
- **Docker & Docker Compose** - Containerization
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## 📦 Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd python-rag-gemini-api
```

### 2. Set up environment variables

```bash
# Create .env file
cp env.template .env

# Set your GEMINI_API_KEY
# Edit .env file
```

### 3. Run with Docker

```bash
# Quick start
./start.sh

# Or manually
docker-compose up -d
```

## 🐳 Docker Services

This project includes the following services:

- **FastAPI App** (Port 2000): Main application
- **ChromaDB** (Port 8000): Vector database

### Development

```bash
# Start all services
./start.sh

# Check service status
docker-compose ps

# View logs
docker-compose logs -f app
docker-compose logs -f chroma
```

## 📚 API Documentation

After starting the application:

- **Swagger UI**: http://localhost:2000/docs
- **ReDoc**: http://localhost:2000/redoc
- **Health Check**: http://localhost:2000/health
- **ChromaDB**: http://localhost:8000

## 🧠 RAG System Workflow

### 1. File Upload and Processing

#### Upload Single File
```bash
# Upload a single file (PDF, DOCX, TXT, etc.)
curl -X POST "http://localhost:2000/api/v1/documents/upload" \
  -F "file=@document.pdf" \
  -F 'metadata={"source": "manual_upload", "category": "documentation"}'
```

#### Upload Multiple Files
```bash
# Upload multiple files at once
curl -X POST "http://localhost:2000/api/v1/documents/upload-multiple" \
  -F "files=@document1.pdf" \
  -F "files=@document2.docx" \
  -F "files=@image.png" \
  -F 'metadatas=[{"source": "file1"}, {"source": "file2"}, {"source": "image"}]'
```

#### Get Supported File Types
```bash
# Check supported file types and limits
curl -X GET "http://localhost:2000/api/v1/documents/supported-types"
```

#### Traditional Text Upload (Still Available)
```bash
# Upload documents as text
curl -X POST "http://localhost:2000/api/v1/documents/" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "Python is a programming language",
      "FastAPI is a modern web framework"
    ],
    "metadatas": [
      {"source": "python_guide.pdf", "category": "programming"},
      {"source": "web_frameworks.txt", "category": "web"}
    ]
  }'
```

### 2. Document Search
```bash
# Search similar documents
curl -X POST "http://localhost:2000/api/v1/documents/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Python?",
    "n_results": 3
  }'
```

### 3. AI Chat (RAG)
```bash
# Chat with RAG
curl -X POST "http://localhost:2000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about Python programming",
    "conversation_id": "optional"
  }'
```

## 🌐 API Endpoints

### 📁 Document Management
- `POST /api/v1/documents/` - Add documents to knowledge base
- `GET /api/v1/documents/` - List all documents with metadata
- `GET /api/v1/documents/search` - Search similar documents
- `GET /api/v1/documents/{id}` - Get specific document
- `PUT /api/v1/documents/{id}` - Update document
- `DELETE /api/v1/documents/{id}` - Delete document
- `GET /api/v1/documents/stats` - Get collection statistics
- `POST /api/v1/documents/reset` - Reset collection
- `POST /api/v1/documents/upload` - Upload single file
- `POST /api/v1/documents/upload-multiple` - Upload multiple files
- `GET /api/v1/documents/supported-types` - Get supported file types

### 🤖 Chat & AI
- `POST /api/v1/chat/` - Chat with Gemini AI (with RAG)
  - Supports RAG context with configurable parameters
  - Returns sources and similarity information
  - Configurable context document limits

### 🔧 System
- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

## 🧪 Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_main.py
```

## 🔒 Security Features

- **JWT Authentication**: Token-based authentication
- **Password Hashing**: Secure password hashing with bcrypt
- **CORS Protection**: Cross-origin request protection
- **Security Headers**: Security headers
- **Rate Limiting**: API rate limiting
- **Input Validation**: Data validation with Pydantic

## 📊 Monitoring

- **Health Check**: `/health` endpoint
- **Request Logging**: All requests are logged
- **Performance Metrics**: Performance metrics
- **Error Handling**: Comprehensive error handling

## 🔧 Development

### Code Formatting
```bash
black .
isort .
```

### Linting
```bash
flake8 app/
mypy app/
```

## 🚀 Quick Start Example

```bash
# 1. Start services
docker-compose up -d

# 2. Upload a document file
curl -X POST "http://localhost:2000/api/v1/documents/upload" \
  -F "file=@document.pdf" \
  -F 'metadata={"source": "manual_upload", "category": "documentation"}'

# 3. List uploaded documents
curl -X GET "http://localhost:2000/api/v1/documents/"

# 4. Chat with AI using RAG
curl -X POST "http://localhost:2000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is this document about?",
    "use_rag": true,
    "max_context_docs": 3
  }'

# 5. Search documents
curl -X GET "http://localhost:2000/api/v1/documents/search?query=python&n_results=3"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues:
- Use GitHub Issues
- Check API documentation
- Test health check endpoint