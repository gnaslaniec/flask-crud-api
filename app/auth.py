"""Authentication helpers and decorators."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import Callable, Optional, Tuple, TypeVar, TypedDict, cast

import jwt
from flask import Response, current_app, g, jsonify, request
from jwt import ExpiredSignatureError, InvalidTokenError

from .extensions import db
from .models import User

F = TypeVar("F", bound=Callable[..., Response])
MISSING_TOKEN_MSG = "Missing or invalid bearer token."


class JWTClaims(TypedDict):
    """Expected structure of access-token claims."""

    sub: str
    role: str
    iat: int
    exp: int


def _unauthorized(message: str) -> Response:
    """Return a standardised 401 response."""

    return jsonify({"error": "unauthorized", "message": message}), 401


def _forbidden(message: str) -> Response:
    """Return a standardised 403 response."""

    return jsonify({"error": "forbidden", "message": message}), 403


def _clear_current_user() -> None:
    """Remove any previously stored user from the request context."""

    g.pop("current_user", None)


def _auth_failure(message: str) -> Tuple[None, Response]:
    """Return an auth failure response while clearing context."""

    _clear_current_user()
    return None, _unauthorized(message)


def _get_jwt_algorithm() -> str:
    """Return the configured JWT signing algorithm."""

    return current_app.config.get("JWT_ALGORITHM", "HS256")


def generate_access_token(user: User) -> str:
    """Generate a signed JWT for the given user."""

    now = datetime.now(UTC)
    expires_in = current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES", 3600)
    algorithm = _get_jwt_algorithm()

    payload: JWTClaims = {
        "sub": str(user.id),
        "role": user.role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in)).timestamp()),
    }
    secret_key = current_app.config["JWT_SECRET_KEY"]
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_access_token(token: str) -> JWTClaims:
    """Decode a JWT and return its payload."""

    secret_key = current_app.config["JWT_SECRET_KEY"]
    algorithm = _get_jwt_algorithm()
    decoded = jwt.decode(token, secret_key, algorithms=[algorithm])
    return cast(JWTClaims, decoded)


def _authenticate_request() -> Tuple[Optional[User], Optional[Response]]:
    """Validate the bearer token on the current request."""

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        return _auth_failure(MISSING_TOKEN_MSG)

    token = auth_header.split(None, 1)[1].strip()
    if not token:
        return _auth_failure(MISSING_TOKEN_MSG)

    try:
        payload = decode_access_token(token)
    except ExpiredSignatureError:
        return _auth_failure("Authentication token has expired.")
    except InvalidTokenError:
        return _auth_failure("Invalid authentication token.")

    user_id = payload.get("sub")
    if user_id is None:
        return _auth_failure("Invalid authentication token.")

    user = db.session.get(User, int(user_id))
    if user is None:
        return _auth_failure("User referenced by token no longer exists.")

    g.current_user = user
    return user, None


def require_auth(func: F) -> F:
    """Ensure the request is authenticated."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        _, error = _authenticate_request()
        if error:
            return error
        return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


def require_manager(func: F) -> F:
    """Ensure the request is authenticated as a manager."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        user, error = _authenticate_request()
        if error:
            return error

        if user.role != "manager":
            return _forbidden("Manager role required for this operation.")

        return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]
