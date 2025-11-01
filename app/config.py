"""Configuration for different application environments."""

from __future__ import annotations

import os
import secrets
from pathlib import Path


class Config:
    """Base configuration shared by all environments."""

    ENV = os.getenv("FLASK_ENV", os.getenv("APP_ENV", "production"))
    DEBUG = False

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{Path(os.getenv('FLASK_APP_DB', 'project_management.db')).resolve()}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600"))
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@admin.com")
    DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin")
    DEFAULT_ADMIN_NAME = os.getenv("DEFAULT_ADMIN_NAME", "Administrator")
    CORS_ALLOWED_ORIGINS = tuple(
        origin.strip()
        for origin in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(
            ","
        )
        if origin.strip()
    )
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "200 per day;50 per hour")
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_STRATEGY = os.getenv("RATELIMIT_STRATEGY", "fixed-window")
    LOGIN_RATE_LIMIT = os.getenv("LOGIN_RATE_LIMIT", "5 per minute")
    SENSITIVE_RATE_LIMIT = os.getenv("SENSITIVE_RATE_LIMIT", "20 per minute")
    PAGINATION_DEFAULT_PAGE = int(os.getenv("PAGINATION_DEFAULT_PAGE", "1"))
    PAGINATION_DEFAULT_PAGE_SIZE = int(os.getenv("PAGINATION_DEFAULT_PAGE_SIZE", "20"))
    PAGINATION_MAX_PAGE_SIZE = int(os.getenv("PAGINATION_MAX_PAGE_SIZE", "100"))
    PASSWORD_COMPLEXITY_REGEX = os.getenv(
        "PASSWORD_COMPLEXITY_REGEX",
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{12,}$",
    )

    @staticmethod
    def generate_ephemeral_secret() -> str:
        """Generate a short-lived secret key for non-production environments."""

        return secrets.token_urlsafe(32)


class DevelopmentConfig(Config):
    """Development configuration."""

    ENV = "development"
    DEBUG = True
    SECRET_KEY = os.getenv("SECRET_KEY") or Config.generate_ephemeral_secret()
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or SECRET_KEY


class TestingConfig(Config):
    """Configuration used by pytest."""

    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SECRET_KEY = "test-secret-key"
    JWT_SECRET_KEY = "test-jwt-secret-key"
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URI = "memory://"
    LOGIN_RATE_LIMIT = "3 per minute"
    SENSITIVE_RATE_LIMIT = "10 per minute"
