"""FastAPI application entry point for Expression Learner Agent."""

import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from src.core.models import SessionRequest, SessionResponse, StartChatRequest, Topic
from src.core.session_store import create_session, get_session, update_session
from src.core.rss_client import get_client

app = FastAPI(
    title="Expression Learner Agent",
    description="Conversational AI agent for learning English idioms and expressions",
    version="0.1.0",
)

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
            topics_by_source = client.get_topics_from_multiple_sources(limit_per_source=3)
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
