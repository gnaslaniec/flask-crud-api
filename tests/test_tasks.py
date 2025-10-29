"""Tests for task endpoints."""

from __future__ import annotations

import json

from .utils import create_project, create_task


def test_manager_can_create_task(client, manager_headers):
    """Managers can create tasks within a project."""

    project = create_project(client, manager_headers)
    response = client.post(
        f"/projects/{project['id']}/tasks",
        data=json.dumps({"title": "Task 1", "description": "Do the thing"}),
        headers=manager_headers,
    )
    assert response.status_code == 201
    data = response.get_json()["data"]
    assert data["title"] == "Task 1"
    assert data["project_id"] == project["id"]


def test_employee_cannot_create_task(client, manager_headers, employee_headers):
    """Employees are forbidden from creating tasks."""

    project = create_project(client, manager_headers)
    response = client.post(
        f"/projects/{project['id']}/tasks",
        data=json.dumps({"title": "Forbidden Task"}),
        headers=employee_headers,
    )
    assert response.status_code == 403


def test_task_assignment_requires_existing_user(client, manager_headers):
    """Assigning a task to a non-existent user fails."""

    project = create_project(client, manager_headers)
    response = client.post(
        f"/projects/{project['id']}/tasks",
        data=json.dumps({"title": "Assign", "assigned_to": 123}),
        headers=manager_headers,
    )
    assert response.status_code == 404


def test_manager_can_update_task(client, manager_headers):
    """Managers can update an existing task."""

    project = create_project(client, manager_headers)
    task = create_task(
        client,
        manager_headers,
        project["id"],
        title="Initial",
        description="Start",
    )

    response = client.put(
        f"/projects/{project['id']}/tasks/{task['id']}",
        data=json.dumps({
            "title": "Updated",
            "status": "in_progress",
            "description": "Refined",
        }),
        headers=manager_headers,
    )

    assert response.status_code == 200
    payload = response.get_json()["data"]
    assert payload["title"] == "Updated"
    assert payload["status"] == "in_progress"
    assert payload["description"] == "Refined"


def test_list_tasks(client, manager_headers, employee_headers):
    """Listing tasks returns all project tasks."""

    project = create_project(client, manager_headers)
    create_task(client, manager_headers, project["id"], title="Task A")
    create_task(client, manager_headers, project["id"], title="Task B")

    response = client.get(
        f"/projects/{project['id']}/tasks", headers=employee_headers
    )
    assert response.status_code == 200
    titles = [task["title"] for task in response.get_json()["data"]]
    assert "Task A" in titles and "Task B" in titles
