"""Integration tests for the HTTP routes."""

from __future__ import annotations

from http import HTTPStatus

from app_flask.extensions import db
from app_flask.models import Project


def test_index_returns_greeting(client) -> None:
    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == {"message": "Hello from hello-codex"}


def test_projects_endpoint_lists_seeded_projects(app, client) -> None:
    with app.app_context():
        db.session.add(Project(name="Sample"))
        db.session.commit()

    response = client.get("/projects")

    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == {"projects": ["Sample"]}
