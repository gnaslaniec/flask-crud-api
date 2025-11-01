"""Schema for user resources."""

from __future__ import annotations

import re

from flask import current_app
from marshmallow import ValidationError, fields, validate, validates_schema

from .base import BaseSchema


class UserSchema(BaseSchema):
    """Serialises User objects."""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    email = fields.Email(required=True)
    role = fields.Str(
        required=True,
        validate=validate.OneOf(["manager", "employee"]),
    )
    password = fields.Str(
        load_only=True,
        required=True,
        validate=validate.Length(min=12, max=128),
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates_schema
    def validate_password_complexity(self, data, **kwargs) -> None:
        """Enforce password complexity rules defined in configuration."""

        password = data.get("password")
        if password is None:
            return

        pattern = current_app.config["PASSWORD_COMPLEXITY_REGEX"]
        if not re.fullmatch(pattern, password):
            raise ValidationError(
                "Password must be at least 12 characters and include uppercase, "
                "lowercase, numeric, and special characters.",
                field_name="password",
            )


__all__ = ["UserSchema"]
