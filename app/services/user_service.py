"""Business logic for user resources."""

from __future__ import annotations

from typing import Dict, Tuple

from sqlalchemy.exc import NoResultFound

from ..errors import BusinessValidationError, NotFoundError
from ..extensions import db
from ..models import User
from ..repositories import UserRepository
from .validators import ensure_immutable_fields_not_modified

IMMUTABLE_FIELDS = {"id", "created_at", "updated_at"}


def create_user(data: Dict) -> User:
    """Create a new user and hash their password."""

    password = data.pop("password", None)
    if not password:
        raise BusinessValidationError("Password is required.")

    user = User(**data)
    user.set_password(password)

    repo = UserRepository(db.session)
    return repo.create(user)


def list_users(*, page: int, per_page: int) -> Tuple[list[User], dict]:
    """Return a paginated list of users."""

    repo = UserRepository(db.session)
    items, meta = repo.list(page=page, per_page=per_page)
    return list(items), meta


def get_user(user_id: int) -> User:
    """Fetch a user or raise a 404 error."""

    repo = UserRepository(db.session)
    try:
        return repo.get_by_id(user_id)
    except NoResultFound as exc:
        raise NotFoundError("User not found.") from exc


def update_user(user_id: int, payload: Dict, data: Dict) -> User:
    """Update mutable user fields."""

    repo = UserRepository(db.session)
    try:
        user = repo.get_by_id(user_id)
    except NoResultFound as exc:
        raise NotFoundError("User not found.") from exc

    ensure_immutable_fields_not_modified(payload, IMMUTABLE_FIELDS)

    password = data.pop("password", None)
    if password:
        user.set_password(password)

    return repo.update(user, data)


def delete_user(user_id: int) -> None:
    """Delete a user."""

    repo = UserRepository(db.session)
    try:
        repo.delete(user_id)
    except NoResultFound as exc:
        raise NotFoundError("User not found.") from exc


__all__ = [
    "create_user",
    "delete_user",
    "get_user",
    "list_users",
    "update_user",
]
