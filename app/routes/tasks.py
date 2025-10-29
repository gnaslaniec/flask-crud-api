"""Task-related API routes."""

from __future__ import annotations

from flask import Response, jsonify, request

from ..auth import require_auth, require_manager
from ..extensions import db
from ..models import Project, Task, User
from ..schemas import TaskSchema
from . import api_bp
from .common import get_or_404, json_response

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)


@api_bp.route("/projects/<int:project_id>/tasks", methods=["POST"])
@require_manager
def create_task(project_id: int) -> Response:
    """Create a task within a project."""

    project = get_or_404(Project, project_id)
    payload = request.get_json() or {}
    data = task_schema.load(payload)

    assignee_id = data.get("assigned_to")
    if assignee_id is not None and not db.session.get(User, assignee_id):
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"User with ID {assignee_id} does not exist.",
                }
            ),
            404,
        )

    task = Task(**data, project=project)
    db.session.add(task)
    db.session.commit()
    return json_response({"data": task_schema.dump(task)}, 201)


@api_bp.route("/projects/<int:project_id>/tasks", methods=["GET"])
@require_auth
def list_tasks(project_id: int) -> Response:
    """List tasks for a project."""

    project = get_or_404(Project, project_id)
    return json_response({"data": tasks_schema.dump(project.tasks)})


@api_bp.route("/projects/<int:project_id>/tasks/<int:task_id>", methods=["PUT"])
@require_manager
def update_task(project_id: int, task_id: int) -> Response:
    """Update an existing task within a project."""

    project = get_or_404(Project, project_id)
    task = get_or_404(Task, task_id)

    if task.project_id != project.id:
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"Task with ID {task_id} does not belong to project {project_id}.",
                }
            ),
            404,
        )

    payload = request.get_json() or {}
    data = task_schema.load(payload, partial=True)

    assignee_id = data.get("assigned_to")
    if assignee_id is not None and not db.session.get(User, assignee_id):
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"User with ID {assignee_id} does not exist.",
                }
            ),
            404,
        )

    for key, value in data.items():
        setattr(task, key, value)

    db.session.commit()
    return json_response({"data": task_schema.dump(task)})


__all__ = ["create_task", "list_tasks", "update_task"]
