"""User-related API routes."""

from __future__ import annotations

from flask import Response, current_app, request

from ..auth import require_auth, require_manager
from ..extensions import limiter
from ..schemas import UserSchema
from ..services import (
    create_user as create_user_service,
    delete_user as delete_user_service,
    get_user as get_user_service,
    list_users as list_users_service,
    update_user as update_user_service,
)
from . import api_bp
from .common import get_pagination_params, json_response

user_schema = UserSchema()
users_schema = UserSchema(many=True)


@api_bp.route("/users", methods=["POST"])
@require_manager
@limiter.limit(lambda: current_app.config["SENSITIVE_RATE_LIMIT"])
def create_user() -> Response:
    """Create a new user."""

    data = user_schema.load(request.get_json() or {})
    user = create_user_service(data)
    return json_response({"data": user_schema.dump(user)}, 201)


@api_bp.route("/users", methods=["GET"])
@require_auth
def list_users() -> Response:
    """Return paginated users."""

    page, per_page = get_pagination_params()
    users, meta = list_users_service(page=page, per_page=per_page)
    return json_response({"data": users_schema.dump(users)}, meta=meta)


@api_bp.route("/users/<int:user_id>", methods=["GET"])
@require_auth
def get_user(user_id: int) -> Response:
    """Fetch a single user."""

    user = get_user_service(user_id)
    return json_response({"data": user_schema.dump(user)})


@api_bp.route("/users/<int:user_id>", methods=["PUT"])
@require_manager
@limiter.limit(lambda: current_app.config["SENSITIVE_RATE_LIMIT"])
def update_user(user_id: int) -> Response:
    """Update an existing user."""

    payload = request.get_json() or {}
    data = user_schema.load(payload, partial=True)
    user = update_user_service(user_id, payload, data)
    return json_response({"data": user_schema.dump(user)})


@api_bp.route("/users/<int:user_id>", methods=["DELETE"])
@require_manager
@limiter.limit(lambda: current_app.config["SENSITIVE_RATE_LIMIT"])
def delete_user(user_id: int) -> Response:
    """Delete a user."""

    delete_user_service(user_id)
    return json_response({"message": "User deleted."})


__all__ = [
    "create_user",
    "delete_user",
    "get_user",
    "list_users",
    "update_user",
]
