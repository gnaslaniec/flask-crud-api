Usage Guide
===========

Quick Overview
--------------

The Project Management API is a Flask application that exposes CRUD endpoints
for users, projects, and tasks. Write operations require the ``X-User-Role``
header to be set to ``manager`` while read operations are open to all roles.

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

This sample application does not implement full authentication. Instead, it
expects a simple header on mutating requests:

``X-User-Role: manager`` – Grants permission to create, update, and delete
users, projects, and tasks.

Leave the header empty or use ``employee`` for read-only operations.

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

Tasks
~~~~~

``POST /projects/<id>/tasks`` – Create a task within a project (manager only)
``GET /projects/<id>/tasks`` – List tasks for a project

Marshmallow validation ensures required fields are supplied and values fall
within expected ranges.
