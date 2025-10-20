#!/bin/bash

# RAG System Startup Script
echo "🚀 Starting RAG System with ChromaDB"
echo "====================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.template .env
    echo "⚠️  Please edit .env file and set your GEMINI_API_KEY"
    echo "   You can get your API key from: https://makersuite.google.com/app/apikey"
    read -p "Press Enter to continue after setting your API key..."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it first."
    exit 1
fi

echo "📦 Building and starting services..."
docker-compose up -d --build

echo "⏳ Waiting for services to be ready..."
sleep 10

echo "🔍 Checking service health..."
echo "FastAPI App: http://localhost:2000"
echo "ChromaDB: http://localhost:8000"

echo ""
echo "📚 API Documentation:"
echo "- Swagger UI: http://localhost:2000/docs"
echo "- ReDoc: http://localhost:2000/redoc"
echo "- Health Check: http://localhost:2000/health"

echo ""
echo "🧪 Test the system:"
echo "Visit http://localhost:2000/docs to test the API"

echo ""
echo "✅ RAG System is ready!"
echo "Add documents to ChromaDB and search for similar content!"
