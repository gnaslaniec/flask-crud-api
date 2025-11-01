# Design Rationale

## Architecture

- **Application factory** keeps the Flask setup flexible for tests and future environments.
- **Extensions module** holds shared SQLAlchemy and Flask-Migrate instances so ORM setup lives in one place.
- **Environment loader** (`python-dotenv`) pulls secrets, pagination defaults, and rate limits from `.env` at startup instead of hard-coding them.
- **Blueprint routing** groups routes by feature area (auth, users, projects, tasks) while still registering on one blueprint.
- **CLI commands** expose migrations and the `init-admin` seeder so setup stays one command away.
- **Static frontend** lives beside the API in `frontend/` and talks to the same endpoints via HTMX, giving teams a lightweight UI without bundlers.

## Data Model Choices

- **Users** store a role (`manager` or `employee`) enforced by both the database and Marshmallow.
- **Projects** record who created them and cascade-delete their tasks; busy columns like `name` are indexed.
- **Tasks** belong to projects, track a simple status enum, and optionally reference an assignee.
- Each model keeps `created_at`/`updated_at` timestamps for cheap auditing.

## Validation & Error Handling

- **Marshmallow schemas** filter input and return consistent JSON errors.
- Pagination parsing rejects non-integers and `per_page` values out of range with a clear error message.
- Lookups rely on `get_or_404` to keep missing-resource handling consistent.

## Authorization

- Managers get write access; everyone else reads. Login uses Basic auth to issue short-lived JWTs.
- A `require_manager` decorator checks the token and role, then stores the user on `g`.
- Passwords must pass a regex that enforces strong credentials before saving.

## Testing

- Pytest runs against an in-memory SQLite database for quick feedback.
- Shared factory helpers build users, projects, and tasks in tests without duplication.
- Suites cover happy paths, permission failures, CLI commands, and pagination edge cases.

## Documentation

- Routes carry Sphinx-ready docstrings for parameters and responses.
- The README walks through environment setup, API usage, and testing; this rationale explains the decisions behind them.

## Cross-Cutting Concerns

- **Pagination**: One helper standardises query params, enforces limits, and returns `page`, `per_page`, and `total` in every list response.
- **Rate limiting**: Flask-Limiter protects login and manager endpoints with configs pulled from the environment.
- **CORS**: Flask-CORS only allows origins listed in configuration, keeping integrations predictable.
- **Configuration**: Keys like JWT secrets, password rules, and pagination sizes live in environment variables so each environment can tune them safely.
- **Frontend integration**: The static site reads an overridable `pm_api_base` from `localStorage`, so it can be pointed at different API deployments without rebuilds.
