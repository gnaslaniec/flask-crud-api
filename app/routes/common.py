"""Shared helpers and lightweight routes for API modules."""

from __future__ import annotations

from typing import Any, Dict

from flask import Response, current_app, jsonify, request

from ..errors import BusinessValidationError
from . import api_bp


@api_bp.route("/health", methods=["GET"])
def health() -> Response:
    """Expose a minimal health check endpoint."""

    return json_response({"status": "ok"})


def json_response(
    payload: Dict[str, Any], status: int = 200, meta: Dict[str, Any] | None = None
) -> Response:
    """Return a consistently formatted JSON response."""

    response_payload = dict(payload)
    if meta:
        response_payload["meta"] = meta
    return jsonify(response_payload), status


def get_pagination_params() -> tuple[int, int]:
    """Parse pagination parameters from the query string."""

    page_default = current_app.config["PAGINATION_DEFAULT_PAGE"]
    page_size_default = current_app.config["PAGINATION_DEFAULT_PAGE_SIZE"]
    max_per_page = current_app.config["PAGINATION_MAX_PAGE_SIZE"]

    try:
        page = int(request.args.get("page", page_default))
        per_page = int(request.args.get("per_page", page_size_default))
    except ValueError as exc:
        raise BusinessValidationError("Pagination parameters must be integers.") from exc

    if page < 1:
        raise BusinessValidationError("Page must be greater than or equal to 1.")

    if per_page < 1:
        raise BusinessValidationError("per_page must be greater than or equal to 1.")

    if per_page > max_per_page:
        raise BusinessValidationError(
            f"per_page must be less than or equal to {max_per_page}."
        )

    return page, per_page


__all__ = ["get_pagination_params", "json_response"]
