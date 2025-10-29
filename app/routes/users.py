"""User-related API routes."""

from __future__ import annotations

from flask import Response, request

from ..auth import require_auth, require_manager
from ..extensions import db
from ..models import User
from ..schemas import UserSchema
from . import api_bp
from .common import get_or_404, json_response

user_schema = UserSchema()
users_schema = UserSchema(many=True)


@api_bp.route("/users", methods=["POST"])
@require_manager
def create_user() -> Response:
    """Create a new user."""

    data = user_schema.load(request.get_json() or {})
    password = data.pop("password")

    user = User(**data)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return json_response({"data": user_schema.dump(user)}, 201)


@api_bp.route("/users", methods=["GET"])
@require_auth
def list_users() -> Response:
    """Return all users."""

    users = User.query.order_by(User.id).all()
    return json_response({"data": users_schema.dump(users)})


@api_bp.route("/users/<int:user_id>", methods=["GET"])
@require_auth
def get_user(user_id: int) -> Response:
    """Fetch a single user."""

    user = get_or_404(User, user_id)
    return json_response({"data": user_schema.dump(user)})


@api_bp.route("/users/<int:user_id>", methods=["PUT"])
@require_manager
def update_user(user_id: int) -> Response:
    """Update an existing user."""

    user = get_or_404(User, user_id)
    data = user_schema.load(request.get_json() or {}, partial=True)

    password = data.pop("password", None)
    for key, value in data.items():
        setattr(user, key, value)

    if password:
        user.set_password(password)

    db.session.commit()
    return json_response({"data": user_schema.dump(user)})


@api_bp.route("/users/<int:user_id>", methods=["DELETE"])
@require_manager
def delete_user(user_id: int) -> Response:
    """Delete a user."""

    user = get_or_404(User, user_id)
    db.session.delete(user)
    db.session.commit()
    return json_response({"message": "User deleted."})


__all__ = [
    "create_user",
    "list_users",
    "get_user",
    "update_user",
    "delete_user",
]
