# Flask Project Management API

This repository contains a complete Project Management REST API built with Flask, SQLAlchemy, Marshmallow and Alembic. It exposes CRUD endpoints for users, projects, and tasks, enforces simple role-based access control, and includes pytest-based unit tests and documentation.

## Features

- CRUD endpoints for users, projects, and nested project tasks
- JWT-backed authentication with manager-only write permissions
- SQLAlchemy data models with relationships and cascading deletes
- Database versioning and migrations via Flask-Migrate (Alembic)
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

Or use the bundled Makefile helpers:

```bash
make venv
source .venv/bin/activate
make install
```

### Database Setup

By default the app uses a SQLite database file `project_management.db` in the repository root. 

First, initialize the Alembic migration environment (this creates the migrations/ folder):

```bash
flask --app app:create_app db init
```

Or via Makefile:

```bash
make db-init
```

Then, generate and apply the initial migration to create the database schema:

```bash
flask db migrate -m "initial migration"
flask db upgrade
```

With Makefile equivalents:

```bash
make db-migrate m="initial migration"
make db-upgrade
```

This creates or updates all database tables in sync with your SQLAlchemy models.

If you need to reset or inspect migrations later, use:

```bash
flask db history
flask db downgrade
```

Makefile:

```bash
make db-downgrade
```

### Seeding a Default Admin User

After applying migrations, you can create a default manager user via the CLI:

```bash
flask init-admin
```

Or simply:

```bash
make init-admin
```

If no users exist yet, this command seeds a default manager using the credentials
configured via DEFAULT_ADMIN_EMAIL and DEFAULT_ADMIN_PASSWORD (defaults:
admin@admin.com / admin). Update those environment variables before
running the command if you want to set your own secure values.

You can then call /auth/login with those credentials to obtain a JWT token.

### Running the Server

```bash
flask --app run.py run
```

Or:

```bash
make run
```

The API will be available at `http://127.0.0.1:5000/`.

## API Usage

Authentication uses short-lived JWTs. Obtain a token via Basic authentication:

```bash
curl -X POST \
  -u manager@example.com:SuperSecret123 \
  http://127.0.0.1:5000/auth/login
```

The response contains an `access_token`. Include it in subsequent requests:

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

All endpoints require a valid bearer token. Any authenticated user can perform
read operations, while only managers can invoke mutating endpoints. Create users
by supplying a `password` field; passwords are stored as hashes and never
returned by the API.

Key endpoints:

| Resource  | Method & Path             | Description                    |
|-----------|---------------------------|--------------------------------|
| Auth      | `POST /auth/login`        | Exchange Basic credentials for a JWT |
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
|           | `PUT /projects/<id>/tasks/<task_id>` | Update a task (manager only) |

Projects automatically record the authenticated manager as their creator; any
payload `created_by` value is ignored. Deleting a project removes all of its
tasks thanks to cascading deletes.

Refer to in-code docstrings under `app/routes/` for detailed parameter and response information.

## Running Tests

```bash
pytest
```

Or:

```bash
make test
```

Coverage run:

```bash
make test-cov
```

The tests use an in-memory SQLite database and cover CRUD happy paths, authorisation failures, and validation edge cases.

## Documentation

Endpoints, parameters, and return types are described with Sphinx-style docstrings throughout the modules in `app/routes/`. Full HTML documentation can be generated with Sphinx:

```bash
pip install -r requirements.txt  # if not already installed
sphinx-build -b html docs docs/_build/html
```

Or streamline with:

```bash
make docs
```

Open `docs/_build/html/index.html` in your browser to explore the rendered docs.

## Postman Collection

A Postman collection (`docs/Project Management API.postman_collection.json`) is included for quickly exercising the API endpoints in a collaborative environment.

## Design Rationale

For deeper architectural context, see [`DESIGN_RATIONALE.md`](DESIGN_RATIONALE.md).
