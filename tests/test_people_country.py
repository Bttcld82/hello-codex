"""Tests for the country field in Person model."""

from __future__ import annotations


def test_person_model_has_country_field(app):
    """Test that Person model has country field."""
    from app.models import Person

    with app.app_context():
        person = Person(
            full_name="Test User",
            email="test@example.com",
            password_hash="test",
            country="Italy",
        )
        assert person.country == "Italy"


def test_create_person_with_country(client, admin_user):
    """Test creating a person with country field."""
    client.post(
        "/login",
        data={"email": "admin@example.com", "password": "password123"},
        follow_redirects=True,
    )

    response = client.post(
        "/people/new",
        data={
            "full_name": "Mario Rossi",
            "email": "mario@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "country": "Italia",
            "is_active": True,
            "role": "user",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Persona creata" in response.data


def test_people_list_shows_country_column(client, admin_user):
    """Test that the people list page displays the country column."""
    client.post(
        "/login",
        data={"email": "admin@example.com", "password": "password123"},
        follow_redirects=True,
    )

    response = client.get("/people/")
    assert response.status_code == 200
    assert b"Paese" in response.data  # "Paese" is Italian for "Country"


def test_edit_person_with_country(client, admin_user, app):
    """Test editing a person's country field."""
    from app.extensions import db
    from app.models import Person

    client.post(
        "/login",
        data={"email": "admin@example.com", "password": "password123"},
        follow_redirects=True,
    )

    with app.app_context():
        # Create a test person
        person = Person(
            full_name="Test User",
            email="testuser@example.com",
            country="USA",
            role="user",
        )
        person.set_password("password123")
        db.session.add(person)
        db.session.commit()
        person_id = person.id

    # Edit the person's country
    response = client.post(
        f"/people/{person_id}/edit",
        data={
            "full_name": "Test User",
            "email": "testuser@example.com",
            "country": "Canada",
            "is_active": True,
            "role": "user",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Persona aggiornata" in response.data

    # Verify the country was updated
    with app.app_context():
        updated_person = Person.query.get(person_id)
        assert updated_person.country == "Canada"
