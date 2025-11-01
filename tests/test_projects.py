"""Tests for project endpoints."""

from __future__ import annotations

import json

from app.models import Task

from .utils import create_project, create_task


def test_manager_can_create_project(client, manager_headers):
    """Managers can create projects."""

    response = client.post(
        "/projects",
        data=json.dumps(
            {
                "name": "Project X",
                "description": "Build something great.",
            }
        ),
        headers=manager_headers,
    )
    assert response.status_code == 201
    data = response.get_json()["data"]
    assert data["name"] == "Project X"
    assert data["created_by"] is not None


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


def test_delete_project_removes_tasks(client, manager_headers, employee_headers):
    """Deleting a project cascades to its tasks."""

    project = create_project(client, manager_headers)
    create_task(client, manager_headers, project["id"])

    delete_response = client.delete(
        f"/projects/{project['id']}", headers=manager_headers
    )
    assert delete_response.status_code == 200
    assert delete_response.get_json()["message"] == "Project deleted."

    tasks_response = client.get(
        f"/projects/{project['id']}/tasks", headers=employee_headers
    )
    assert tasks_response.status_code == 404
    assert tasks_response.get_json()["error"] == "not_found"

    with client.application.app_context():
        assert Task.query.filter_by(project_id=project["id"]).count() == 0


def test_list_projects(client, manager_headers, employee_headers):
    """Listing projects returns created projects."""

    create_project(client, manager_headers, name="Project A")
    create_project(client, manager_headers, name="Project B")

    response = client.get("/projects", headers=employee_headers)
    assert response.status_code == 200
    payload = response.get_json()
    names = [project["name"] for project in payload["data"]]
    assert "Project A" in names and "Project B" in names
    meta = payload["meta"]
    assert meta["page"] == 1
    assert meta["per_page"] >= 2
    assert meta["total"] >= 2


def test_update_project_rejects_immutable_fields(client, manager_headers):
    """Updating immutable fields returns a business validation error."""

    project = create_project(client, manager_headers)
    response = client.put(
        f"/projects/{project['id']}",
        data=json.dumps({"created_by": 999}),
        headers=manager_headers,
    )
    assert response.status_code == 422
    body = response.get_json()
    assert body["error"] == "business_validation_error"


def test_list_projects_rejects_oversized_page_size(
    client, manager_headers, employee_headers
):
    """per_page parameter greater than configured maximum is rejected."""

    for i in range(5):
        create_project(client, manager_headers, name=f"Proj {i}")

    max_per_page = client.application.config["PAGINATION_MAX_PAGE_SIZE"]
    response = client.get(
        f"/projects?per_page={max_per_page + 1}", headers=employee_headers
    )
    assert response.status_code == 422
    body = response.get_json()
    assert body["error"] == "business_validation_error"
    assert str(max_per_page) in body["message"]


def test_list_projects_rejects_invalid_page(client, manager_headers, employee_headers):
    """Invalid pagination parameters raise a business validation error."""

    create_project(client, manager_headers)
    response = client.get("/projects?page=0", headers=employee_headers)
    assert response.status_code == 422
    assert response.get_json()["error"] == "business_validation_error"
