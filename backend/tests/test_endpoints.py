"""Tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from src.core.session_store import get_session, reset_store

client = TestClient(app)


def setup_function() -> None:
    """Reset session store before each test."""
    reset_store()


def test_root_endpoint() -> None:
    """Test metadata endpoint returns service info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert "description" in data
    assert "status" in data
    assert data["status"] == "running"
    assert data["service"] == "Expression Learner Agent"


def test_health_check_endpoint() -> None:
    """Test health check endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_session_endpoint_creates_session() -> None:
    """Test /session endpoint creates session and stores state."""
    response = client.post("/session", json={"variant": "US"})
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"]
    assert data["variant"] == "US"
    assert data["created_at"]

    stored = get_session(data["session_id"])
    assert stored is not None
    assert stored.variant == "US"


def test_session_endpoint_rejects_invalid_variant() -> None:
    """Test /session endpoint rejects invalid variants."""
    response = client.post("/session", json={"variant": "ZZ"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid variant"
