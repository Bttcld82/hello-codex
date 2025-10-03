"""HTTP route handlers for the hello-codex application."""

from __future__ import annotations

from http import HTTPStatus

from flask import Blueprint, jsonify

from .models import Project

bp = Blueprint("main", __name__)


@bp.get("/")
def index() -> tuple[dict[str, str], int]:
    """Return a minimal JSON payload to verify the service is running."""
    return jsonify({"message": "Hello from hello-codex"}), HTTPStatus.OK


@bp.get("/projects")
def list_projects() -> tuple[dict[str, list[str]], int]:
    """List the names of registered projects."""
    project_names = [project.name for project in Project.query.order_by(Project.name)]
    return jsonify({"projects": project_names}), HTTPStatus.OK
