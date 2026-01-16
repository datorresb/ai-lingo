"""FastAPI application entry point for Expression Learner Agent."""

import json
import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from langchain_core.messages import AIMessage, HumanMessage

from src.agents.agent import build_llm, create_agent_workflow
from src.core.expressions import parse_expressions
from src.core.llm_validation import classify_llm_exception
from src.core.models import ChatRequest, Message, SessionRequest, SessionResponse, StartChatRequest, Topic
from src.core.session_store import create_session, get_session, update_session
from src.core.rss_client import get_client

app = FastAPI(
    title="Expression Learner Agent",
    description="Conversational AI agent for learning English idioms and expressions",
    version="0.1.0",
)

logger = logging.getLogger(__name__)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


VALID_VARIANTS = {"us": "US", "uk": "UK", "custom": "Custom"}


@app.get("/")
async def root() -> dict:
    """Metadata endpoint returning service info."""
    return {
        "service": "Expression Learner Agent",
        "version": "0.1.0",
        "description": "Conversational AI agent for learning English idioms and expressions",
        "status": "running",
    }


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/smoke")
async def smoke_check() -> dict:
    """Validate Azure OpenAI connectivity."""
    try:
        llm = build_llm()
        llm.invoke([HumanMessage(content="ping")])
    except Exception as exc:
        status_code, detail = classify_llm_exception(exc)
        logger.warning("LLM smoke check failed", exc_info=exc)
        raise HTTPException(status_code=status_code, detail=detail) from exc

    return {"status": "ok"}


@app.post("/session", response_model=SessionResponse)
async def create_session_endpoint(request: SessionRequest) -> SessionResponse:
    """Create a new session and initialize agent state."""

    raw_variant = request.variant.strip().lower()
    if raw_variant not in VALID_VARIANTS:
        raise HTTPException(status_code=400, detail="Invalid variant")

    normalized_variant = VALID_VARIANTS[raw_variant]
    session_id, _state = create_session(normalized_variant)
    return SessionResponse(session_id=session_id, variant=normalized_variant)


@app.post("/start_chat")
async def start_chat_endpoint(request: StartChatRequest) -> StreamingResponse:
    """Start chat by streaming a list of topics from RSS feeds."""

    state = get_session(request.session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found")

    def topic_stream():
        client = get_client()
        try:
            topics_by_source = client.get_topics_from_multiple_sources(
                limit_per_source=3)
        except Exception as exc:
            payload = json.dumps({"error": "Failed to fetch topics"})
            yield f"data: {payload}\n\n"
            return

        topics: list[Topic] = []
        for source_topics in topics_by_source.values():
            topics.extend(source_topics)

        if not topics:
            payload = json.dumps({"error": "No topics available"})
            yield f"data: {payload}\n\n"
            return

        for topic in topics[:5]:
            payload = json.dumps(
                {
                    "topic": {
                        "headline": topic.headline,
                        "source": topic.source,
                        "url": topic.url,
                    }
                }
            )
            yield f"data: {payload}\n\n"

        update_session(request.session_id, topic=None)

    return StreamingResponse(topic_stream(), media_type="text/event-stream")


def _to_langchain_messages(messages: list[Message]) -> list[HumanMessage | AIMessage]:
    langchain_messages: list[HumanMessage | AIMessage] = []
    for message in messages:
        if message.role == "user":
            langchain_messages.append(HumanMessage(content=message.content))
        else:
            langchain_messages.append(AIMessage(content=message.content))
    return langchain_messages


def _to_core_messages(messages: list[HumanMessage | AIMessage]) -> list[Message]:
    core_messages: list[Message] = []
    for message in messages:
        if isinstance(message, HumanMessage):
            core_messages.append(Message(role="user", content=message.content))
        elif isinstance(message, AIMessage):
            core_messages.append(
                Message(role="assistant", content=message.content))
    return core_messages


@app.post("/chat")
async def chat_endpoint(request: ChatRequest) -> StreamingResponse:
    """Chat endpoint that streams agent response."""

    state = get_session(request.session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found")

    def chat_stream():
        workflow = create_agent_workflow()
        try:
            langchain_messages = _to_langchain_messages(state.messages)
            langchain_messages.append(HumanMessage(content=request.message))

            result = workflow.invoke(
                {
                    "messages": langchain_messages,
                    "variant": state.variant,
                    "topic": state.topic,
                    "last_expressions": state.last_expressions,
                    "turn_count": state.turn_count,
                }
            )
        except Exception:
            payload = json.dumps({"type": "error", "content": "Agent error"})
            yield f"data: {payload}\n\n"
            return

        messages = result.get("messages", [])
        assistant_message = next(
            (message for message in reversed(messages)
             if isinstance(message, AIMessage)), None
        )

        if assistant_message is None:
            payload = json.dumps(
                {"type": "error", "content": "No assistant response"})
            yield f"data: {payload}\n\n"
            return

        expressions = parse_expressions(assistant_message.content)
        updated_messages = _to_core_messages(messages)
        update_session(
            request.session_id,
            messages=updated_messages,
            last_expressions=expressions,
            turn_count=result.get(
                "turn_count", state.turn_count) or state.turn_count + 1,
        )

        thought_payload = json.dumps(
            {"type": "thought", "content": "Thinking about your question."}
        )
        yield f"data: {thought_payload}\n\n"

        text = assistant_message.content
        chunk_size = 40
        for idx in range(0, len(text), chunk_size):
            payload = json.dumps(
                {"type": "chunk", "content": text[idx: idx + chunk_size]})
            yield f"data: {payload}\n\n"

        expr_payload = json.dumps(
            {
                "type": "expressions",
                "content": [expression.model_dump() for expression in expressions],
            }
        )
        yield f"data: {expr_payload}\n\n"

        done_payload = json.dumps({"type": "done"})
        yield f"data: {done_payload}\n\n"

    return StreamingResponse(chat_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
