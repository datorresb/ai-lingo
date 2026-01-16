"""LLM validation and error classification helpers."""

from __future__ import annotations

from typing import Tuple


def _is_timeout_error(exc: Exception) -> bool:
    if isinstance(exc, TimeoutError):
        return True

    try:  # pragma: no cover - optional dependency
        import httpx

        if isinstance(exc, httpx.TimeoutException):
            return True
    except Exception:  # pragma: no cover - fallback when httpx unavailable
        pass

    try:  # pragma: no cover - optional dependency
        from openai import APITimeoutError

        if isinstance(exc, APITimeoutError):
            return True
    except Exception:  # pragma: no cover - fallback when openai unavailable
        pass

    try:  # pragma: no cover - optional dependency
        from azure.core.exceptions import ServiceRequestError

        if isinstance(exc, ServiceRequestError) and "timed out" in str(exc).lower():
            return True
    except Exception:  # pragma: no cover - fallback when azure-core unavailable
        pass

    return False


def _is_network_error(exc: Exception) -> bool:
    if isinstance(exc, OSError):
        return True

    try:  # pragma: no cover - optional dependency
        import httpx

        if isinstance(exc, httpx.RequestError):
            return True
    except Exception:  # pragma: no cover - fallback when httpx unavailable
        pass

    try:  # pragma: no cover - optional dependency
        from openai import APIConnectionError

        if isinstance(exc, APIConnectionError):
            return True
    except Exception:  # pragma: no cover - fallback when openai unavailable
        pass

    try:  # pragma: no cover - optional dependency
        from azure.core.exceptions import ServiceRequestError, ServiceResponseError

        if isinstance(exc, (ServiceRequestError, ServiceResponseError)):
            return True
    except Exception:  # pragma: no cover - fallback when azure-core unavailable
        pass

    return False


def classify_llm_exception(exc: Exception) -> Tuple[int, str]:
    """Classify LLM exceptions into HTTP status codes and messages."""

    if isinstance(exc, ValueError) and "Azure OpenAI configuration" in str(exc):
        return 401, "Azure OpenAI configuration missing"

    try:  # pragma: no cover - optional dependency
        from openai import AuthenticationError, PermissionDeniedError

        if isinstance(exc, AuthenticationError):
            return 401, "Azure OpenAI authentication failed"
        if isinstance(exc, PermissionDeniedError):
            return 403, "Azure OpenAI permission denied"
    except Exception:  # pragma: no cover - fallback when openai unavailable
        pass

    try:  # pragma: no cover - optional dependency
        from azure.core.exceptions import ClientAuthenticationError

        if isinstance(exc, ClientAuthenticationError):
            return 401, "Azure OpenAI authentication failed"
    except Exception:  # pragma: no cover - fallback when azure-core unavailable
        pass

    status_code = getattr(exc, "status_code", None)
    if status_code == 401:
        return 401, "Azure OpenAI authentication failed"
    if status_code == 403:
        return 403, "Azure OpenAI permission denied"

    if _is_timeout_error(exc):
        return 504, "Azure OpenAI request timed out"

    if _is_network_error(exc):
        return 502, "Azure OpenAI network error"

    return 503, "LLM unavailable"
