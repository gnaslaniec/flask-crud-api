"""Project-related API routes."""

from __future__ import annotations

from flask import Response, g, request

from ..auth import require_auth, require_manager
from ..extensions import db
from ..models import Project, User
from ..schemas import ProjectSchema
from . import api_bp
from .common import get_or_404, json_response

project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)


@api_bp.route("/projects", methods=["POST"])
@require_manager
def create_project() -> Response:
    """Create a new project."""

    data = project_schema.load(request.get_json() or {})
    data["created_by"] = g.current_user.id

    project = Project(**data)
    db.session.add(project)
    db.session.commit()
    return json_response({"data": project_schema.dump(project)}, 201)


@api_bp.route("/projects", methods=["GET"])
@require_auth
def list_projects() -> Response:
    """Return all projects."""

    projects = Project.query.order_by(Project.id).all()
    return json_response({"data": projects_schema.dump(projects)})


@api_bp.route("/projects/<int:project_id>", methods=["GET"])
@require_auth
def get_project(project_id: int) -> Response:
    """Fetch a single project."""

    project = get_or_404(Project, project_id)
    return json_response({"data": project_schema.dump(project)})


@api_bp.route("/projects/<int:project_id>", methods=["PUT"])
@require_manager
def update_project(project_id: int) -> Response:
    """Update an existing project."""

    project = get_or_404(Project, project_id)
    data = project_schema.load(request.get_json() or {}, partial=True)

    for key, value in data.items():
        setattr(project, key, value)

    db.session.commit()
    return json_response({"data": project_schema.dump(project)})


@api_bp.route("/projects/<int:project_id>", methods=["DELETE"])
@require_manager
def delete_project(project_id: int) -> Response:
    """Delete a project."""

    project = get_or_404(Project, project_id)
    db.session.delete(project)
    db.session.commit()
    return json_response({"message": "Project deleted."})


__all__ = [
    "create_project",
    "list_projects",
    "get_project",
    "update_project",
    "delete_project",
]
