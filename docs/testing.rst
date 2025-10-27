Testing
=======

Overview
--------

Unit tests are written with ``pytest`` and cover all major business rules,
including role enforcement and relational behaviour between projects and tasks.
Tests execute against an in-memory SQLite database for fast, isolated runs.

Running Tests
-------------

Install dependencies if you have not already ::

   pip install -r requirements.txt

Run the full suite ::

   pytest

You can also use the convenience target defined in the repository Makefile ::

   make test

Fixtures
--------

Key fixtures are defined in ``tests/conftest.py``:

``app`` – Provides a Flask application configured with the testing database.

``client`` – Offers a Flask ``test_client`` for issuing HTTP requests.

``manager_headers`` / ``employee_headers`` – Convenience dictionaries with the
appropriate ``X-User-Role`` header for RBAC checks.

``json_dumps`` – Wrapper around ``json.dumps`` to simplify payload generation.

Helpers
-------

``tests/utils.py`` contains small factories for creating users, projects, and
tasks through the API to reduce duplication in test cases.
