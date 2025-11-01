"""Authentication endpoints."""

from __future__ import annotations

from flask import Response, current_app, request

from ..extensions import limiter
from ..errors import ForbiddenError
from ..services import authenticate_user_and_issue_token
from . import api_bp
from .common import json_response


def _is_origin_allowed() -> bool:
    """Check whether the request Origin header is in the allowed CORS list."""

    origin = request.headers.get("Origin")
    if not origin:
        return True

    allowed = current_app.config.get("CORS_ALLOWED_ORIGINS") or ()
    if "*" in allowed:
        return True
    return origin in allowed


@api_bp.route("/auth/login", methods=["POST", "OPTIONS"])
@limiter.limit(lambda: current_app.config["LOGIN_RATE_LIMIT"], methods=["POST"])
def login() -> Response:
    """Authenticate a user via HTTP Basic auth and issue a JWT."""

    if not _is_origin_allowed():
        raise ForbiddenError("Origin not allowed.")

    if request.method == "OPTIONS":
        response = current_app.make_default_options_response()
        return response

    token = authenticate_user_and_issue_token()
    return json_response({"access_token": token, "token_type": "Bearer"})


__all__ = ["login"]
