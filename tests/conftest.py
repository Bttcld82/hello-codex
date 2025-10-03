from __future__ import annotations

import pytest
from app_flask import create_app
from app_flask.extensions import db
from app_flask.models import Person, Project


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite://",
        WTF_CSRF_ENABLED=False,
        SECRET_KEY="test",
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin_user(app):
    user = Person(full_name="Admin", email="admin@example.com", role="admin", is_active=True)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def regular_user(app):
    user = Person(full_name="User", email="user@example.com", role="user", is_active=True)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def sample_project(app):
    project = Project(name="Project A", code="PA", client="Client", is_active=True)
    db.session.add(project)
    db.session.commit()
    return project


@pytest.fixture()
def login(client, admin_user):
    def _login(email: str, password: str) -> None:
        client.post("/login", data={"email": email, "password": password}, follow_redirects=True)

    return _login
