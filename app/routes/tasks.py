"""Task-related API routes."""

from __future__ import annotations

from flask import Response, current_app, request

from ..auth import require_auth, require_manager
from ..extensions import limiter
from ..schemas import TaskSchema
from ..services import (
    create_task as create_task_service,
    list_tasks as list_tasks_service,
    update_task as update_task_service,
)
from . import api_bp
from .common import get_pagination_params, json_response

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)


@api_bp.route("/projects/<int:project_id>/tasks", methods=["POST"])
@require_manager
@limiter.limit(lambda: current_app.config["SENSITIVE_RATE_LIMIT"])
def create_task(project_id: int) -> Response:
    """Create a task within a project."""

    payload = request.get_json() or {}
    data = task_schema.load(payload)
    task = create_task_service(project_id, data)
    return json_response({"data": task_schema.dump(task)}, 201)


@api_bp.route("/projects/<int:project_id>/tasks", methods=["GET"])
@require_auth
def list_tasks(project_id: int) -> Response:
    """List tasks for a project."""

    page, per_page = get_pagination_params()
    tasks, meta = list_tasks_service(project_id, page=page, per_page=per_page)
    return json_response({"data": tasks_schema.dump(tasks)}, meta=meta)


@api_bp.route("/projects/<int:project_id>/tasks/<int:task_id>", methods=["PUT"])
@require_manager
@limiter.limit(lambda: current_app.config["SENSITIVE_RATE_LIMIT"])
def update_task(project_id: int, task_id: int) -> Response:
    """Update an existing task within a project."""

    payload = request.get_json() or {}
    data = task_schema.load(payload, partial=True)
    task = update_task_service(project_id, task_id, payload, data)
    return json_response({"data": task_schema.dump(task)})


__all__ = ["create_task", "list_tasks", "update_task"]
