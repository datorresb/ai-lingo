"""Agent state definitions for LangGraph workflow.

Defines the AgentState used across the LangGraph workflow and helpers
for initializing state from session metadata.
"""

from typing import Optional, TypedDict

from langchain_core.messages import BaseMessage

from src.core.models import Expression


class AgentState(TypedDict):
    """State container for the Expression Learner agent.

    Fields:
        messages: List of LangChain messages in the conversation
        variant: Language variant (US, UK, etc.)
        topic: Current discussion topic
        last_expressions: Expressions extracted from last assistant response
        turn_count: Number of completed assistant turns
    """

    messages: list[BaseMessage]
    variant: str
    topic: Optional[str]
    last_expressions: list[Expression]
    turn_count: int


def create_initial_state(variant: str, topic: Optional[str] = None) -> AgentState:
    """Create an initial AgentState for a new session.

    Args:
        variant: Language variant (US, UK, etc.)
        topic: Optional discussion topic

    Returns:
        Initialized AgentState
    """

    return {
        "messages": [],
        "variant": variant,
        "topic": topic,
        "last_expressions": [],
        "turn_count": 0,
    }
