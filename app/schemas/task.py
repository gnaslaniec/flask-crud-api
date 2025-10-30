"""Schema for task resources."""

from marshmallow import fields, validate

from ..models import TaskStatus
from .base import BaseSchema


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


__all__ = ["TaskSchema"]
