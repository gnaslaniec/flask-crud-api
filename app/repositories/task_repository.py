"""Task repository implementation."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from ..models import Task
from .base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """Persistence logic for Task entities."""

    model = Task
    default_ordering = (Task.id,)

    def list_by_project(
        self, project_id: int, *, page: int, per_page: int
    ):
        """Return tasks for a project."""

        stmt = (
            select(Task)
            .where(Task.project_id == project_id)
            .order_by(Task.id)
        )
        return self._paginate(stmt, page=page, per_page=per_page)

    def get_by_project_and_id(self, project_id: int, task_id: int) -> Task:
        """Return a task ensuring it belongs to the given project."""

        stmt = select(Task).where(
            Task.id == task_id,
            Task.project_id == project_id,
        )
        task = self.session.execute(stmt).scalar_one_or_none()
        if task is None:
            raise NoResultFound(
                f"Task with id '{task_id}' not found for project '{project_id}'."
            )
        return task


__all__ = ["TaskRepository"]
