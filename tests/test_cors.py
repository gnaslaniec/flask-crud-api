"""CORS configuration tests."""

from __future__ import annotations


def test_cors_allows_configured_origin(client):
    """Allowed origins receive CORS headers."""

    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.status_code == 200
    assert response.headers.get("Access-Control-Allow-Origin") == "http://localhost:3000"


def test_cors_blocks_unconfigured_origin(client):
    """Origins not in the allow-list do not receive CORS headers."""

    response = client.get(
        "/health",
        headers={"Origin": "https://malicious.example"},
    )
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" not in response.headers
