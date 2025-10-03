"""Application factory and extension initialization for the worktime tracker app."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

# Initialize extensions without app context; they will be bound in ``create_app``.
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_object: str | None = None) -> Flask:
    """Create and configure the Flask application instance.

    Parameters
    ----------
    config_object:
        Optional dotted path to a configuration object or class that should be loaded
        after the default configuration.
    """
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)

    # Ensure the instance folder exists for the SQLite database and config overrides.
    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)

    default_db_path = instance_path / "app.db"

    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URI", f"sqlite:///{default_db_path}"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Allow optional config override from file or explicit object.
    app.config.from_pyfile("config.py", silent=True)
    if config_object:
        app.config.from_object(config_object)

    # Bind Flask extensions.
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints here when they become available.
    from . import models  # noqa: F401  # Ensure models are imported for metadata.

    return app


__all__ = ["create_app", "db", "login_manager", "csrf"]
