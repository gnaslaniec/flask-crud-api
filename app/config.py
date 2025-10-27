"""Configuration for different application environments."""

from __future__ import annotations

import os
from pathlib import Path


class Config:
    """Base configuration shared by all environments."""

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{Path(os.getenv('FLASK_APP_DB', 'project_management.db')).resolve()}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False


class TestingConfig(Config):
    """Configuration used by pytest."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
