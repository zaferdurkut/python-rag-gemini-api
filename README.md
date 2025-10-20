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
- **PostgreSQL**: Primary database
- **Redis**: Caching ve session management
- **Docker**: Containerization
- **Authentication**: JWT-based authentication
- **Middleware**: Logging, security, rate limiting
- **Testing**: Pytest ile test coverage

## 🛠️ Teknolojiler

- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
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
cp .env.example .env
# .env dosyasını düzenleyin
```

### 5. Docker ile çalıştırın

```bash
docker-compose up -d
```

## 🐳 Docker

### Development

```bash
docker-compose up -d
```

### Production

```bash
docker-compose -f docker-compose.prod.yml up -d
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

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

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

### Authentication
- `POST /api/v1/token` - Login
- `GET /api/v1/users/me` - Get current user

### Users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/` - List users
- `GET /api/v1/users/{id}` - Get user by ID
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

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
