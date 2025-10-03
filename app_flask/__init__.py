"""Application factory for the hello-codex Flask project."""

from __future__ import annotations

from pathlib import Path
import click
from flask import Flask

from .config import Config
from .extensions import db
from .routes import bp as main_blueprint

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_PATH = BASE_DIR / "instance"


def create_app(config_object: type[Config] | Config | None = None) -> Flask:
    """Create and configure a :class:`flask.Flask` application instance."""
    app = Flask(__name__, instance_path=str(INSTANCE_PATH))
    app.config.from_object(config_object or Config)

    INSTANCE_PATH.mkdir(parents=True, exist_ok=True)

    db.init_app(app)

    register_blueprints(app)
    register_cli(app)

    with app.app_context():
        db.create_all()

    return app


def register_blueprints(app: Flask) -> None:
    """Attach application blueprints."""
    app.register_blueprint(main_blueprint)


def register_cli(app: Flask) -> None:
    """Register custom Flask CLI commands."""

    @app.cli.command("init-db")
    def init_db_command() -> None:
        """Initialise the SQLite database with the configured models."""
        with app.app_context():
            db.create_all()
        click.secho("Database initialised.", fg="green")
