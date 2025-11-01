"""Repository layer behaviour tests."""

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy.exc import NoResultFound

from app.extensions import db
from app.repositories import UserRepository
from app.services import create_user as create_user_service, list_users as list_users_service


def test_user_repository_crud_cycle(app):
    """UserRepository supports full CRUD operations."""

    repo = UserRepository(db.session)
    unique_email = f"repo-{uuid4().hex}@example.com"

    created = repo.create(
        {
            "name": "Repo User",
            "email": unique_email,
            "role": "employee",
            "password_hash": "hashed-password",
        }
    )

    fetched = repo.get_by_id(created.id)
    assert fetched.email == unique_email

    items, meta = repo.list(page=1, per_page=10)
    assert any(user.id == created.id for user in items)
    assert meta["total"] >= 1

    updated = repo.update(fetched, {"name": "Updated Repo User"})
    assert updated.name == "Updated Repo User"

    repo.delete(updated.id)

    with pytest.raises(NoResultFound):
        repo.get_by_id(updated.id)


def test_user_service_integration_uses_repository(app):
    """Service layer creates and lists users via repositories."""

    payload = {
        "name": "Service User",
        "email": f"service-{uuid4().hex}@example.com",
        "role": "manager",
        "password": "ServicePass123!",
    }

    created = create_user_service(payload.copy())
    assert created.id is not None
    assert created.check_password(payload["password"])

    users, meta = list_users_service(page=1, per_page=5)
    assert any(user.id == created.id for user in users)
    assert meta["total"] >= 1
