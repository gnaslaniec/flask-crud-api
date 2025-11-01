"""Business logic for project resources."""

from __future__ import annotations

from typing import Dict, Tuple

from flask import g
from sqlalchemy.exc import NoResultFound

from ..errors import BusinessValidationError, NotFoundError
from ..extensions import db
from ..models import Project
from ..repositories import ProjectRepository
from .validators import ensure_immutable_fields_not_modified


IMMUTABLE_FIELDS = {"id", "created_at", "updated_at", "created_by"}


def create_project(data: Dict) -> Project:
    """Create a new project owned by the current user."""

    current_user = getattr(g, "current_user", None)
    if current_user is None:
        raise BusinessValidationError("Authenticated user is required to create projects.")

    repo = ProjectRepository(db.session)
    payload = dict(data)
    payload["created_by"] = current_user.id
    return repo.create(payload)


def list_projects(*, page: int, per_page: int) -> Tuple[list[Project], dict]:
    """Return a paginated list of projects."""

    repo = ProjectRepository(db.session)
    items, meta = repo.list(page=page, per_page=per_page)
    return list(items), meta


def get_project(project_id: int) -> Project:
    """Fetch a project or raise a 404 error."""

    repo = ProjectRepository(db.session)
    try:
        return repo.get_by_id(project_id)
    except NoResultFound as exc:
        raise NotFoundError("Project not found.") from exc


def update_project(project_id: int, payload: Dict, data: Dict) -> Project:
    """Update mutable project fields."""

    repo = ProjectRepository(db.session)
    try:
        project = repo.get_by_id(project_id)
    except NoResultFound as exc:
        raise NotFoundError("Project not found.") from exc

    ensure_immutable_fields_not_modified(payload, IMMUTABLE_FIELDS)

    return repo.update(project, data)


def delete_project(project_id: int) -> None:
    """Remove a project and cascade related tasks."""

    repo = ProjectRepository(db.session)
    try:
        repo.delete(project_id)
    except NoResultFound as exc:
        raise NotFoundError("Project not found.") from exc


__all__ = [
    "create_project",
    "delete_project",
    "get_project",
    "list_projects",
    "update_project",
]
