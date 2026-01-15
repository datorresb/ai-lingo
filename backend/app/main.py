"""FastAPI application entry point for Expression Learner Agent."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
