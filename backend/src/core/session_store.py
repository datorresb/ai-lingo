"""In-memory session store for agent state."""

from __future__ import annotations

from threading import Lock
from uuid import uuid4

from src.core.models import AgentState

_session_store: dict[str, AgentState] = {}
_store_lock = Lock()


def create_session(variant: str) -> tuple[str, AgentState]:
    """Create a new session and initialize agent state."""

    session_id = str(uuid4())
    state = AgentState(variant=variant)
    with _store_lock:
        _session_store[session_id] = state
    return session_id, state


def get_session(session_id: str) -> AgentState | None:
    """Retrieve a session by id."""

    with _store_lock:
        return _session_store.get(session_id)


def update_session(session_id: str, **updates: object) -> AgentState | None:
    """Update fields on an existing session state."""

    with _store_lock:
        state = _session_store.get(session_id)
        if state is None:
            return None
        for key, value in updates.items():
            if hasattr(state, key):
                setattr(state, key, value)
        return state


def reset_store() -> None:
    """Clear the in-memory session store (for tests)."""

    with _store_lock:
        _session_store.clear()
