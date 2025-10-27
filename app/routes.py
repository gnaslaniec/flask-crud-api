"""HTTP routes providing the public API."""

from __future__ import annotations

from typing import Any, Dict, TypeVar

from flask import Blueprint, Response, abort, jsonify, request
from marshmallow import ValidationError

from .auth import require_manager
from .extensions import db
from .models import Project, Task, User
from .schemas import ProjectSchema, TaskSchema, UserSchema

api_bp = Blueprint("api", __name__)

user_schema = UserSchema()
users_schema = UserSchema(many=True)
project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

ModelT = TypeVar("ModelT")


@api_bp.errorhandler(ValidationError)
def handle_validation_error(err: ValidationError) -> Response:
    """Convert marshmallow validation errors into JSON responses."""
    return (
        jsonify({"error": "validation_error", "messages": err.messages}),
        400,
    )


def _json_response(payload: Dict[str, Any], status: int = 200) -> Response:
    """Consistently format JSON responses."""
    return jsonify(payload), status


def _get_or_404(model: type[ModelT], ident: int) -> ModelT:
    """Fetch a model by primary key or raise a 404."""

    instance = db.session.get(model, ident)
    if instance is None:
        abort(404)
    return instance


@api_bp.route("/users", methods=["POST"])
@require_manager
def create_user() -> Response:
    """
    Create a new user.

    :raises marshmallow.ValidationError: If payload validation fails.
    :return: The created user resource.
    :rtype: flask.Response
    """

    data = user_schema.load(request.get_json() or {})
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return _json_response({"data": user_schema.dump(user)}, 201)


@api_bp.route("/users", methods=["GET"])
def list_users() -> Response:
    """
    List all users.

    :return: A collection of user resources.
    :rtype: flask.Response
    """

    users = User.query.order_by(User.id).all()
    return _json_response({"data": users_schema.dump(users)})


@api_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id: int) -> Response:
    """
    Retrieve a specific user.

    :param user_id: Identifier of the user to fetch.
    :type user_id: int
    :return: The requested user resource.
    :rtype: flask.Response
    """

    user = _get_or_404(User, user_id)
    return _json_response({"data": user_schema.dump(user)})


@api_bp.route("/users/<int:user_id>", methods=["PUT"])
@require_manager
def update_user(user_id: int) -> Response:
    """
    Update an existing user.

    :param user_id: Identifier of the user to update.
    :type user_id: int
    :return: The updated user resource.
    :rtype: flask.Response
    """

    user = _get_or_404(User, user_id)
    data = user_schema.load(request.get_json() or {}, partial=True)

    for key, value in data.items():
        setattr(user, key, value)

    db.session.commit()
    return _json_response({"data": user_schema.dump(user)})


@api_bp.route("/users/<int:user_id>", methods=["DELETE"])
@require_manager
def delete_user(user_id: int) -> Response:
    """
    Delete a user.

    :param user_id: Identifier of the user to delete.
    :type user_id: int
    :return: Confirmation of deletion.
    :rtype: flask.Response
    """

    user = _get_or_404(User, user_id)
    db.session.delete(user)
    db.session.commit()
    return _json_response({"message": "User deleted."})


@api_bp.route("/projects", methods=["POST"])
@require_manager
def create_project() -> Response:
    """
    Create a new project.

    :return: The created project resource.
    :rtype: flask.Response
    """

    data = project_schema.load(request.get_json() or {})

    created_by = data.get("created_by")
    if created_by is not None and not db.session.get(User, created_by):
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"User {created_by} does not exist.",
                }
            ),
            404,
        )

    project = Project(**data)
    db.session.add(project)
    db.session.commit()
    return _json_response({"data": project_schema.dump(project)}, 201)


@api_bp.route("/projects", methods=["GET"])
def list_projects() -> Response:
    """
    List all projects.

    :return: A collection of project resources.
    :rtype: flask.Response
    """

    projects = Project.query.order_by(Project.id).all()
    return _json_response({"data": projects_schema.dump(projects)})


@api_bp.route("/projects/<int:project_id>", methods=["GET"])
def get_project(project_id: int) -> Response:
    """
    Retrieve a specific project.

    :param project_id: Identifier of the project to fetch.
    :type project_id: int
    :return: The requested project resource.
    :rtype: flask.Response
    """

    project = _get_or_404(Project, project_id)
    return _json_response({"data": project_schema.dump(project)})


@api_bp.route("/projects/<int:project_id>", methods=["PUT"])
@require_manager
def update_project(project_id: int) -> Response:
    """
    Update a project.

    :param project_id: Identifier of the project to update.
    :type project_id: int
    :return: The updated project resource.
    :rtype: flask.Response
    """

    project = _get_or_404(Project, project_id)
    data = project_schema.load(request.get_json() or {}, partial=True)

    created_by = data.get("created_by")
    if created_by is not None and not db.session.get(User, created_by):
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"User {created_by} does not exist.",
                }
            ),
            404,
        )

    for key, value in data.items():
        setattr(project, key, value)

    db.session.commit()
    return _json_response({"data": project_schema.dump(project)})


@api_bp.route("/projects/<int:project_id>", methods=["DELETE"])
@require_manager
def delete_project(project_id: int) -> Response:
    """
    Delete a project.

    :param project_id: Identifier of the project to delete.
    :type project_id: int
    :return: Confirmation of deletion.
    :rtype: flask.Response
    """

    project = _get_or_404(Project, project_id)
    db.session.delete(project)
    db.session.commit()
    return _json_response({"message": "Project deleted."})


@api_bp.route("/projects/<int:project_id>/tasks", methods=["POST"])
@require_manager
def create_task(project_id: int) -> Response:
    """
    Create a task under a project.

    :param project_id: Identifier of the parent project.
    :type project_id: int
    :return: The created task resource.
    :rtype: flask.Response
    """

    project = _get_or_404(Project, project_id)
    payload = request.get_json() or {}
    data = task_schema.load(payload)

    assignee_id = data.get("assigned_to")
    if assignee_id is not None and not db.session.get(User, assignee_id):
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"User {assignee_id} does not exist.",
                }
            ),
            404,
        )

    task = Task(**data, project=project)
    db.session.add(task)
    db.session.commit()
    return _json_response({"data": task_schema.dump(task)}, 201)


@api_bp.route("/projects/<int:project_id>/tasks", methods=["GET"])
def list_tasks(project_id: int) -> Response:
    """
    List tasks for a project.

    :param project_id: Identifier of the parent project.
    :type project_id: int
    :return: Collection of tasks for the project.
    :rtype: flask.Response
    """

    project = _get_or_404(Project, project_id)
    return _json_response({"data": tasks_schema.dump(project.tasks)})
