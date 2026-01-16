"""Tests for FastAPI endpoints."""

import os

import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

import app.main as main_module
from app.main import app
from src.core import rss_client
from src.core.models import Topic
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


def test_start_chat_endpoint_streams_topics(monkeypatch) -> None:
    """Test /start_chat streams topic events."""
    session = client.post("/session", json={"variant": "US"}).json()
    session_id = session["session_id"]

    def fake_topics(*_args, **_kwargs):
        return {
            "BBC": [
                Topic(
                    headline="News headline",
                    source="BBC",
                    url="https://example.com/news",
                )
            ]
        }

    monkeypatch.setattr(rss_client.get_client(),
                        "get_topics_from_multiple_sources", fake_topics)

    with client.stream("POST", "/start_chat", json={"session_id": session_id}) as response:
        assert response.status_code == 200
        lines = [line for line in response.iter_lines() if line]

    assert any(line.startswith("data: ") for line in lines)


def test_start_chat_endpoint_invalid_session() -> None:
    """Test /start_chat returns 404 for unknown session."""
    response = client.post("/start_chat", json={"session_id": "missing"})
    assert response.status_code == 404


def test_chat_endpoint_streams_response(monkeypatch) -> None:
    """Test /chat streams agent response and expressions."""
    session = client.post("/session", json={"variant": "US"}).json()
    session_id = session["session_id"]

    class FakeWorkflow:
        def invoke(self, state):
            return {
                "messages": [
                    *state["messages"],
                    AIMessage(content="Hello [[a piece of cake::easy]]"),
                ],
                "turn_count": state["turn_count"] + 1,
            }

    monkeypatch.setattr(main_module, "create_agent_workflow",
                        lambda: FakeWorkflow())

    with client.stream(
        "POST",
        "/chat",
        json={"session_id": session_id, "message": "Hi"},
    ) as response:
        assert response.status_code == 200
        lines = [line for line in response.iter_lines() if line]

    assert any("\"type\": \"chunk\"" in line for line in lines)
    assert any("\"type\": \"expressions\"" in line for line in lines)
    assert any("\"type\": \"done\"" in line for line in lines)


def test_chat_endpoint_invalid_session() -> None:
    """Test /chat returns 404 for unknown session."""
    response = client.post(
        "/chat", json={"session_id": "missing", "message": "Hi"})
    assert response.status_code == 404


def test_smoke_endpoint_requires_azure_env() -> None:
    """Smoke test hits Azure when env vars are configured."""
    if not os.getenv("AZURE_OPENAI_ENDPOINT") or not os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"):
        pytest.skip("Azure OpenAI env vars not set")

    response = client.get("/smoke")
    assert response.status_code == 200


def test_smoke_endpoint_returns_401_for_missing_config(monkeypatch) -> None:
    def raise_missing_config():
        raise ValueError(
            "Missing Azure OpenAI configuration in environment variables")

    monkeypatch.setattr(main_module, "build_llm", raise_missing_config)

    response = client.get("/smoke")
    assert response.status_code == 401
    assert "configuration" in response.json()["detail"]


def test_smoke_endpoint_returns_403_for_forbidden(monkeypatch) -> None:
    class ForbiddenError(Exception):
        status_code = 403

    class FakeLLM:
        def invoke(self, _messages):
            raise ForbiddenError("forbidden")

    monkeypatch.setattr(main_module, "build_llm", lambda: FakeLLM())

    response = client.get("/smoke")
    assert response.status_code == 403
    assert "permission" in response.json()["detail"]


def test_smoke_endpoint_returns_504_for_timeout(monkeypatch) -> None:
    class FakeLLM:
        def invoke(self, _messages):
            raise TimeoutError("timeout")

    monkeypatch.setattr(main_module, "build_llm", lambda: FakeLLM())

    response = client.get("/smoke")
    assert response.status_code == 504
    assert "timed out" in response.json()["detail"]


def test_smoke_endpoint_returns_502_for_network_error(monkeypatch) -> None:
    class FakeLLM:
        def invoke(self, _messages):
            raise OSError("network down")

    monkeypatch.setattr(main_module, "build_llm", lambda: FakeLLM())

    response = client.get("/smoke")
    assert response.status_code == 502
    assert "network" in response.json()["detail"]
