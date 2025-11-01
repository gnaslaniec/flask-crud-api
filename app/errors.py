"""Centralised error handlers for the API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from flask import Flask, Response, current_app, jsonify
from flask_limiter.errors import RateLimitExceeded
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from .extensions import db


@dataclass(frozen=True)
class ErrorPayload:
    """Lightweight container for error responses."""

    error: str
    message: str
    details: Optional[Dict[str, Any]] = None


class APIError(Exception):
    """Base class for predictable API errors."""

    status_code: int = 400
    error_code: str = "bad_request"

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code or self.status_code
        self.error_code = error_code or self.error_code
        self.details = details


class UnauthorizedError(APIError):
    """Raised when authentication fails."""

    status_code = 401
    error_code = "unauthorized"


class ForbiddenError(APIError):
    """Raised when authorisation fails."""

    status_code = 403
    error_code = "forbidden"


class NotFoundError(APIError):
    """Raised when a requested resource does not exist."""

    status_code = 404
    error_code = "not_found"


class ConflictError(APIError):
    """Raised when a resource conflicts with existing state."""

    status_code = 409
    error_code = "conflict"


class BusinessValidationError(APIError):
    """Raised when business rules are violated."""

    status_code = 422
    error_code = "business_validation_error"


def register_error_handlers(app: Flask) -> None:
    """Register application-wide error handlers."""

    @app.errorhandler(APIError)
    def handle_api_error(err: APIError) -> Response:
        payload = ErrorPayload(err.error_code, err.message, err.details)
        return jsonify(_serialize_error(payload)), err.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(err: ValidationError) -> Response:
        """Convert marshmallow validation errors into JSON responses."""

        payload = ErrorPayload(
            "validation_error",
            "Invalid request payload.",
            {"messages": err.messages},
        )
        return jsonify(_serialize_error(payload)), 400

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(err: IntegrityError) -> Response:
        """Translate database integrity violations into API errors."""

        db.session.rollback()

        orig = getattr(err, "orig", None)
        raw_message: Any = getattr(orig, "args", [""])[0]
        message = str(raw_message).lower()
        if "users.email" in message:
            payload = ErrorPayload("conflict", "Email is already being used.")
            return jsonify(_serialize_error(payload)), 409

        payload = ErrorPayload(
            "database_error", "A database integrity error occurred."
        )
        return jsonify(_serialize_error(payload)), 400

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit(err: RateLimitExceeded) -> Response:
        payload = ErrorPayload(
            "rate_limit_exceeded",
            "Too many requests, please try again later.",
            {"limit": str(err.limit)},
        )
        return jsonify(_serialize_error(payload)), 429

    @app.errorhandler(404)
    def handle_not_found(error) -> Response:
        payload = ErrorPayload("not_found", "Resource not found.")
        return jsonify(_serialize_error(payload)), 404

    @app.errorhandler(400)
    def handle_bad_request(error) -> Response:
        payload = ErrorPayload("bad_request", "Bad request.")
        return jsonify(_serialize_error(payload)), 400

    @app.errorhandler(500)
    def handle_internal_error(error) -> Response:  # pragma: no cover - requires env
        current_app.logger.exception(error)
        payload = ErrorPayload(
            "internal_server_error",
            "An unexpected error occurred.",
        )
        return jsonify(_serialize_error(payload)), 500


def _serialize_error(payload: ErrorPayload) -> Dict[str, Any]:
    """Serialize an ErrorPayload to a dict while omitting empty details."""

    data: Dict[str, Any] = {"error": payload.error, "message": payload.message}
    if payload.details:
        data.update(payload.details)
    return data


__all__ = [
    "APIError",
    "BusinessValidationError",
    "ConflictError",
    "ForbiddenError",
    "NotFoundError",
    "UnauthorizedError",
    "register_error_handlers",
]
