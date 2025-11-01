"""Application factory and setup for the Flask API."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Type

from flask import Flask
from flask.cli import with_appcontext
from dotenv import load_dotenv

from .config import Config
from .errors import register_error_handlers
from .extensions import cors, db, limiter, migrate
from .models import User
from .routes import api_bp


def _merge_config(app: Flask, config_object: Optional[Type[Config] | Dict[str, Any]]) -> None:
    """Merge dynamic configuration into the app config."""

    if not config_object:
        return

    if isinstance(config_object, dict):
        app.config.update(config_object)
        return

    app.config.from_object(config_object)


def create_app(config_object: Optional[Type[Config] | Dict[str, Any]] = None) -> Flask:
    """Create a configured Flask application."""

    _load_env_file()
    app = Flask(__name__)
    app.config.from_object(Config)

    _merge_config(app, config_object)

    app.config.setdefault("ENV", getattr(app, "env", "production"))
    app.logger.info(f"Starting Flask app [{app.config['ENV']}]")

    _ensure_secrets(app)
    register_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_cli(app)

    return app


def register_extensions(app: Flask) -> None:
    """Attach extensions to the app."""

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(
        app,
        resources={r"/*": {"origins": app.config["CORS_ALLOWED_ORIGINS"]}},
        supports_credentials=True,
    )

    if app.config.get("RATELIMIT_ENABLED", True):
        limiter.init_app(app)
        default_limit = app.config.get("RATELIMIT_DEFAULT")
        if default_limit:
            limiter.default_limits = [default_limit]
    else:
        app.logger.info("Rate limiting disabled for this configuration.")

    if not app.config.get("JWT_SECRET_KEY"):
        app.config["JWT_SECRET_KEY"] = app.config["SECRET_KEY"]


def register_blueprints(app: Flask) -> None:
    """Register application blueprints."""

    app.register_blueprint(api_bp)


def _load_env_file() -> None:
    """Load environment variables from the project .env if present."""

    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env", override=False)


def _ensure_secrets(app: Flask) -> None:
    """Validate that required secret keys are present."""

    if not app.config.get("SECRET_KEY"):
        if app.config.get("ENV") == "production":
            raise RuntimeError("SECRET_KEY environment variable must be set in production.")
        generated = Config.generate_ephemeral_secret()
        app.logger.warning("SECRET_KEY not provided; generating ephemeral key for non-production use.")
        app.config["SECRET_KEY"] = generated

    if not app.config.get("JWT_SECRET_KEY"):
        app.config["JWT_SECRET_KEY"] = app.config["SECRET_KEY"]


def register_cli(app: Flask) -> None:
    """Register custom Flask CLI commands."""

    @app.cli.command("init-admin")
    @with_appcontext
    def init_admin() -> None:  # pragma: no cover - CLI utility
        """Ensure a default admin user exists."""

        admin_exists = db.session.query(User.id).first() is not None
        if admin_exists:
            print("Default admin already exists.")
            return

        admin = User(
            name=app.config["DEFAULT_ADMIN_NAME"],
            email=app.config["DEFAULT_ADMIN_EMAIL"],
            role="manager",
        )
        admin.set_password(app.config["DEFAULT_ADMIN_PASSWORD"])
        db.session.add(admin)
        db.session.commit()

        print(
            f"Default admin '{admin.email}' created successfully with password from configuration."
        )
