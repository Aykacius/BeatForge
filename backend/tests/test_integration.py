"""Integration tests."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_root(client):
    """Test API root endpoint."""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data
