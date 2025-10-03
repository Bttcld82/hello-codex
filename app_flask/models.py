"""Database models for the hello-codex application."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .extensions import db


class Project(db.Model):
    """Simple project entity used for bootstrapping the database schema."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC), nullable=False)

    def __repr__(self) -> str:  # pragma: no cover - for debugging only
        return f"<Project id={self.id!r} name={self.name!r}>"
