"""Shared SQLAlchemy repository abstractions."""

from __future__ import annotations

import math
from typing import Any, Dict, Generic, Iterable, Tuple, Type, TypeVar, Union

from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    """Generic repository implementing common CRUD operations."""

    model: Type[ModelT]
    default_ordering: Iterable[Any] | None = None

    def __init__(self, session: Session) -> None:
        self.session = session
        if not hasattr(self, "model"):
            raise ValueError("Repository subclasses must define a 'model' attribute.")

    def get_by_id(self, entity_id: int) -> ModelT:
        """Return an entity by its primary key."""

        entity = self.session.get(self.model, entity_id)
        if entity is None:
            raise NoResultFound(
                f"{self.model.__name__} with id '{entity_id}' was not found."
            )
        return entity

    def list(self, *, page: int = 1, per_page: int = 20) -> Tuple[list[ModelT], dict]:
        """Return a paginated list of entities."""

        stmt = select(self.model)
        ordering = tuple(self.default_ordering or self._derive_ordering())
        if ordering:
            stmt = stmt.order_by(*ordering)
        return self._paginate(stmt, page=page, per_page=per_page)

    def create(self, data: Union[Dict[str, Any], ModelT]) -> ModelT:
        """Create and persist a new entity."""

        entity = self._coerce_entity(data)
        self.session.add(entity)
        self._commit()
        return entity

    def update(self, entity: ModelT, data: Dict[str, Any]) -> ModelT:
        """Update an entity with the supplied attributes."""

        for key, value in data.items():
            setattr(entity, key, value)
        self._commit()
        return entity

    def delete(self, entity_id: int) -> None:
        """Delete an entity by id."""

        entity = self.get_by_id(entity_id)
        self.session.delete(entity)
        self._commit()

    def _coerce_entity(self, data: Union[Dict[str, Any], ModelT]) -> ModelT:
        """Normalise payloads passed to create()."""

        if isinstance(data, self.model):
            return data
        return self.model(**data)  # type: ignore[arg-type]

    def _paginate(
        self, stmt: Select, *, page: int, per_page: int
    ) -> Tuple[list[ModelT], dict]:
        """Execute a select statement with pagination metadata."""

        count_subquery = stmt.order_by(None).subquery()
        total_stmt = select(func.count()).select_from(count_subquery)
        total = self.session.execute(total_stmt).scalar_one()
        offset = (page - 1) * per_page

        items = (
            self.session.execute(stmt.limit(per_page).offset(offset)).scalars().all()
        )

        pages = math.ceil(total / per_page) if per_page else 0
        meta = {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1 and total > 0,
        }
        return list(items), meta

    def _derive_ordering(self) -> Tuple[Any, ...]:
        """Attempt to derive a sensible default ordering for list()."""

        identifier = getattr(self.model, "id", None)
        if identifier is not None:
            return (identifier,)
        return tuple()

    def _commit(self) -> None:
        """Commit the current transaction handling rollback on failure."""

        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        except SQLAlchemyError:
            self.session.rollback()
            raise


__all__ = ["BaseRepository"]
