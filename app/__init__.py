"""Application factory and setup for the Flask API."""

from __future__ import annotations

from typing import Any, Dict, Optional, Type

from flask import Flask, Response, jsonify

from .config import Config
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


def register_error_handlers(app: Flask) -> None:
    """Configure JSON error responses."""

    @app.errorhandler(404)
    def handle_not_found(error) -> Response:  # pragma: no cover - simple handler
        return jsonify({"error": "not_found", "message": "Resource not found."}), 404

    @app.errorhandler(400)
    def handle_bad_request(error) -> Response:  # pragma: no cover - simple handler
        return jsonify({"error": "bad_request", "message": "Bad request."}), 400


def register_cli(app: Flask) -> None:
    """Set up helpful Flask CLI commands."""

    @app.cli.command("init-db")
    def init_db() -> None:  # pragma: no cover - CLI utility
        """Initialise the database tables."""

        db.create_all()
        print("Database initialised.")
