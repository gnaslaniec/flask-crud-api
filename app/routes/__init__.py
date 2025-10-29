"""Blueprint assembly for API routes."""

from __future__ import annotations

from importlib import import_module

from flask import Blueprint

api_bp = Blueprint("api", __name__)


def _load_route_modules() -> None:
    """Import modules so their routes register with the blueprint."""

    for module in ("auth_routes", "projects", "tasks", "users"):
        import_module(f"{__name__}.{module}")


_load_route_modules()

__all__ = ["api_bp"]
