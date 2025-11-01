"""Project repository implementation."""

from __future__ import annotations

from sqlalchemy import select

from ..models import Project
from .base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Persistence logic for Project entities."""

    model = Project
    default_ordering = (Project.id,)

    def list_by_creator(self, created_by: int, *, page: int, per_page: int):
        """Return projects filtered by creator."""

        stmt = (
            select(Project)
            .where(Project.created_by == created_by)
            .order_by(Project.id)
        )
        return self._paginate(stmt, page=page, per_page=per_page)


__all__ = ["ProjectRepository"]
