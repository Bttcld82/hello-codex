"""Extension instances used across the Flask project."""

from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy


db: SQLAlchemy = SQLAlchemy()
