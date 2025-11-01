"""Schema for task resources."""

from __future__ import annotations

from datetime import date

from marshmallow import ValidationError, fields, validate, validates_schema, pre_load

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

    @pre_load
    def normalize_optional_fields(self, data, **kwargs):
        """Strip empty strings from optional fields."""

        if not isinstance(data, dict):
            return data

        if "due_date" in data:
            raw_due_date = data.get("due_date")
            if isinstance(raw_due_date, str):
                stripped = raw_due_date.strip()
                data["due_date"] = stripped or None
            elif raw_due_date is None:
                data["due_date"] = None

        if "assigned_to" in data:
            raw_assigned_to = data.get("assigned_to")
            if isinstance(raw_assigned_to, str):
                stripped = raw_assigned_to.strip()
                if not stripped:
                    data["assigned_to"] = None
                else:
                    try:
                        data["assigned_to"] = int(stripped)
                    except ValueError:
                        # Let schema validation surface a clean error for non-numeric values.
                        data["assigned_to"] = stripped
            elif raw_assigned_to is None:
                data["assigned_to"] = None

        return data

    @validates_schema
    def validate_due_date(self, data, **kwargs) -> None:
        """Prevent due dates from being set in the past."""

        due_date = data.get("due_date")
        if due_date and due_date < date.today():
            raise ValidationError(
                "Due date cannot be set in the past.",
                field_name="due_date",
            )


__all__ = ["TaskSchema"]
