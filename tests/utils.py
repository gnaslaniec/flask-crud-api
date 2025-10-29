"""Test helper functions and payload factories."""

from __future__ import annotations

import json
from typing import Any, Dict
from uuid import uuid4


def create_user(client, manager_headers, **overrides) -> Dict[str, Any]:
    """Create a user through the API."""

    payload = {
        "name": "Jane Manager",
        "email": f"user-{uuid4().hex}@example.com",
        "role": "manager",
        "password": "Password123!",
    }
    payload.update(overrides)

    response = client.post(
        "/users",
        data=json.dumps(payload),
        headers=manager_headers,
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def create_project(client, manager_headers, **overrides) -> Dict[str, Any]:
    """Create a project through the API."""

    payload = {"name": "Project Alpha", "description": "Top secret project."}
    payload.update(overrides)

    response = client.post(
        "/projects",
        data=json.dumps(payload),
        headers=manager_headers,
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def create_task(
    client, manager_headers, project_id: int, **overrides
) -> Dict[str, Any]:
    """Create a task for a project through the API."""

    payload = {"title": "Initial task", "description": "Something to do."}
    payload.update(overrides)

    response = client.post(
        f"/projects/{project_id}/tasks",
        data=json.dumps(payload),
        headers=manager_headers,
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]
