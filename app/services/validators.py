"""Common validation helpers for service-layer logic."""

from __future__ import annotations

from typing import Iterable

from ..errors import BusinessValidationError


def ensure_immutable_fields_not_modified(payload: dict, immutable_fields: Iterable[str]) -> None:
    """Raise an error if payload attempts to mutate immutable attributes."""

    invalid = set(payload).intersection(set(immutable_fields))
    if invalid:
        raise BusinessValidationError(
            "Attempted to update immutable fields.",
            details={"fields": sorted(invalid)},
        )


__all__ = ["ensure_immutable_fields_not_modified"]
