"""Authentication service functions."""

from __future__ import annotations

from typing import Optional

from flask import Request, request
from sqlalchemy.exc import NoResultFound

from ..errors import UnauthorizedError
from ..auth import generate_access_token
from ..extensions import db
from ..repositories import UserRepository


def _get_authorization(request_obj: Optional[Request] = None):
    """Return the HTTP basic auth payload from the request."""

    req = request_obj or request
    return req.authorization


def authenticate_user_and_issue_token() -> str:
    """Validate HTTP basic credentials and issue an access token."""

    auth = _get_authorization()
    if not auth or not auth.username or not auth.password:
        raise UnauthorizedError("Credentials required.")

    repo = UserRepository(db.session)
    try:
        user = repo.get_by_email(auth.username)
    except NoResultFound as exc:
        raise UnauthorizedError("Invalid email or password.") from exc

    if not user.check_password(auth.password):
        raise UnauthorizedError("Invalid email or password.")

    return generate_access_token(user)


__all__ = ["authenticate_user_and_issue_token"]
