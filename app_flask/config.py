"""Configuration objects for the Flask application."""

from __future__ import annotations

from os import getenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "instance" / "app.db"


def _default_database_uri() -> str:
    return f"sqlite:///{DEFAULT_DB_PATH}".replace("\\", "/")


class Config:
    """Base configuration suitable for local development."""

    SECRET_KEY = getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = getenv("DATABASE_URL", _default_database_uri())
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = getenv("SQLALCHEMY_ECHO", "0") == "1"
