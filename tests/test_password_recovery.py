"""Tests for password recovery functionality."""
from __future__ import annotations

from datetime import datetime, timedelta
from http import HTTPStatus

from app.extensions import db
from app.models import Person


def test_request_password_reset_page_loads(client) -> None:
    """Test that the password reset request page loads successfully."""
    response = client.get("/request-password-reset")
    
    assert response.status_code == HTTPStatus.OK
    assert b"Recupero Password" in response.data
    assert b"Inserisci la tua email" in response.data


def test_request_password_reset_with_valid_email(client, admin_user) -> None:
    """Test requesting a password reset with a valid email."""
    response = client.post(
        "/request-password-reset",
        data={"email": admin_user.email},
        follow_redirects=True
    )
    
    assert response.status_code == HTTPStatus.OK
    assert b"Link di reset generato" in response.data or b"riceverai un link" in response.data
    
    # Check that the user now has a reset token
    user = Person.query.filter_by(email=admin_user.email).first()
    assert user.reset_token is not None
    assert user.reset_token_expiry is not None


def test_request_password_reset_with_invalid_email(client) -> None:
    """Test requesting a password reset with an invalid email."""
    response = client.post(
        "/request-password-reset",
        data={"email": "nonexistent@example.com"},
        follow_redirects=True
    )
    
    # Should still show success message for security (don't reveal if email exists)
    assert response.status_code == HTTPStatus.OK
    assert b"riceverai un link" in response.data


def test_reset_password_page_loads_with_valid_token(client, admin_user) -> None:
    """Test that the reset password page loads with a valid token."""
    token = admin_user.generate_reset_token()
    db.session.commit()
    
    response = client.get(f"/reset-password/{token}")
    
    assert response.status_code == HTTPStatus.OK
    assert b"Reimposta Password" in response.data
    assert b"Inserisci la tua nuova password" in response.data


def test_reset_password_page_rejects_invalid_token(client) -> None:
    """Test that the reset password page rejects an invalid token."""
    response = client.get("/reset-password/invalid-token", follow_redirects=True)
    
    assert response.status_code == HTTPStatus.OK
    assert b"Link di reset non valido o scaduto" in response.data


def test_reset_password_page_rejects_expired_token(client, admin_user) -> None:
    """Test that the reset password page rejects an expired token."""
    token = admin_user.generate_reset_token()
    # Make the token expired
    admin_user.reset_token_expiry = datetime.utcnow() - timedelta(hours=2)
    db.session.commit()
    
    response = client.get(f"/reset-password/{token}", follow_redirects=True)
    
    assert response.status_code == HTTPStatus.OK
    assert b"Link di reset non valido o scaduto" in response.data


def test_reset_password_successfully(client, admin_user) -> None:
    """Test successfully resetting a password."""
    token = admin_user.generate_reset_token()
    db.session.commit()
    
    new_password = "newpassword123"
    response = client.post(
        f"/reset-password/{token}",
        data={"password": new_password, "confirm_password": new_password},
        follow_redirects=True
    )
    
    assert response.status_code == HTTPStatus.OK
    assert b"Password reimpostata con successo" in response.data
    
    # Check that the password was changed
    user = Person.query.filter_by(email=admin_user.email).first()
    assert user.check_password(new_password)
    assert not user.check_password("password123")
    
    # Check that the reset token was cleared
    assert user.reset_token is None
    assert user.reset_token_expiry is None


def test_reset_password_mismatched_passwords(client, admin_user) -> None:
    """Test that mismatched passwords are rejected."""
    token = admin_user.generate_reset_token()
    db.session.commit()
    
    response = client.post(
        f"/reset-password/{token}",
        data={"password": "newpassword123", "confirm_password": "differentpassword"},
        follow_redirects=False
    )
    
    # Should reload the form with an error
    assert response.status_code == HTTPStatus.OK
    # The old password should still work
    user = Person.query.filter_by(email=admin_user.email).first()
    assert user.check_password("password123")


def test_login_page_has_forgot_password_link(client) -> None:
    """Test that the login page has a link to the forgot password page."""
    response = client.get("/login")
    
    assert response.status_code == HTTPStatus.OK
    assert b"Password dimenticata?" in response.data
    assert b"/request-password-reset" in response.data


def test_authenticated_user_redirected_from_password_reset(client, login, admin_user) -> None:
    """Test that authenticated users are redirected from password reset pages."""
    login(admin_user.email, "password123")
    
    # Try to access the request password reset page
    response = client.get("/request-password-reset", follow_redirects=False)
    assert response.status_code == HTTPStatus.FOUND
    assert "/dashboard" in response.headers["Location"]
    
    # Try to access the reset password page with a token
    token = admin_user.generate_reset_token()
    db.session.commit()
    response = client.get(f"/reset-password/{token}", follow_redirects=False)
    assert response.status_code == HTTPStatus.FOUND
    assert "/dashboard" in response.headers["Location"]


def test_person_model_generate_reset_token(admin_user) -> None:
    """Test that the Person model can generate a reset token."""
    token = admin_user.generate_reset_token()
    
    assert token is not None
    assert len(token) > 0
    assert admin_user.reset_token == token
    assert admin_user.reset_token_expiry is not None
    assert admin_user.reset_token_expiry > datetime.utcnow()


def test_person_model_verify_reset_token(admin_user) -> None:
    """Test that the Person model can verify a reset token."""
    token = admin_user.generate_reset_token()
    db.session.commit()
    
    # Valid token should verify
    assert admin_user.verify_reset_token(token) is True
    
    # Invalid token should not verify
    assert admin_user.verify_reset_token("invalid-token") is False
    
    # Expired token should not verify
    admin_user.reset_token_expiry = datetime.utcnow() - timedelta(hours=2)
    db.session.commit()
    assert admin_user.verify_reset_token(token) is False


def test_person_model_clear_reset_token(admin_user) -> None:
    """Test that the Person model can clear a reset token."""
    admin_user.generate_reset_token()
    db.session.commit()
    
    assert admin_user.reset_token is not None
    assert admin_user.reset_token_expiry is not None
    
    admin_user.clear_reset_token()
    db.session.commit()
    
    assert admin_user.reset_token is None
    assert admin_user.reset_token_expiry is None
