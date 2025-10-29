# Design Rationale

## Architecture

- **Application Factory**: The Flask app is created via `create_app` (`app/__init__.py`), enabling configuration overrides for testing and future environments.
- **Extensions Module**: A single `SQLAlchemy` instance is initialised in `app/extensions.py` and imported wherever models need it, centralising ORM configuration.
- **Blueprint Routing**: HTTP routes are grouped into modules under `app/routes/`, all registering on a shared blueprint for clean separation by resource (auth, users, projects, tasks).

## Data Model Choices

- **Users** hold a `role` (`manager` or `employee`) enforced with both database constraints and Marshmallow validation.
- **Projects** optionally reference their creator (`created_by`) and cascade delete their nested tasks.
- **Tasks** belong to a project, expose a simple status lifecycle (`todo`, `in_progress`, `done`), and may optionally reference an assignee for future expansion.
- Timestamp fields on all models provide basic auditing with minimal overhead.

## Validation & Error Handling

- **Marshmallow Schemas** (`app/schemas.py`) guarantee consistent input validation and serialisation. Validation errors bubble through a blueprint error handler that returns structured JSON (`error`, `messages`).
- Database lookups use Flask-SQLAlchemy helpers (`get_or_404`) so HTTP 404s are raised uniformly when resources are missing.

## Authorisation Approach

- Manager-only write access drives the need for authentication. A dedicated login endpoint exchanges Basic credentials for short-lived JWTs, keeping the system stateless and compatible with HTTP clients.
- The `require_manager` decorator validates bearer tokens, retrieves the associated user, and enforces the manager role while exposing `g.current_user` to route handlers.

## Testing Strategy

- Pytest fixtures spin up an in-memory SQLite database (`TestingConfig`) for quick, isolated tests.
- Factory helpers in `tests/utils.py` reduce duplication across user, project, and task scenarios.
- Tests assert both successful CRUD flows and forbidden/edge cases to lock down the business rules (manager-only writes, missing user references).

## Documentation

- Routes include concise Sphinx docstrings to describe their behaviour, parameters, and response types. These are easy to ingest with Sphinx autodoc or similar tooling.
- The README captures setup instructions, API overview, and testing steps. This document captures the reasoning behind major architectural choices.
