"""Centralised error handlers for the API."""

from __future__ import annotations

from typing import Any

from flask import Flask, Response, current_app, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from .extensions import db


def register_error_handlers(app: Flask) -> None:
    """Register application-wide error handlers."""

    @app.errorhandler(404)
    def handle_not_found(error) -> Response:
        return jsonify({"error": "not_found", "message": "Resource not found."}), 404

    @app.errorhandler(400)
    def handle_bad_request(error) -> Response:
        return jsonify({"error": "bad_request", "message": "Bad request."}), 400

    @app.errorhandler(ValidationError)
    def handle_validation_error(err: ValidationError) -> Response:
        """Convert marshmallow validation errors into JSON responses."""

        return (
            jsonify(
                {
                    "error": "validation_error",
                    "message": "Invalid request payload.",
                    "messages": err.messages,
                }
            ),
            400,
        )

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(err: IntegrityError) -> Response:
        """Translate database integrity violations into API errors."""

        db.session.rollback()

        orig = getattr(err, "orig", None)
        raw_message: Any = getattr(orig, "args", [""])[0]
        message = str(raw_message).lower()
        if "users.email" in message:
            return (
                jsonify(
                    {"error": "conflict", "message": "Email is already being used."}
                ),
                409,
            )

        return (
            jsonify(
                {
                    "error": "database_error",
                    "message": "A database integrity error occurred.",
                }
            ),
            400,
        )

    @app.errorhandler(500)
    def handle_internal_error(error) -> Response:  # pragma: no cover - requires env
        current_app.logger.exception(error)
        return (
            jsonify(
                {
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred.",
                }
            ),
            500,
        )
