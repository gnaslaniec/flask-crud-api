"""Simple request guards for role-based access control."""

from __future__ import annotations

from functools import wraps
from typing import Callable, TypeVar

from flask import Response, jsonify, request

F = TypeVar("F", bound=Callable[..., Response])


def require_manager(func: F) -> F:
    """Decorate an endpoint to ensure only managers can mutate data."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        role = request.headers.get("X-User-Role")
        if role != "manager":
            return (
                jsonify(
                    {
                        "error": "forbidden",
                        "message": "Manager role required for this operation.",
                    }
                ),
                403,
            )
        return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]
