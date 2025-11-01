"""Authentication helpers and decorators."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import Callable, TypeVar, TypedDict, cast

import jwt
from flask import current_app, g, request
from jwt import ExpiredSignatureError, InvalidTokenError

from .errors import ForbiddenError, UnauthorizedError
from .extensions import db
from .models import User

F = TypeVar("F", bound=Callable[..., object])
MISSING_TOKEN_MSG = "Missing or invalid bearer token."


class JWTClaims(TypedDict):
    """Expected structure of access-token claims."""

    sub: str
    role: str
    iat: int
    exp: int


def _clear_current_user() -> None:
    """Remove any previously stored user from the request context."""

    g.pop("current_user", None)


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


def _authenticate_request(require_manager: bool = False) -> User:
    """Validate the bearer token on the current request."""

    _clear_current_user()

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise UnauthorizedError(MISSING_TOKEN_MSG)

    token = auth_header.split(None, 1)[1].strip()
    if not token:
        raise UnauthorizedError(MISSING_TOKEN_MSG)

    try:
        payload = decode_access_token(token)
    except ExpiredSignatureError as exc:  # pragma: no cover - relies on timing
        raise UnauthorizedError("Authentication token has expired.") from exc
    except InvalidTokenError as exc:
        raise UnauthorizedError("Invalid authentication token.") from exc

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError("Invalid authentication token.")

    user = db.session.get(User, int(user_id))
    if user is None:
        raise UnauthorizedError("User referenced by token no longer exists.")

    if require_manager and user.role != "manager":
        raise ForbiddenError("Manager role required for this operation.")

    g.current_user = user
    return user


def require_auth(func: F) -> F:
    """Ensure the request is authenticated."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        _authenticate_request(require_manager=False)
        return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


def require_manager(func: F) -> F:
    """Ensure the request is authenticated as a manager."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        _authenticate_request(require_manager=True)
        return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


__all__ = [
    "decode_access_token",
    "generate_access_token",
    "require_auth",
    "require_manager",
]
