"""Migration script to add password reset fields to the people table."""

from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from app.extensions import db


def migrate() -> None:
    """Add reset_token and reset_token_expiry columns to people table."""
    app = create_app()

    with app.app_context():
        # Check if columns already exist
        inspector = db.inspect(db.engine)
        columns = [col["name"] for col in inspector.get_columns("people")]

        if "reset_token" in columns and "reset_token_expiry" in columns:
            print("Migration already applied - columns exist")
            return

        # Add the new columns using raw SQL
        with db.engine.connect() as conn:
            if "reset_token" not in columns:
                conn.execute(
                    db.text("ALTER TABLE people ADD COLUMN reset_token VARCHAR(100)")
                )
                print("Added reset_token column")

            if "reset_token_expiry" not in columns:
                conn.execute(
                    db.text("ALTER TABLE people ADD COLUMN reset_token_expiry DATETIME")
                )
                print("Added reset_token_expiry column")

            conn.commit()

        print("Migration completed successfully")


if __name__ == "__main__":
    migrate()
