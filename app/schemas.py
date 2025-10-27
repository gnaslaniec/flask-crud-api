"""Input and output schemas for serialising API payloads."""

from __future__ import annotations

from marshmallow import EXCLUDE, Schema, ValidationError, fields, validate

from .models import TaskStatus


class BaseSchema(Schema):
    """Common schema configuration."""

    class Meta:
        unknown = EXCLUDE


class UserSchema(BaseSchema):
    """Serialises User objects."""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    email = fields.Email(required=True)
    role = fields.Str(
        required=True,
        validate=validate.OneOf(["manager", "employee"]),
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ProjectSchema(BaseSchema):
    """Serialises Project objects."""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    description = fields.Str(allow_none=True)
    created_by = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class TaskSchema(BaseSchema):
    """Serialises Task objects."""

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    description = fields.Str(allow_none=True)
    status = fields.Str(
        load_default=TaskStatus.TODO,
        validate=validate.OneOf(TaskStatus.ALL),
    )
    due_date = fields.Date(allow_none=True)
    project_id = fields.Int(dump_only=True)
    assigned_to = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
