"""Integration tests for the HTTP routes."""

from __future__ import annotations

from http import HTTPStatus


def test_index_redirects_to_dashboard(client) -> None:
    response = client.get("/", follow_redirects=False)

    assert response.status_code == HTTPStatus.FOUND
    assert "/dashboard/" in response.headers["Location"]


def test_dashboard_requires_login(client) -> None:
    response = client.get("/dashboard/", follow_redirects=False)

    assert response.status_code == HTTPStatus.FOUND
    assert "/login" in response.headers["Location"]


def test_dashboard_renders_for_authenticated_user(client, login, admin_user) -> None:
    login(admin_user.email, "password123")
    response = client.get("/dashboard/")

    assert response.status_code == HTTPStatus.OK
    assert b"Dashboard" in response.data
    assert b"Ore totali" in response.data
