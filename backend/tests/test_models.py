"""Tests for Pydantic domain models."""

import pytest
from datetime import datetime
from src.core.models import (
    Expression,
    SessionRequest,
    SessionResponse,
    ChatRequest,
    ChatResponse,
    StartChatRequest,
    Topic,
    Message,
    AgentState,
)


class TestExpressionModel:
    """Tests for Expression model."""

    def test_expression_valid(self) -> None:
        """Test creating a valid expression."""
        expr = Expression(phrase="a piece of cake", meaning="something very easy")
        assert expr.phrase == "a piece of cake"
        assert expr.meaning == "something very easy"

    def test_expression_empty_phrase_fails(self) -> None:
        """Test that empty phrase fails validation."""
        with pytest.raises(ValueError):
            Expression(phrase="", meaning="something easy")

    def test_expression_empty_meaning_fails(self) -> None:
        """Test that empty meaning fails validation."""
        with pytest.raises(ValueError):
            Expression(phrase="a piece of cake", meaning="")

    def test_expression_phrase_too_long_fails(self) -> None:
        """Test that phrase exceeding max length fails."""
        long_phrase = "a" * 201
        with pytest.raises(ValueError):
            Expression(phrase=long_phrase, meaning="test")


class TestSessionRequestModel:
    """Tests for SessionRequest model."""

    def test_session_request_valid(self) -> None:
        """Test creating a valid session request."""
        req = SessionRequest(variant="US")
        assert req.variant == "US"

    def test_session_request_uk_variant(self) -> None:
        """Test UK variant."""
        req = SessionRequest(variant="UK")
        assert req.variant == "UK"

    def test_session_request_empty_variant_fails(self) -> None:
        """Test that empty variant fails."""
        with pytest.raises(ValueError):
            SessionRequest(variant="")


class TestSessionResponseModel:
    """Tests for SessionResponse model."""

    def test_session_response_valid(self) -> None:
        """Test creating a valid session response."""
        resp = SessionResponse(
            session_id="550e8400-e29b-41d4-a716-446655440000", variant="US"
        )
        assert resp.session_id == "550e8400-e29b-41d4-a716-446655440000"
        assert resp.variant == "US"
        assert isinstance(resp.created_at, datetime)

    def test_session_response_has_timestamp(self) -> None:
        """Test that response includes creation timestamp."""
        resp = SessionResponse(session_id="test-id", variant="UK")
        assert resp.created_at is not None


class TestChatRequestModel:
    """Tests for ChatRequest model."""

    def test_chat_request_valid(self) -> None:
        """Test creating a valid chat request."""
        req = ChatRequest(session_id="test-session", message="Hello, how are you?")
        assert req.session_id == "test-session"
        assert req.message == "Hello, how are you?"

    def test_chat_request_empty_message_fails(self) -> None:
        """Test that empty message fails."""
        with pytest.raises(ValueError):
            ChatRequest(session_id="test", message="")

    def test_chat_request_message_too_long_fails(self) -> None:
        """Test that message exceeding max length fails."""
        long_message = "a" * 2001
        with pytest.raises(ValueError):
            ChatRequest(session_id="test", message=long_message)


class TestChatResponseModel:
    """Tests for ChatResponse model."""

    def test_chat_response_valid(self) -> None:
        """Test creating a valid chat response."""
        resp = ChatResponse(message="Hello!", turn_count=1)
        assert resp.message == "Hello!"
        assert resp.turn_count == 1
        assert resp.expressions == []

    def test_chat_response_with_expressions(self) -> None:
        """Test chat response with expressions."""
        expr = Expression(phrase="piece of cake", meaning="easy")
        resp = ChatResponse(message="That's a piece of cake!", expressions=[expr], turn_count=1)
        assert len(resp.expressions) == 1
        assert resp.expressions[0].phrase == "piece of cake"

    def test_chat_response_invalid_turn_count_fails(self) -> None:
        """Test that negative turn count fails."""
        with pytest.raises(ValueError):
            ChatResponse(message="test", turn_count=-1)


class TestTopicModel:
    """Tests for Topic model."""

    def test_topic_valid(self) -> None:
        """Test creating a valid topic."""
        topic = Topic(
            headline="AI Reaches New Milestone",
            source="BBC",
            url="https://bbc.com/news/ai",
        )
        assert topic.headline == "AI Reaches New Milestone"
        assert topic.source == "BBC"
        assert topic.url == "https://bbc.com/news/ai"


class TestMessageModel:
    """Tests for Message model."""

    def test_message_user_valid(self) -> None:
        """Test creating a valid user message."""
        msg = Message(role="user", content="What is AI?")
        assert msg.role == "user"
        assert msg.content == "What is AI?"
        assert isinstance(msg.timestamp, datetime)

    def test_message_assistant_valid(self) -> None:
        """Test creating a valid assistant message."""
        msg = Message(role="assistant", content="AI is...")
        assert msg.role == "assistant"

    def test_message_invalid_role_fails(self) -> None:
        """Test that invalid role fails."""
        with pytest.raises(ValueError):
            Message(role="invalid", content="test")

    def test_message_empty_content_fails(self) -> None:
        """Test that empty content fails."""
        with pytest.raises(ValueError):
            Message(role="user", content="")


class TestAgentStateModel:
    """Tests for AgentState model."""

    def test_agent_state_minimal(self) -> None:
        """Test creating minimal agent state."""
        state = AgentState(variant="US")
        assert state.variant == "US"
        assert state.messages == []
        assert state.topic is None
        assert state.last_expressions == []
        assert state.turn_count == 0

    def test_agent_state_full(self) -> None:
        """Test creating full agent state."""
        msg = Message(role="user", content="Hello")
        expr = Expression(phrase="test", meaning="test phrase")
        state = AgentState(
            variant="UK",
            messages=[msg],
            topic="AI News",
            last_expressions=[expr],
            turn_count=1,
        )
        assert state.variant == "UK"
        assert len(state.messages) == 1
        assert state.topic == "AI News"
        assert len(state.last_expressions) == 1
        assert state.turn_count == 1

    def test_agent_state_negative_turn_count_fails(self) -> None:
        """Test that negative turn count fails."""
        with pytest.raises(ValueError):
            AgentState(variant="US", turn_count=-1)

    def test_agent_state_multiple_messages(self) -> None:
        """Test agent state with multiple messages."""
        messages = [
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi!"),
            Message(role="user", content="How are you?"),
        ]
        state = AgentState(variant="US", messages=messages, turn_count=3)
        assert len(state.messages) == 3
        assert state.messages[0].role == "user"
        assert state.messages[1].role == "assistant"


class TestStartChatRequestModel:
    """Tests for StartChatRequest model."""

    def test_start_chat_request_valid(self) -> None:
        """Test creating a valid start chat request."""
        req = StartChatRequest(session_id="test-session-id")
        assert req.session_id == "test-session-id"
