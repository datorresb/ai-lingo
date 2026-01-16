"""Tests for LLM validation helpers."""

from src.core.llm_validation import classify_llm_exception


class _StatusError(Exception):
    def __init__(self, status_code: int):
        super().__init__("status error")
        self.status_code = status_code


def test_classify_missing_config() -> None:
    status, detail = classify_llm_exception(
        ValueError("Missing Azure OpenAI configuration in environment variables")
    )
    assert status == 401
    assert "configuration" in detail


def test_classify_status_unauthorized() -> None:
    status, detail = classify_llm_exception(_StatusError(401))
    assert status == 401
    assert "authentication" in detail


def test_classify_status_forbidden() -> None:
    status, detail = classify_llm_exception(_StatusError(403))
    assert status == 403
    assert "permission" in detail


def test_classify_timeout() -> None:
    status, detail = classify_llm_exception(TimeoutError("timeout"))
    assert status == 504
    assert "timed out" in detail


def test_classify_network_error() -> None:
    status, detail = classify_llm_exception(OSError("network"))
    assert status == 502
    assert "network" in detail


def test_classify_default() -> None:
    status, detail = classify_llm_exception(Exception("boom"))
    assert status == 503
    assert "LLM" in detail
