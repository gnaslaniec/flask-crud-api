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
    SECRET_KEY = os.getenv("SECRET_KEY", "development-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600"))
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@admin.com")
    DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin")
    DEFAULT_ADMIN_NAME = os.getenv("DEFAULT_ADMIN_NAME", "Administrator")


class TestingConfig(Config):
    """Configuration used by pytest."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
