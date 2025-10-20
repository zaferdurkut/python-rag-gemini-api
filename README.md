# RAG System with ChromaDB & Gemini AI

This project is a modern FastAPI application that provides a RAG (Retrieval-Augmented Generation) system with file upload, ChromaDB integration, and Gemini AI integration.

## 🎯 Project Purpose

This system supports the following workflow:
1. **File Upload**: Upload PDF, TXT, DOCX files
2. **ChromaDB Integration**: Add files to vector database
3. **Gemini AI Integration**: AI-powered question-answer system
4. **RAG System**: Document-based intelligent responses

## 🏗️ Architecture

The project follows hexagonal architecture pattern:

```
app/
├── core/           # Core business logic and configuration
├── domain/         # Domain entities and repository interfaces
├── application/    # Use cases and business logic
├── infrastructure/ # External services (ChromaDB, Gemini AI)
└── presentation/   # FastAPI endpoints and middleware
```

## 🚀 Features

### 📁 File Management
- **Multi-format Support**: PDF, TXT, DOCX, MD files
- **File Upload**: RESTful API for file upload
- **Content Extraction**: Automatic text extraction
- **Batch Processing**: Bulk file processing

### 🧠 ChromaDB Vector Database
- **Vector Storage**: Store documents as vectors
- **Similarity Search**: Search for similar content
- **Metadata Filtering**: Filter by metadata
- **Persistent Storage**: Persistent data storage
- **Collection Management**: Collection management

### 🤖 Gemini AI Integration
- **Context-Aware Responses**: Document-based responses
- **Conversation Management**: Chat history management
- **Session Handling**: Session management
- **RAG Implementation**: Retrieval-Augmented Generation

### 🔧 Technical Features
- **Hexagonal Architecture**: Clean architecture principles
- **FastAPI**: Modern, fast web framework
- **Docker**: Containerization
- **JWT Authentication**: Secure authentication
- **Middleware**: Logging, security, rate limiting
- **Testing**: Test coverage with Pytest

## 🛠️ Technologies

- **Python 3.13+**
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
```bash
# Upload documents
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
- `POST /api/v1/documents/search` - Search similar documents
- `GET /api/v1/documents/{id}` - Get specific document
- `PUT /api/v1/documents/{id}` - Update document
- `DELETE /api/v1/documents/{id}` - Delete document
- `GET /api/v1/documents/stats` - Get collection statistics
- `POST /api/v1/documents/reset` - Reset collection

### 🤖 Chat & AI
- `POST /api/v1/chat/` - Chat with Gemini AI (with RAG)
- `GET /api/v1/chat/conversation/{id}` - Get conversation history
- `DELETE /api/v1/chat/conversation/{id}` - Delete conversation
- `POST /api/v1/chat/session/start` - Start chat session
- `POST /api/v1/chat/session/reset` - Reset chat session
- `GET /api/v1/chat/session/history` - Get chat history

### 🔧 System
- `GET /health` - Health check
- `GET /docs` - API documentation
- `GET /redoc` - Alternative documentation

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

# 2. Add document
curl -X POST "http://localhost:2000/api/v1/documents/" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": ["Python is a versatile programming language"],
    "metadatas": [{"source": "python_intro.txt"}]
  }'

# 3. Chat with AI
curl -X POST "http://localhost:2000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Python?"
  }'
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