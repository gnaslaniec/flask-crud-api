"""Business logic for task resources."""

from __future__ import annotations

from datetime import date
from typing import Dict, Tuple

from sqlalchemy.exc import NoResultFound

from ..errors import BusinessValidationError, NotFoundError
from ..extensions import db
from ..models import Task
from ..repositories import ProjectRepository, TaskRepository, UserRepository
from .validators import ensure_immutable_fields_not_modified

IMMUTABLE_FIELDS = {"id", "created_at", "updated_at", "project_id"}


def _ensure_due_date_is_valid(data: Dict) -> None:
    """Ensure provided due dates align with business rules."""

    due_date = data.get("due_date")
    if due_date and due_date < date.today():
        raise BusinessValidationError("Task due date cannot be in the past.")


def _ensure_assignee_exists(user_repo: UserRepository, assignee_id: int | None) -> None:
    """Ensure the referenced assignee exists when provided."""

    if assignee_id is None:
        return
    try:
        user_repo.get_by_id(assignee_id)
    except NoResultFound as exc:
        raise NotFoundError(f"User with ID {assignee_id} does not exist.") from exc


def create_task(project_id: int, data: Dict) -> Task:
    """Create a new task for a project."""

    project_repo = ProjectRepository(db.session)
    task_repo = TaskRepository(db.session)
    user_repo = UserRepository(db.session)

    try:
        project = project_repo.get_by_id(project_id)
    except NoResultFound as exc:
        raise NotFoundError(f"Project with ID {project_id} does not exist.") from exc

    _ensure_due_date_is_valid(data)
    _ensure_assignee_exists(user_repo, data.get("assigned_to"))

    payload = dict(data)
    payload["project_id"] = project.id

    return task_repo.create(payload)


def list_tasks(project_id: int, *, page: int, per_page: int) -> Tuple[list[Task], dict]:
    """List tasks for a project with pagination."""

    project_repo = ProjectRepository(db.session)
    task_repo = TaskRepository(db.session)

    try:
        project_repo.get_by_id(project_id)
    except NoResultFound as exc:
        raise NotFoundError(f"Project with ID {project_id} does not exist.") from exc

    items, meta = task_repo.list_by_project(project_id, page=page, per_page=per_page)
    return list(items), meta


def update_task(project_id: int, task_id: int, payload: Dict, data: Dict) -> Task:
    """Update an existing task ensuring it belongs to the project."""

    task_repo = TaskRepository(db.session)
    user_repo = UserRepository(db.session)

    try:
        task = task_repo.get_by_project_and_id(project_id, task_id)
    except NoResultFound as exc:
        raise NotFoundError(
            f"Task with ID {task_id} does not belong to project {project_id}."
        ) from exc

    ensure_immutable_fields_not_modified(payload, IMMUTABLE_FIELDS)

    _ensure_due_date_is_valid(data)
    _ensure_assignee_exists(user_repo, data.get("assigned_to"))

    return task_repo.update(task, data)


__all__ = ["create_task", "list_tasks", "update_task"]
