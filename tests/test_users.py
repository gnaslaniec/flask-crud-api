"""Tests covering user endpoints."""

from __future__ import annotations

import json

from .utils import create_user


def test_manager_can_create_user(client, manager_headers):
    """Creating a user succeeds when requester is a manager."""

    response = client.post(
        "/users",
        data=json.dumps(
            {"name": "John Doe", "email": "john@example.com", "role": "employee"}
        ),
        headers=manager_headers,
    )
    assert response.status_code == 201
    assert response.get_json()["data"]["email"] == "john@example.com"


def test_employee_cannot_create_user(client, employee_headers):
    """Employees are not allowed to create new users."""

    response = client.post(
        "/users",
        data=json.dumps(
            {"name": "John Doe", "email": "john@example.com", "role": "employee"}
        ),
        headers=employee_headers,
    )
    assert response.status_code == 403


def test_get_user(client, manager_headers):
    """Fetching a single user returns the resource."""

    created = create_user(client, manager_headers)
    response = client.get(f"/users/{created['id']}")
    assert response.status_code == 200
    assert response.get_json()["data"]["email"] == created["email"]


def test_update_user(client, manager_headers):
    """Managers can update an existing user."""

    created = create_user(client, manager_headers)
    response = client.put(
        f"/users/{created['id']}",
        data=json.dumps({"name": "Updated Name"}),
        headers=manager_headers,
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["name"] == "Updated Name"


def test_delete_user(client, manager_headers):
    """Managers can delete an existing user."""

    created = create_user(client, manager_headers)
    response = client.delete(f"/users/{created['id']}", headers=manager_headers)
    assert response.status_code == 200
    assert response.get_json()["message"] == "User deleted."

    # Ensure the user is gone
    response = client.get(f"/users/{created['id']}")
    assert response.status_code == 404
