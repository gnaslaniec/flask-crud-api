"""Tests for project endpoints."""

from __future__ import annotations

import json

from .utils import create_project, create_task, create_user


def test_manager_can_create_project(client, manager_headers):
    """Managers can create projects."""

    owner = create_user(client, manager_headers)
    response = client.post(
        "/projects",
        data=json.dumps(
            {
                "name": "Project X",
                "description": "Build something great.",
                "created_by": owner["id"],
            }
        ),
        headers=manager_headers,
    )
    assert response.status_code == 201
    data = response.get_json()["data"]
    assert data["name"] == "Project X"
    assert data["created_by"] == owner["id"]


def test_employee_cannot_create_project(client, employee_headers):
    """Employees are forbidden from creating projects."""

    response = client.post(
        "/projects",
        data=json.dumps({"name": "Project Beta", "description": "Should be blocked."}),
        headers=employee_headers,
    )
    assert response.status_code == 403


def test_update_project(client, manager_headers):
    """Managers can update project attributes."""

    project = create_project(client, manager_headers)
    response = client.put(
        f"/projects/{project['id']}",
        data=json.dumps({"description": "Updated"}),
        headers=manager_headers,
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["description"] == "Updated"


def test_delete_project_removes_tasks(client, manager_headers):
    """Deleting a project cascades to its tasks."""

    project = create_project(client, manager_headers)
    create_task(client, manager_headers, project["id"])

    delete_response = client.delete(
        f"/projects/{project['id']}", headers=manager_headers
    )
    assert delete_response.status_code == 200

    tasks_response = client.get(f"/projects/{project['id']}/tasks")
    assert tasks_response.status_code == 404


def test_list_projects(client, manager_headers):
    """Listing projects returns created projects."""

    create_project(client, manager_headers, name="Project A")
    create_project(client, manager_headers, name="Project B")

    response = client.get("/projects")
    assert response.status_code == 200
    names = [project["name"] for project in response.get_json()["data"]]
    assert "Project A" in names and "Project B" in names
