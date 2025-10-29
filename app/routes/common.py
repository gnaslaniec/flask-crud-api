"""Shared helpers for API route modules."""

from __future__ import annotations

from typing import Any, Dict, TypeVar

from flask import Response, abort, jsonify

from ..extensions import db

ModelT = TypeVar("ModelT")


def json_response(payload: Dict[str, Any], status: int = 200) -> Response:
    """Return a consistently formatted JSON response."""

    return jsonify(payload), status


def get_or_404(model: type[ModelT], ident: int) -> ModelT:
    """Fetch a model by primary key or abort with 404 if missing."""

    instance = db.session.get(model, ident)
    if instance is None:
        abort(404)
    return instance
