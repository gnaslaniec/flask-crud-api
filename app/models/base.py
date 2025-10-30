"""Shared model utilities and mixins."""

from __future__ import annotations

from datetime import UTC, datetime

from ..extensions import db


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


__all__ = ["TimestampMixin"]
