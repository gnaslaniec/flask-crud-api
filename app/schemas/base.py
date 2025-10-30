"""Common schema helpers."""

from marshmallow import EXCLUDE, Schema


class BaseSchema(Schema):
    """Common schema configuration."""

    class Meta:
        unknown = EXCLUDE


__all__ = ["BaseSchema"]
