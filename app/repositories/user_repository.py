"""User repository implementation."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from ..models import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Persistence logic for User entities."""

    model = User
    default_ordering = (User.id,)

    def get_by_email(self, email: str) -> User:
        """Return a user matching the supplied email address."""

        stmt = select(User).where(User.email == email)
        user = self.session.execute(stmt).scalar_one_or_none()
        if user is None:
            raise NoResultFound(f"User with email '{email}' was not found.")
        return user


__all__ = ["UserRepository"]
