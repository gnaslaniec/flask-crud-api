"""Shared pytest fixtures."""

from __future__ import annotations

import json
import os
import sys
from typing import Dict

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.config import TestingConfig
from app.extensions import db


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
def manager_headers() -> Dict[str, str]:
    """Headers representing an authorised manager user."""

    return {"X-User-Role": "manager", "Content-Type": "application/json"}


@pytest.fixture
def employee_headers() -> Dict[str, str]:
    """Headers representing a non-privileged employee user."""

    return {"X-User-Role": "employee", "Content-Type": "application/json"}


@pytest.fixture
def json_dumps():
    """Simple wrapper around json.dumps for convenience."""

    return json.dumps
