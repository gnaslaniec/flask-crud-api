"""Schema for project resources."""

from marshmallow import fields, validate

from .base import BaseSchema


class ProjectSchema(BaseSchema):
    """Serialises Project objects."""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    description = fields.Str(allow_none=True)
    created_by = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


__all__ = ["ProjectSchema"]
