"""Schema for user resources."""

from marshmallow import fields, validate

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
        validate=validate.Length(min=8, max=128),
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


__all__ = ["UserSchema"]
