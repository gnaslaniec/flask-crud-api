"""Application factory and setup for the Flask API."""

from __future__ import annotations

from typing import Any, Dict, Optional, Type

from flask import Flask
from flask.cli import with_appcontext

from .config import Config
from .errors import register_error_handlers
from .extensions import db, migrate
from .models import User
from .routes import api_bp


def create_app(config_object: Optional[Type[Config] | Dict[str, Any]] = None) -> Flask:
    """Create a configured Flask application."""

    app = Flask(__name__)
    app.config.from_object(Config)

    if config_object:
        app.config.from_object(config_object)

    app.config.setdefault("ENV", getattr(app, "env", "production"))
    app.logger.info(f"Starting Flask app [{app.config['ENV']}]")

    register_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_cli(app)

    return app


def register_extensions(app: Flask) -> None:
    """Attach extensions to the app."""

    db.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app: Flask) -> None:
    """Register application blueprints."""

    app.register_blueprint(api_bp)


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
