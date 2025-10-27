"""Database models for the project management system."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import validates

from .extensions import db


def _utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(UTC)


class TimestampMixin:
    """Mixin that adds created/updated timestamps."""

    created_at = db.Column(db.DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
        nullable=False,
    )


class User(TimestampMixin, db.Model):
    """Represents a platform user."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)

    created_projects = db.relationship(
        "Project",
        back_populates="created_by_user",
        lazy="select",
    )
    assigned_tasks = db.relationship(
        "Task",
        back_populates="assignee",
        lazy="select",
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('manager', 'employee')",
            name="ck_users_role_valid",
        ),
    )

    @validates("role")
    def validate_role(self, key: str, value: str) -> str:
        """Ensure role is one of the supported values."""
        if value not in {"manager", "employee"}:
            raise ValueError("role must be either 'manager' or 'employee'")
        return value

    def __repr__(self) -> str:
        return f"<User {self.id} {self.email}>"


class Project(TimestampMixin, db.Model):
    """Represents a project that groups related tasks."""

    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
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


class TaskStatus:
    """Supported task statuses."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

    ALL = (TODO, IN_PROGRESS, DONE)


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

    __table_args__ = (
        CheckConstraint(
            "status IN ('todo', 'in_progress', 'done')",
            name="ck_tasks_status_valid",
        ),
    )

    @validates("status")
    def validate_status(self, key: str, value: str) -> str:
        """Ensure status is one of the supported values."""
        if value not in TaskStatus.ALL:
            raise ValueError("status must be one of 'todo', 'in_progress', 'done'")
        return value

    def __repr__(self) -> str:
        return f"<Task {self.id} {self.title}>"
