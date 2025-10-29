"""Application factory and setup for the Flask API."""

from __future__ import annotations

from typing import Any, Dict, Optional, Type

from flask import Flask

from .config import Config
from .errors import register_error_handlers
from .extensions import db
from .routes import api_bp


def create_app(config_object: Optional[Type[Config] | Dict[str, Any]] = None) -> Flask:
    """Create a configured Flask application."""

    app = Flask(__name__)
    app.config.from_object(Config)

    if config_object:
        app.config.from_object(config_object)

    register_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_cli(app)

    return app


def register_extensions(app: Flask) -> None:
    """Attach extensions to the app."""

    db.init_app(app)


def register_blueprints(app: Flask) -> None:
    """Register application blueprints."""

    app.register_blueprint(api_bp)


def register_cli(app: Flask) -> None:
    """Set up helpful Flask CLI commands."""

    @app.cli.command("init-db")
    def init_db() -> None:  # pragma: no cover - CLI utility
        """Initialise the database tables."""

        db.create_all()

        from .models import User

        admin_exists = db.session.query(User.id).first() is not None
        if not admin_exists:
            admin = User(
                name=app.config["DEFAULT_ADMIN_NAME"],
                email=app.config["DEFAULT_ADMIN_EMAIL"],
                role="manager",
            )
            admin.set_password(app.config["DEFAULT_ADMIN_PASSWORD"])
            db.session.add(admin)
            db.session.commit()
            print(
                "Database initialised. "
                f"Default admin '{admin.email}' created with manager role."
            )
        else:
            print("Database initialised.")
