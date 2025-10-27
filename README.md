# Flask Project Management API

This repository contains a small but complete Project Management REST API built with Flask, SQLAlchemy, and Marshmallow. It exposes CRUD endpoints for users, projects, and tasks, enforces simple role-based access control, and includes pytest-based unit tests and documentation.

## Features

- CRUD endpoints for users, projects, and nested project tasks
- Role guard that requires managers (`X-User-Role: manager`) for all mutating operations
- SQLAlchemy data models with relationships and cascading deletes
- Input validation and structured JSON error responses
- Comprehensive pytest suite with reusable fixtures and factories
- Sphinx-style docstrings for automatic API documentation extraction

## Getting Started

### Prerequisites

- Python 3.11+
- A virtual environment is strongly recommended

### Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Database Setup

By default the app uses a SQLite database file `project_management.db` in the repository root. Initialise the schema once:

```bash
flask --app run.py init-db
```

You can point to a different database by setting `DATABASE_URL`.

### Running the Server

```bash
flask --app run.py run
```

The API will be available at `http://127.0.0.1:5000/`.

## API Usage

Role-based access is enforced through the `X-User-Role` header:

- Use `X-User-Role: manager` for create/update/delete requests.
- Omit the header or set `X-User-Role: employee` for read-only access.

Key endpoints:

| Resource  | Method & Path             | Description                    |
|-----------|---------------------------|--------------------------------|
| Users     | `POST /users`             | Create a user (manager only)   |
|           | `GET /users`              | List users                     |
|           | `GET /users/<id>`         | Retrieve a user                |
|           | `PUT /users/<id>`         | Update a user (manager only)   |
|           | `DELETE /users/<id>`      | Delete a user (manager only)   |
| Projects  | `POST /projects`          | Create a project (manager only)|
|           | `GET /projects`           | List projects                  |
|           | `GET /projects/<id>`      | Retrieve a project             |
|           | `PUT /projects/<id>`      | Update a project (manager only)|
|           | `DELETE /projects/<id>`   | Delete a project (manager only)|
| Tasks     | `POST /projects/<id>/tasks` | Create a task (manager only) |
|           | `GET /projects/<id>/tasks`  | List project tasks            |

Refer to in-code docstrings (`app/routes.py`) for detailed parameter and response information.

## Running Tests

```bash
pytest
```

The tests use an in-memory SQLite database and cover CRUD happy paths, authorisation failures, and validation edge cases.

## Repository Layout

```
app/
  __init__.py        # App factory, error handlers, CLI hooks
  config.py          # Runtime configuration classes
  extensions.py      # SQLAlchemy instance
  models.py          # ORM models and relationships
  routes.py          # Flask routes and business logic
  schemas.py         # Marshmallow schemas for validation/serialisation
tests/
  conftest.py        # Pytest fixtures
  test_users.py      # User endpoint tests
  test_projects.py   # Project endpoint tests
  test_tasks.py      # Task endpoint tests
  utils.py           # Shared API factory helpers
run.py               # Flask entrypoint
requirements.txt     # Python dependencies
README.md            # This file
DESIGN_RATIONALE.md  # Architectural decisions
```

## Documentation

Endpoints, parameters, and return types are described with Sphinx-style docstrings throughout `app/routes.py`. Full HTML documentation can be generated with Sphinx:

```bash
pip install -r requirements.txt  # if not already installed
sphinx-build -b html docs docs/_build/html
```

Open `docs/_build/html/index.html` in your browser to explore the rendered docs.

## Postman Collection (Optional)

A Postman collection (`docs/postman_collection.json`) is included for quickly exercising the API endpoints in a collaborative environment.
