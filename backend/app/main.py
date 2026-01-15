"""FastAPI application entry point for Expression Learner Agent."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.core.models import SessionRequest, SessionResponse
from src.core.session_store import create_session

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
