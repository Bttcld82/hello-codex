#!/usr/bin/env python3
"""Utility script to create or update an admin user for local development."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add parent directory to sys.path to import app module
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from app.extensions import db
from app.models import Person


def create_admin_user(email: str, password: str, full_name: str) -> None:
    app = create_app()

    with app.app_context():
        person = Person.query.filter_by(email=email).first()

        if person is None:
            person = Person(
                full_name=full_name, email=email, role="admin", is_active=True
            )
            db.session.add(person)
            action = "created"
        else:
            person.full_name = full_name
            person.role = "admin"
            person.is_active = True
            action = "updated"

        person.set_password(password)
        db.session.commit()

        print(f"Admin user {action}: {email}")
        print("You can now sign in with the provided credentials.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or update an admin user.")
    parser.add_argument(
        "--email", default="admin@test.com", help="Email for the admin user"
    )
    parser.add_argument(
        "--password", default="change-me", help="Password for the admin user"
    )
    parser.add_argument(
        "--full-name", default="Administrator", help="Full name for the admin user"
    )
    args = parser.parse_args()

    create_admin_user(
        email=args.email, password=args.password, full_name=args.full_name
    )


if __name__ == "__main__":
    main()
