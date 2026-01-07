"""
Unit tests for health check endpoint
"""

import pytest
from fastapi import status


@pytest.mark.unit
def test_health_check_returns_200(test_client):
    """Test that health check endpoint returns 200"""
    response = test_client.get("/api/health")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.unit
def test_health_check_structure(test_client):
    """Test that health check returns expected structure"""
    response = test_client.get("/api/health")
    data = response.json()

    assert "status" in data
    assert "version" in data
    assert "timestamp" in data
    assert "services" in data
    assert data["status"] == "healthy"


@pytest.mark.unit
def test_ping_endpoint(test_client):
    """Test simple ping endpoint"""
    response = test_client.get("/api/ping")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "ping" in data
    assert data["ping"] == "pong"


@pytest.mark.unit
def test_root_endpoint(test_client):
    """Test root endpoint returns API information"""
    response = test_client.get("/")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["version"] == "2.0.0"
