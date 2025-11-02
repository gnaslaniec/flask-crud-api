Usage Guide
===========

Quick Overview
--------------

The Project Management API is a Flask application that exposes CRUD endpoints
for users, projects, and tasks. Recent iterations introduced a repository +
service architecture, rate limiting, pagination metadata, CORS enforcement, and
password complexity requirements. Write operations require a manager-
authenticated JSON Web Token (JWT), while read operations are open to all
roles.

Running the Server
------------------

1. Create and activate a virtual environment.
2. Install dependencies (runtime now includes "Flask-Limiter" and
   "Flask-Cors") ::

      pip install -r requirements.txt

   Or use the Makefile helper ::

      make install

3. Set up the database schema using Flask-Migrate. On a brand-new checkout
   initialise the Alembic environment ::

      flask --app app:create_app db init

   Equivalent Makefile target ::

      make db-init

   Generate and apply the initial migration ::

      flask db migrate -m "initial migration"
      flask db upgrade

   Or ::

      make db-migrate m="initial migration"
      make db-upgrade

4. Copy ``.env.example`` to ``.env`` and customise as needed. The application
   automatically loads this file through ``python-dotenv`` on startup.

5. Seed the default administrator account ::

      flask --app app:create_app init-admin

   Or simply ::

      make init-admin

6. Start the development server ::

      flask --app run.py run

   Makefile alternative ::

      make run

Running the Frontend
--------------------

The repository bundles a static HTMX-powered frontend inside the ``frontend/``
directory. Serve it with your favourite static file server; Python's standard
library works well for a quick local setup ::

   python -m http.server 3000 --directory frontend

If you prefer the Makefile helper ::

   make frontend [FRONTEND_PORT=3000]

When the page loads it calls the API at ``http://localhost:5000``. To point the
UI to another deployment, set ``pm_api_base`` in your browser console and
refresh ::

   localStorage.setItem('pm_api_base', 'http://localhost:8000');

Authentication & Authorisation
------------------------------

The ``init-admin`` command seeds a default manager account when no users exist.
Credentials come from ``DEFAULT_ADMIN_EMAIL`` and ``DEFAULT_ADMIN_PASSWORD``
configuration values (defaults: ``admin@admin.com`` / ``admin``). Adjust these
environment variables before executing the command if you want a different
bootstrap user.

Seeding Demo Data
-----------------

Load deterministic demo users and projects with the ``seed-data`` command. For
example, to create 10 users and 10 projects while assigning a custom password ::

   flask --app app:create_app seed-data --users 10 --projects 10 --password "Temp123!"

An equivalent Makefile helper accepts the same overrides ::

   make seed users=10 projects=10 password=Temp123!

Omit options to fall back to the defaults (5 users, 5 projects, password
``ChangeMe123!``). The command is idempotent: rerunning the seed only adds new
records when unique emails or project names are available.

Authenticate by submitting Basic credentials to ``POST /auth/login``. This
endpoint is rate limited (default: ``5 per minute``). The API responds with a
bearer token:

.. code-block:: bash

   curl -u manager@example.com:SuperSecret123 http://127.0.0.1:5000/auth/login

Use the returned ``access_token`` when calling protected endpoints:

.. code-block:: text

   Authorization: Bearer <access_token>

All endpoints require a bearer token. Authenticated users of any role can
perform read-only requests, while only users with the ``manager`` role can
perform create, update, or delete operations. When creating or updating users
you must supply a ``password`` field which must pass the configured complexity
regex and is stored as a secure hash that is never returned in responses.

Key Endpoints
-------------

Users
~~~~~

``POST /users`` – Create a new user (manager only)
``GET /users`` – List all users (paginated)
``GET /users/<id>`` – Fetch a user
``PUT /users/<id>`` – Update user details (manager only)
``DELETE /users/<id>`` – Delete a user (manager only)

Projects
~~~~~~~~

``POST /projects`` – Create a new project (manager only)
``GET /projects`` – List all projects (paginated)
``GET /projects/<id>`` – Fetch a project
``PUT /projects/<id>`` – Update a project (manager only)
``DELETE /projects/<id>`` – Delete a project (manager only)

The API automatically assigns the authenticated manager as ``created_by`` and
removes all associated tasks when a project is deleted.

Tasks
~~~~~

``POST /projects/<id>/tasks`` – Create a task within a project (manager only)
``GET /projects/<id>/tasks`` – List tasks for a project (paginated)
``PUT /projects/<id>/tasks/<task_id>`` – Update a task (manager only)

Marshmallow validation ensures required fields are supplied and values fall
within expected ranges. Pagination responses include a ``meta`` object with
``page``, ``per_page``, ``total``, and navigation hints.

Pagination Parameters
---------------------

All list endpoints accept ``page`` and ``per_page`` query arguments. Values
larger than ``PAGINATION_MAX_PAGE_SIZE`` raise a business validation error. The
defaults can be configured via environment variables.

When overriding ``PASSWORD_COMPLEXITY_REGEX`` in ``.env`` make sure to use
single backslashes (``\``) in escape sequences, e.g. ``\d`` and ``\W``. Double
escaping would cause the pattern to match literal characters instead of the
expected character classes.

CORS
----

Cross-Origin Resource Sharing is enforced with ``Flask-Cors``. Only origins in
``CORS_ALLOWED_ORIGINS`` may call the API. The default allow list is
``http://localhost:3000`` for local development.
