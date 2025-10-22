import pytest
from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)


def test_read_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_docs_endpoint():
    """Test that docs endpoint is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
