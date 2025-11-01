"""Project-related API routes."""

from __future__ import annotations

from flask import Response, current_app, request

from ..auth import require_auth, require_manager
from ..extensions import limiter
from ..schemas import ProjectSchema
from ..services import (
    create_project as create_project_service,
    delete_project as delete_project_service,
    get_project as get_project_service,
    list_projects as list_projects_service,
    update_project as update_project_service,
)
from . import api_bp
from .common import get_pagination_params, json_response

project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)


@api_bp.route("/projects", methods=["POST"])
@require_manager
@limiter.limit(lambda: current_app.config["SENSITIVE_RATE_LIMIT"])
def create_project() -> Response:
    """Create a new project."""

    data = project_schema.load(request.get_json() or {})
    project = create_project_service(data)
    return json_response({"data": project_schema.dump(project)}, 201)


@api_bp.route("/projects", methods=["GET"])
@require_auth
def list_projects() -> Response:
    """Return all projects with pagination."""

    page, per_page = get_pagination_params()
    projects, meta = list_projects_service(page=page, per_page=per_page)
    return json_response({"data": projects_schema.dump(projects)}, meta=meta)


@api_bp.route("/projects/<int:project_id>", methods=["GET"])
@require_auth
def get_project(project_id: int) -> Response:
    """Fetch a single project."""

    project = get_project_service(project_id)
    return json_response({"data": project_schema.dump(project)})


@api_bp.route("/projects/<int:project_id>", methods=["PUT"])
@require_manager
@limiter.limit(lambda: current_app.config["SENSITIVE_RATE_LIMIT"])
def update_project(project_id: int) -> Response:
    """Update an existing project."""

    payload = request.get_json() or {}
    data = project_schema.load(payload, partial=True)
    project = update_project_service(project_id, payload, data)
    return json_response({"data": project_schema.dump(project)})


@api_bp.route("/projects/<int:project_id>", methods=["DELETE"])
@require_manager
@limiter.limit(lambda: current_app.config["SENSITIVE_RATE_LIMIT"])
def delete_project(project_id: int) -> Response:
    """Delete a project."""

    delete_project_service(project_id)
    return json_response({"message": "Project deleted."})


__all__ = [
    "create_project",
    "delete_project",
    "get_project",
    "list_projects",
    "update_project",
]
