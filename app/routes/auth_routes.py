"""Authentication endpoints."""

from __future__ import annotations

from flask import Response, jsonify, request

from ..auth import generate_access_token
from ..models import User
from . import api_bp
from .common import json_response


@api_bp.route("/auth/login", methods=["POST"])
def login() -> Response:
    """Authenticate a user via HTTP Basic auth and issue a JWT."""

    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return (
            jsonify({"error": "unauthorized", "message": "Credentials required."}),
            401,
            {"WWW-Authenticate": 'Basic realm="Login Required"'},
        )

    user = User.query.filter_by(email=auth.username).first()
    if user is None or not user.check_password(auth.password):
        return (
            jsonify({"error": "unauthorized", "message": "Invalid email or password."}),
            401,
            {"WWW-Authenticate": 'Basic realm="Login Required"'},
        )

    token = generate_access_token(user)
    return json_response({"access_token": token, "token_type": "Bearer"})


__all__ = ["login"]
