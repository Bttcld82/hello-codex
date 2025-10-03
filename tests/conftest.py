"""Test fixtures for the hello-codex Flask application."""

from __future__ import annotations

import pytest

from app_flask import create_app
from app_flask.extensions import db


@pytest.fixture
def app():
    """Create a Flask app instance for testing."""
    application = create_app()

    with application.app_context():
        db.drop_all()
        db.create_all()

    yield application

    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Return a test client bound to the app fixture."""
    return app.test_client()
