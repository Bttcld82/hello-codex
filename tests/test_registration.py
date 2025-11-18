"""Tests for user registration functionality."""

from __future__ import annotations

from http import HTTPStatus

from app.models import Person


def test_register_page_loads(client) -> None:
    """Test that the registration page loads successfully."""
    response = client.get("/register")

    assert response.status_code == HTTPStatus.OK
    assert b"Registrazione" in response.data
    assert b"Nome completo" in response.data
    assert b"Email" in response.data
    assert b"Password" in response.data
    assert b"Conferma Password" in response.data


def test_register_new_user_successfully(client) -> None:
    """Test successful registration of a new user."""
    response = client.post(
        "/register",
        data={
            "full_name": "Mario Rossi",
            "email": "mario.rossi@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == HTTPStatus.OK
    assert b"Registrazione completata con successo" in response.data
    assert b"Accesso" in response.data  # Redirected to login page

    # Verify user was created in database
    user = Person.query.filter_by(email="mario.rossi@example.com").first()
    assert user is not None
    assert user.full_name == "Mario Rossi"
    assert user.role == "user"
    assert user.is_active is True
    assert user.check_password("password123") is True


def test_register_with_existing_email(client, admin_user) -> None:
    """Test registration with an email that already exists."""
    response = client.post(
        "/register",
        data={
            "full_name": "Another User",
            "email": admin_user.email,
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == HTTPStatus.OK
    assert b"Email gi" in response.data or b"registrata" in response.data


def test_register_with_mismatched_passwords(client) -> None:
    """Test registration with mismatched passwords."""
    response = client.post(
        "/register",
        data={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "different_password",
        },
        follow_redirects=True,
    )

    assert response.status_code == HTTPStatus.OK
    # Should show validation error
    assert b"Le password devono corrispondere" in response.data

    # Verify user was not created
    user = Person.query.filter_by(email="test@example.com").first()
    assert user is None


def test_register_with_short_password(client) -> None:
    """Test registration with password shorter than 8 characters."""
    response = client.post(
        "/register",
        data={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "short",
            "confirm_password": "short",
        },
        follow_redirects=True,
    )

    assert response.status_code == HTTPStatus.OK
    # Should show validation error for minimum length

    # Verify user was not created
    user = Person.query.filter_by(email="test@example.com").first()
    assert user is None


def test_register_with_invalid_email(client) -> None:
    """Test registration with an invalid email format."""
    response = client.post(
        "/register",
        data={
            "full_name": "Test User",
            "email": "not-an-email",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == HTTPStatus.OK
    # Should show validation error
    assert b"Inserire un" in response.data or b"email valida" in response.data

    # Verify user was not created
    user = Person.query.filter_by(email="not-an-email").first()
    assert user is None


def test_register_with_missing_full_name(client) -> None:
    """Test registration without providing a full name."""
    response = client.post(
        "/register",
        data={
            "full_name": "",
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == HTTPStatus.OK

    # Verify user was not created
    user = Person.query.filter_by(email="test@example.com").first()
    assert user is None


def test_register_redirects_authenticated_users(client, admin_user) -> None:
    """Test that authenticated users are redirected from the registration page."""
    # Login first
    client.post("/login", data={"email": admin_user.email, "password": "password123"})

    # Try to access registration page
    response = client.get("/register", follow_redirects=True)

    assert response.status_code == HTTPStatus.OK
    # Should be redirected to dashboard
    assert b"Dashboard" in response.data or b"Tracker" in response.data


def test_register_email_case_insensitive(client) -> None:
    """Test that email registration is case-insensitive."""
    response = client.post(
        "/register",
        data={
            "full_name": "Test User",
            "email": "Test.User@Example.COM",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == HTTPStatus.OK
    assert b"Registrazione completata con successo" in response.data

    # Verify email was stored in lowercase
    user = Person.query.filter_by(email="test.user@example.com").first()
    assert user is not None
    assert user.email == "test.user@example.com"


def test_register_page_has_login_link(client) -> None:
    """Test that the registration page has a link back to login."""
    response = client.get("/register")

    assert response.status_code == HTTPStatus.OK
    assert b"Hai gi" in response.data or b"Accedi" in response.data
