"""LangGraph workflow for the Expression Learner agent.

Implements a ReAct-style state graph with an agent node and tools node,
backed by LangChain and Azure OpenAI.
"""

from __future__ import annotations

import os
from typing import Callable, Iterable, Optional

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, StateGraph

from src.agents.state import AgentState
from src.core.expressions import parse_expressions
from src.core.rss_client import get_article_snippet, list_topics


DEFAULT_API_VERSION = "2024-02-15-preview"


def build_llm() -> AzureChatOpenAI:
    """Create an Azure OpenAI chat model using environment configuration."""

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", DEFAULT_API_VERSION)

    if not endpoint or not deployment:
        raise ValueError("Missing Azure OpenAI configuration in environment variables")

    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if api_key:
        return AzureChatOpenAI(
            azure_endpoint=endpoint,
            deployment_name=deployment,
            api_version=api_version,
            api_key=api_key,
        )

    try:
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    except ImportError as exc:  # pragma: no cover - exercised in production
        raise ImportError("azure-identity is required for managed identity auth") from exc

    credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")

    return AzureChatOpenAI(
        azure_endpoint=endpoint,
        deployment_name=deployment,
        api_version=api_version,
        azure_ad_token_provider=token_provider,
    )


def build_tools() -> list[Callable]:
    """Build LangChain tools for RSS operations."""

    @tool("list_topics")
    def list_topics_tool(feed_url: str, limit: int = 5) -> str:
        """List top topics from the RSS feed."""

        topics = list_topics(feed_url=feed_url, limit=limit)
        return "\n".join(f"{topic.headline} ({topic.source})" for topic in topics)

    @tool("get_article_snippet")
    def get_article_snippet_tool(url: str) -> str:
        """Get a short snippet for a news article URL."""

        snippet = get_article_snippet(url)
        return snippet or ""

    return [list_topics_tool, get_article_snippet_tool]


def build_system_message(variant: str, topic: Optional[str]) -> SystemMessage:
    """Create the system prompt for the agent."""

    topic_text = f"Topic: {topic}." if topic else ""
    content = (
        f"You are a helpful {variant} English native speaker. {topic_text} "
        "Use idioms naturally and format them as [[phrase::meaning]]."
    )
    return SystemMessage(content=content.strip())


def create_agent_node(llm: Callable) -> Callable[[AgentState], dict]:
    """Create the agent node function for the LangGraph workflow."""

    def agent_node(state: AgentState) -> dict:
        messages: list[BaseMessage] = state["messages"]
        system_message = build_system_message(state["variant"], state.get("topic"))
        response = llm.invoke([system_message, *messages])

        updated_messages = [*messages, response]
        updates: dict = {"messages": updated_messages}

        tool_calls = getattr(response, "tool_calls", None)
        if tool_calls:
            return updates

        updates["turn_count"] = state.get("turn_count", 0) + 1
        updates["last_expressions"] = parse_expressions(response.content)
        return updates

    return agent_node


def create_tools_node(tools: Iterable[Callable]) -> Callable[[AgentState], dict]:
    """Create the tools node that executes tool calls from the LLM."""

    tool_map = {tool_func.name: tool_func for tool_func in tools}

    def tools_node(state: AgentState) -> dict:
        messages = state["messages"]
        if not messages:
            return {}

        last_message = messages[-1]
        tool_calls = getattr(last_message, "tool_calls", [])
        if not tool_calls:
            return {}

        tool_messages: list[ToolMessage] = []
        for call in tool_calls:
            tool_name = call.get("name")
            tool_args = call.get("args", {})
            tool = tool_map.get(tool_name)
            if not tool:
                continue
            result = tool.invoke(tool_args)
            tool_messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=call.get("id", tool_name or "tool_call"),
                )
            )

        return {"messages": [*messages, *tool_messages]}

    return tools_node


def should_continue(state: AgentState) -> str:
    """Route to tools if the last assistant message requested a tool."""

    if not state.get("messages"):
        return END

    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and getattr(last_message, "tool_calls", None):
        return "tools"

    return END


def create_agent_workflow(llm: Optional[Callable] = None):
    """Create and compile the LangGraph workflow for the agent."""

    tools = build_tools()
    model = llm or build_llm()
    if hasattr(model, "bind_tools"):
        model = model.bind_tools(tools)

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", create_agent_node(model))
    workflow.add_node("tools", create_tools_node(tools))

    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")

    return workflow.compile()
