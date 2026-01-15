"""Pydantic domain models for Expression Learner Agent.

This module defines all data models used throughout the application,
including request/response models for API endpoints and internal domain models.

Refer to PRD section 5.2 for detailed specifications.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


# ============================================================================
# Expression Models
# ============================================================================


class Expression(BaseModel):
    """Represents an idiom or expression with its meaning.

    Attributes:
        phrase: The idiom or expression (e.g., "a piece of cake")
        meaning: The definition or explanation of the expression
    """

    phrase: str = Field(..., min_length=1, max_length=200, description="The idiom phrase")
    meaning: str = Field(..., min_length=1, max_length=500, description="Meaning/definition")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {"phrase": "a piece of cake", "meaning": "something that is very easy"}
        }


# ============================================================================
# Session Models
# ============================================================================


class SessionRequest(BaseModel):
    """Request model for creating a new session.

    Attributes:
        variant: Language variant (e.g., "US", "UK", "Custom")
    """

    variant: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Language variant (US, UK, Custom, etc.)",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {"example": {"variant": "US"}}


class SessionResponse(BaseModel):
    """Response model after session creation.

    Attributes:
        session_id: Unique identifier for the session
        variant: Confirmed language variant
        created_at: Timestamp of session creation
    """

    session_id: str = Field(..., description="Unique session identifier")
    variant: str = Field(..., description="Language variant")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "variant": "US",
                "created_at": "2026-01-15T10:30:00",
            }
        }


# ============================================================================
# Chat Models
# ============================================================================


class ChatRequest(BaseModel):
    """Request model for chat endpoint.

    Attributes:
        session_id: Session identifier
        message: User message
    """

    session_id: str = Field(..., description="Session ID")
    message: str = Field(..., min_length=1, max_length=2000, description="User message")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "message": "Tell me about AI",
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint.

    Attributes:
        message: Agent's response message
        expressions: List of expressions found in response
        turn_count: Current turn number
    """

    message: str = Field(..., description="Agent response")
    expressions: list[Expression] = Field(default_factory=list, description="Extracted expressions")
    turn_count: int = Field(..., ge=1, description="Turn count")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "message": "That's [[a piece of cake::very easy]]!",
                "expressions": [{"phrase": "a piece of cake", "meaning": "very easy"}],
                "turn_count": 1,
            }
        }


class StartChatRequest(BaseModel):
    """Request model for /start_chat endpoint.

    Attributes:
        session_id: Session identifier
    """

    session_id: str = Field(..., description="Session ID")

    class Config:
        """Pydantic config."""

        json_schema_extra = {"example": {"session_id": "550e8400-e29b-41d4-a716-446655440000"}}


class Topic(BaseModel):
    """Represents a discussion topic from RSS feed.

    Attributes:
        headline: Topic headline
        source: News source (BBC, NYT, etc.)
        url: URL to full article
    """

    headline: str = Field(..., description="Topic headline")
    source: str = Field(..., description="News source")
    url: str = Field(..., description="Article URL")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "headline": "AI Reaches New Milestone",
                "source": "BBC",
                "url": "https://bbc.com/news/ai-milestone",
            }
        }


# ============================================================================
# Agent State Model
# ============================================================================


class Message(BaseModel):
    """Represents a message in conversation history.

    Attributes:
        role: "user" or "assistant"
        content: Message content
        timestamp: When message was created
    """

    role: str = Field(..., pattern="^(user|assistant)$", description="Message role")
    content: str = Field(..., min_length=1, description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")


class AgentState(BaseModel):
    """State of the Expression Learner agent during conversation.

    This model tracks all relevant state for an active conversation session.
    Refer to PRD section 5.2 for detailed specifications.

    Attributes:
        messages: List of message history
        variant: Language variant (US, UK, etc.)
        topic: Current discussion topic
        last_expressions: Most recent expressions extracted
        turn_count: Number of conversation turns
    """

    messages: list[Message] = Field(
        default_factory=list, description="Conversation message history"
    )
    variant: str = Field(..., description="Language variant")
    topic: Optional[str] = Field(default=None, description="Current discussion topic")
    last_expressions: list[Expression] = Field(
        default_factory=list, description="Recently extracted expressions"
    )
    turn_count: int = Field(default=0, ge=0, description="Number of conversation turns")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello",
                        "timestamp": "2026-01-15T10:30:00",
                    },
                    {
                        "role": "assistant",
                        "content": "Hi there!",
                        "timestamp": "2026-01-15T10:30:05",
                    },
                ],
                "variant": "US",
                "topic": "AI News",
                "last_expressions": [
                    {"phrase": "up and running", "meaning": "operational and working"}
                ],
                "turn_count": 1,
            }
        }
