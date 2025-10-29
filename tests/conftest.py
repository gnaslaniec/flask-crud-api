"""Shared pytest fixtures."""

from __future__ import annotations

import json
import os
import sys
from base64 import b64encode
from typing import Callable, Dict

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.config import TestingConfig
from app.extensions import db
from app.models import User


@pytest.fixture
def app():
    """Create a Flask app configured for testing."""

    app = create_app(TestingConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Return an HTTP client for the Flask app."""

    return app.test_client()


@pytest.fixture
def create_user_record(app) -> Callable[..., User]:
    """Factory for creating users directly in the database."""

    def _create_user(
        *,
        name: str,
        email: str,
        role: str,
        password: str = "Password123!",
    ) -> User:
        with app.app_context():
            user = User(name=name, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)
            db.session.expunge(user)
            return user

    return _create_user


@pytest.fixture
def manager_headers(client, create_user_record) -> Dict[str, str]:
    """Headers representing an authorised manager user."""

    password = "ManagerPass123!"
    user = create_user_record(
        name="Jane Manager",
        email="jane.manager@example.com",
        role="manager",
        password=password,
    )

    basic_token = b64encode(f"{user.email}:{password}".encode()).decode()
    response = client.post(
        "/auth/login",
        headers={"Authorization": f"Basic {basic_token}"},
    )
    assert response.status_code == 200, response.get_json()
    access_token = response.get_json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


@pytest.fixture
def employee_headers(client, create_user_record) -> Dict[str, str]:
    """Headers representing a non-privileged employee user."""

    password = "EmployeePass123!"
    user = create_user_record(
        name="Eddie Employee",
        email="eddie.employee@example.com",
        role="employee",
        password=password,
    )

    basic_token = b64encode(f"{user.email}:{password}".encode()).decode()
    response = client.post(
        "/auth/login",
        headers={"Authorization": f"Basic {basic_token}"},
    )
    assert response.status_code == 200, response.get_json()
    access_token = response.get_json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


@pytest.fixture
def json_dumps():
    """Simple wrapper around json.dumps for convenience."""

    return json.dumps
