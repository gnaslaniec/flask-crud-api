"""Project model definition."""

from __future__ import annotations

from ..extensions import db
from .base import TimestampMixin


class Project(TimestampMixin, db.Model):
    """Represents a project that groups related tasks."""

    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    created_by_user = db.relationship(
        "User",
        back_populates="created_projects",
        lazy="joined",
    )
    tasks = db.relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Project {self.id} {self.name}>"


__all__ = ["Project"]
