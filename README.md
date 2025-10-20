# FastAPI Hexagonal Architecture

Bu proje, FastAPI kullanarak hexagonal architecture (ports and adapters) pattern'i ile geliştirilmiş bir REST API uygulamasıdır.

## 🏗️ Mimari

Proje hexagonal architecture pattern'ini takip eder:

```
app/
├── core/           # Core business logic ve configuration
├── domain/         # Domain entities ve repository interfaces
├── application/    # Use cases ve business logic
├── infrastructure/ # External services (database, redis, etc.)
└── presentation/   # FastAPI endpoints ve middleware
```

## 🚀 Özellikler

- **Hexagonal Architecture**: Clean architecture principles
- **FastAPI**: Modern, fast web framework
- **ChromaDB**: Vector database for RAG (Retrieval-Augmented Generation)
- **Redis**: Caching ve session management
- **Gemini AI**: Google's generative AI integration
- **Docker**: Containerization
- **Authentication**: JWT-based authentication
- **Middleware**: Logging, security, rate limiting
- **Testing**: Pytest ile test coverage
- **RAG System**: Intelligent document retrieval and AI-powered responses

## 🛠️ Teknolojiler

- Python 3.11+
- FastAPI
- ChromaDB (Vector Database)
- Redis
- Google Gemini AI
- Docker & Docker Compose
- Pytest

## 📦 Kurulum

### 1. Repository'yi klonlayın

```bash
git clone <repository-url>
cd python-rag-gemini-api
```

### 2. Virtual environment oluşturun

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows
```

### 3. Dependencies'leri yükleyin

```bash
pip install -r requirements.txt
```

### 4. Environment variables'ları ayarlayın

```bash
# .env dosyası otomatik oluşturulacak
# GEMINI_API_KEY'inizi ayarlayın
```

### 5. Docker ile çalıştırın

```bash
# Hızlı başlatma
./start.sh

# Veya manuel olarak
docker-compose up -d
```

## 🐳 Docker Services

Bu proje aşağıdaki servisleri içerir:

- **FastAPI App** (Port 2000): Ana uygulama
- **ChromaDB** (Port 8001): Vector database
- **Redis** (Port 6379): Cache ve session storage

### Development

```bash
# Tüm servisleri başlat
./start.sh

# Veya manuel olarak
docker-compose up -d
```

### Servis Durumunu Kontrol Et

```bash
# Servis durumunu kontrol et
docker-compose ps

# Logları görüntüle
docker-compose logs -f

# Belirli servis logları
docker-compose logs -f app
docker-compose logs -f chroma
docker-compose logs -f redis
```

## 🧪 Testing

```bash
# Tüm testleri çalıştır
pytest

# Coverage ile test
pytest --cov=app

# Specific test file
pytest tests/test_main.py
```

## 📚 API Documentation

Uygulama çalıştıktan sonra:

- **Swagger UI**: http://localhost:2000/docs
- **ReDoc**: http://localhost:2000/redoc
- **Health Check**: http://localhost:2000/health
- **ChromaDB UI**: http://localhost:8000

## 🧠 ChromaDB & RAG System

Bu proje ChromaDB kullanarak RAG (Retrieval-Augmented Generation) sistemi içerir:

### ChromaDB Özellikleri
- **Vector Storage**: Dokümanları vektör olarak saklar
- **Similarity Search**: Benzer içerik arama
- **Metadata Filtering**: Metadata ile filtreleme
- **Persistent Storage**: Kalıcı veri saklama

### RAG Sistemi Nasıl Çalışır
1. **Document Ingestion**: Dokümanlar ChromaDB'ye eklenir
2. **Vector Embedding**: Dokümanlar vektörlere dönüştürülür
3. **Query Processing**: Kullanıcı sorusu vektöre dönüştürülür
4. **Similarity Search**: Benzer dokümanlar bulunur
5. **Context Retrieval**: İlgili içerik Gemini'ye gönderilir
6. **AI Response**: Gemini, context ile birlikte cevap üretir

### Örnek Kullanım

```python
# Doküman ekleme
POST /documents/
{
    "documents": [
        "Python is a programming language",
        "FastAPI is a web framework"
    ],
    "metadatas": [
        {"category": "programming"},
        {"category": "web"}
    ]
}

# Benzer doküman arama
POST /documents/search
{
    "query": "What is Python?",
    "n_results": 3
}

# RAG ile chat
POST /chat/
{
    "message": "Tell me about Python programming",
    "conversation_id": "optional"
}
```

### Demo Script
ChromaDB entegrasyonunu test etmek için:

```bash
python example_chroma_usage.py
```

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

## 🌐 Endpoints

### Chat & AI
- `POST /chat/` - Chat with Gemini AI (with RAG)
- `GET /chat/conversation/{id}` - Get conversation history
- `DELETE /chat/conversation/{id}` - Delete conversation
- `POST /chat/session/start` - Start chat session
- `POST /chat/session/reset` - Reset chat session
- `GET /chat/session/history` - Get chat history

### Document Management (RAG)
- `POST /documents/` - Add documents to knowledge base
- `POST /documents/search` - Search similar documents
- `GET /documents/{id}` - Get specific document
- `PUT /documents/{id}` - Update document
- `DELETE /documents/{id}` - Delete document
- `GET /documents/stats` - Get collection statistics
- `POST /documents/reset` - Reset collection

## 🔒 Security Features

- JWT Authentication
- Password hashing (bcrypt)
- CORS protection
- Security headers
- Rate limiting
- Input validation

## 📊 Monitoring

- Health check endpoint: `/health`
- Request logging
- Performance metrics
- Error handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.
