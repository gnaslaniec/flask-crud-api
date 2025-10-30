"""User model definition."""

from __future__ import annotations

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import validates
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from .base import TimestampMixin


class User(TimestampMixin, db.Model):
    """Represents a platform user."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    created_projects = db.relationship(
        "Project",
        back_populates="created_by_user",
        lazy="selectin",
    )
    assigned_tasks = db.relationship(
        "Task",
        back_populates="assignee",
        lazy="selectin",
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

    def set_password(self, password: str) -> None:
        """Hash and store the user's password."""

        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a plaintext password against the stored hash."""

        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.id} {self.email}>"


__all__ = ["User"]
