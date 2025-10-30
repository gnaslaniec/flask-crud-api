"""Task model definition."""

from __future__ import annotations

from sqlalchemy.orm import validates

from ..extensions import db
from .base import TimestampMixin


class TaskStatus:
    """Supported task statuses."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELED = "canceled"

    ALL = (TODO, IN_PROGRESS, DONE, CANCELED)


class Task(TimestampMixin, db.Model):
    """Represents an actionable task within a project."""

    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.String(20),
        nullable=False,
        default=TaskStatus.TODO,
    )
    due_date = db.Column(db.Date, nullable=True)

    project_id = db.Column(
        db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True
    )
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    project = db.relationship(
        "Project",
        back_populates="tasks",
        lazy="joined",
    )
    assignee = db.relationship(
        "User",
        back_populates="assigned_tasks",
        lazy="joined",
    )

    @validates("status")
    def validate_status(self, key: str, value: str) -> str:
        """Ensure status is one of the supported values."""
        if value not in TaskStatus.ALL:
            raise ValueError("status must be one of 'todo', 'in_progress', 'done'")
        return value

    def __repr__(self) -> str:
        return f"<Task {self.id} {self.title}>"


__all__ = ["TaskStatus", "Task"]
