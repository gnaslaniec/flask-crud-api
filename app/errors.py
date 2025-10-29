"""Centralised error handlers for the API."""

from __future__ import annotations

from flask import Flask, Response, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .routes import api_bp


def register_error_handlers(app: Flask) -> None:
    """Register application-wide error handlers."""

    @app.errorhandler(404)
    def handle_not_found(error) -> Response:  # pragma: no cover - simple handler
        return jsonify({"error": "not_found", "message": "Resource not found."}), 404

    @app.errorhandler(400)
    def handle_bad_request(error) -> Response:  # pragma: no cover - simple handler
        return jsonify({"error": "bad_request", "message": "Bad request."}), 400


@api_bp.errorhandler(ValidationError)
def handle_validation_error(err: ValidationError) -> Response:
    """Convert marshmallow validation errors into JSON responses."""

    return jsonify({"error": "validation_error", "messages": err.messages}), 400


@api_bp.errorhandler(IntegrityError)
def handle_integrity_error(err: IntegrityError) -> Response:
    """Translate database integrity violations into API errors."""

    db.session.rollback()

    message = str(err.orig).lower()
    if "users.email" in message or "users.email" in getattr(err.orig, "args", [""])[0]:
        return jsonify({"error": "conflict", "message": "Email is already being used."}), 409

    return (
        jsonify(
            {
                "error": "database_error",
                "message": "A database integrity error occurred.",
            }
        ),
        400,
    )
