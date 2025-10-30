"""Authentication flow tests."""

from __future__ import annotations

from base64 import b64encode

from app.extensions import db
from app.models import User


def test_login_returns_token(client, create_user_record):
    """Valid credentials return a JWT access token."""

    password = "ValidPass123!"
    user = create_user_record(
        name="Alice Manager",
        email="alice.manager@example.com",
        role="manager",
        password=password,
    )

    basic_token = b64encode(f"{user.email}:{password}".encode()).decode()
    response = client.post(
        "/auth/login",
        headers={"Authorization": f"Basic {basic_token}"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert "access_token" in body
    assert body["token_type"] == "Bearer"


def test_login_rejects_invalid_credentials(client):
    """Unknown users receive an unauthorized response."""

    basic_token = b64encode("unknown@example.com:wrong".encode()).decode()
    response = client.post(
        "/auth/login",
        headers={"Authorization": f"Basic {basic_token}"},
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "unauthorized"


def test_init_admin_creates_default_admin(app):
    """init-admin seeds a default manager when no users exist."""

    runner = app.test_cli_runner()
    with app.app_context():
        db.drop_all()
        db.create_all()

    result = runner.invoke(args=["init-admin"])
    assert result.exit_code == 0

    with app.app_context():
        admin = User.query.filter_by(email=app.config["DEFAULT_ADMIN_EMAIL"]).first()
        assert admin is not None
        assert admin.role == "manager"
        assert admin.check_password(app.config["DEFAULT_ADMIN_PASSWORD"])


def test_init_admin_is_idempotent(app):
    """Running init-admin repeatedly does not create duplicate admins."""

    runner = app.test_cli_runner()
    with app.app_context():
        db.drop_all()
        db.create_all()

    first_run = runner.invoke(args=["init-admin"])
    assert first_run.exit_code == 0

    second_run = runner.invoke(args=["init-admin"])
    assert second_run.exit_code == 0
    assert "Default admin already exists." in second_run.output

    with app.app_context():
        admins = User.query.filter_by(email=app.config["DEFAULT_ADMIN_EMAIL"]).all()
        assert len(admins) == 1
