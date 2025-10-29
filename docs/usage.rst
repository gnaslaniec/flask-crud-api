Usage Guide
===========

Quick Overview
--------------

The Project Management API is a Flask application that exposes CRUD endpoints
for users, projects, and tasks. Write operations require a manager-authenticated
JSON Web Token (JWT), while read operations are open to all roles.

Running the Server
------------------

1. Create and activate a virtual environment.
2. Install dependencies ::

      pip install -r requirements.txt

3. Initialise the database ::

      flask --app run.py init-db

4. Start the development server ::

      flask --app run.py run

Authentication & Authorisation
------------------------------

To bootstrap the system run ``flask --app run.py init-db``. On first execution
it creates a default manager account using the credentials supplied via the
``DEFAULT_ADMIN_EMAIL`` and ``DEFAULT_ADMIN_PASSWORD`` environment variables
(defaults: ``admin@example.com`` / ``ChangeMe123!``).

Authenticate by submitting Basic credentials to ``POST /auth/login``. The API
responds with a bearer token:

.. code-block:: bash

   curl -u manager@example.com:SuperSecret123 http://127.0.0.1:5000/auth/login

Use the returned ``access_token`` when calling protected endpoints:

.. code-block:: text

   Authorization: Bearer <access_token>

All endpoints require a bearer token. Authenticated users of any role can
perform read-only requests, while only users with the ``manager`` role can
perform create, update, or delete operations. When creating or updating users
you must supply a ``password`` field which is stored as a secure hash and never
returned in responses.

Key Endpoints
-------------

Users
~~~~~

``POST /users`` – Create a new user (manager only)
``GET /users`` – List all users
``GET /users/<id>`` – Fetch a user
``PUT /users/<id>`` – Update user details (manager only)
``DELETE /users/<id>`` – Delete a user (manager only)

Projects
~~~~~~~~

``POST /projects`` – Create a new project (manager only)
``GET /projects`` – List all projects
``GET /projects/<id>`` – Fetch a project
``PUT /projects/<id>`` – Update a project (manager only)
``DELETE /projects/<id>`` – Delete a project (manager only)

The API automatically assigns the authenticated manager as ``created_by`` and
removes all associated tasks when a project is deleted.

Tasks
~~~~~

``POST /projects/<id>/tasks`` – Create a task within a project (manager only)
``GET /projects/<id>/tasks`` – List tasks for a project
``PUT /projects/<id>/tasks/<task_id>`` – Update a task (manager only)

Marshmallow validation ensures required fields are supplied and values fall
within expected ranges.
