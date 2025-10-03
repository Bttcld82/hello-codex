"""Application factory and extension registration for the worktime tracker app."""
from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import click
from dotenv import load_dotenv
from flask import Flask, redirect, url_for
from flask.typing import ResponseReturnValue

from .extensions import csrf, db, login_manager

if TYPE_CHECKING:
    from .models import Person


def register_blueprints(app: Flask) -> None:
    from .auth.routes import bp as auth_bp
    from .views.dashboard import bp as dashboard_bp
    from .views.people import bp as people_bp
    from .views.projects import bp as projects_bp
    from .views.timesheet import bp as timesheet_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(people_bp)
    app.register_blueprint(timesheet_bp)


def configure_shell_context(app: Flask) -> None:
    from . import models

    @app.shell_context_processor
    def _make_shell_context() -> dict[str, object]:
        return {
            "db": db,
            "Project": models.Project,
            "Person": models.Person,
            "TimeEntry": models.TimeEntry,
        }


def register_cli_commands(app: Flask) -> None:
    from .models import Person

    @app.cli.command("init-db")
    def init_db_command() -> None:
        """Create database tables."""

        db.create_all()
        click.echo("Initialized the database.")

    @app.cli.command("create-admin")
    @click.option("--email", prompt=True)
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    @click.option("--full-name", default="Administrator", show_default=True)
    def create_admin(email: str, password: str, full_name: str) -> None:
        """Create an admin user if the email is not already taken."""

        if Person.query.filter_by(email=email).first():
            click.echo("Admin already exists; aborting.")
            return

        person = Person(full_name=full_name, email=email, role="admin", is_active=True)
        person.set_password(password)
        db.session.add(person)
        db.session.commit()
        click.echo(f"Created admin user {email}")


def register_routes(app: Flask) -> None:
    @app.route("/")
    def index() -> ResponseReturnValue:
        return redirect(url_for("dashboard.index"))


def create_app(config_object: str | None = None) -> Flask:
    """Create and configure the Flask application instance."""

    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)

    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)

    default_db_path = instance_path / "app.db"

    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URI", f"sqlite:///{default_db_path}"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        DEFAULT_DASHBOARD_RANGE_DAYS=7,
    )

    app.config.from_pyfile("config.py", silent=True)
    if config_object:
        app.config.from_object(config_object)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str) -> Person | None:
        from .models import Person

        return Person.query.get(int(user_id))

    register_blueprints(app)
    register_routes(app)
    register_cli_commands(app)
    configure_shell_context(app)

    return app


__all__ = ["create_app", "db", "login_manager", "csrf"]
