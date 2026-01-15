"""Tests for LangGraph agent workflow with mock LLM."""

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from src.agents.agent import create_agent_workflow
from src.agents.state import create_initial_state
from src.core.models import Topic
from src.core import rss_client


class FakeLLM:
    """Simple mock LLM that first calls a tool, then responds."""

    def __init__(self) -> None:
        self.calls = 0

    def bind_tools(self, tools):
        self.tools = tools
        return self

    def invoke(self, messages):
        self.calls += 1
        if self.calls == 1:
            return AIMessage(
                content="Let's fetch topics.",
                tool_calls=[
                    {
                        "id": "call_1",
                        "name": "list_topics",
                        "args": {"feed_url": "https://example.com/rss", "limit": 1},
                    }
                ],
            )

        return AIMessage(
            content="We could discuss [[big news::important updates]] today.",
        )


def test_agent_workflow_with_tools(monkeypatch):
    """End-to-end flow executes tool call and completes a turn."""

    monkeypatch.setattr(
        rss_client,
        "list_topics",
        lambda feed_url, limit=5: [
            Topic(headline="Big news headline", source="BBC", url="https://example.com")
        ],
    )
    monkeypatch.setattr(rss_client, "get_article_snippet", lambda url: "Snippet")

    workflow = create_agent_workflow(llm=FakeLLM())
    state = create_initial_state("US")
    state["messages"] = [HumanMessage(content="Hi there")]

    result = workflow.invoke(state)

    assert result["turn_count"] == 1
    assert result["last_expressions"]
    assert result["last_expressions"][0].phrase == "big news"
    assert any(isinstance(msg, ToolMessage) for msg in result["messages"])
