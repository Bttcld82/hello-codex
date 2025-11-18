"""Database models for the worktime tracker application."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
import secrets

from flask_login import UserMixin
from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class TimestampMixin:
    """Reusable mixin that stores creation timestamp."""

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )


class Project(TimestampMixin, db.Model):
    """A client project that can receive tracked time entries."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    code: Mapped[str | None] = mapped_column(db.String(50))
    client: Mapped[str | None] = mapped_column(db.String(120))
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    time_entries: Mapped[list[TimeEntry]] = relationship(back_populates="project")

    def __repr__(self) -> str:  # pragma: no cover - repr helper
        return f"<Project id={self.id} name={self.name!r}>"


class Person(UserMixin, TimestampMixin, db.Model):
    """Team member that can log time against projects."""

    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(db.String(120), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(255), nullable=False)
    hourly_rate: Mapped[float | None] = mapped_column(db.Numeric(10, 2))
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    role: Mapped[str] = mapped_column(db.String(20), default="user", nullable=False)
    reset_token: Mapped[str | None] = mapped_column(db.String(100))
    reset_token_expiry: Mapped[datetime | None] = mapped_column(db.DateTime)

    time_entries: Mapped[list[TimeEntry]] = relationship(back_populates="person")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self) -> str:
        """Generate a secure password reset token."""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token

    def verify_reset_token(self, token: str) -> bool:
        """Verify if the reset token is valid and not expired."""
        if not self.reset_token or not self.reset_token_expiry:
            return False
        if self.reset_token != token:
            return False
        if datetime.utcnow() > self.reset_token_expiry:
            return False
        return True

    def clear_reset_token(self) -> None:
        """Clear the reset token after successful password reset."""
        self.reset_token = None
        self.reset_token_expiry = None

    def __repr__(self) -> str:  # pragma: no cover - repr helper
        return f"<Person id={self.id} email={self.email!r}>"


class TimeEntry(TimestampMixin, db.Model):
    """Tracked block of work attributed to a project and person."""

    __tablename__ = "time_entries"
    __table_args__ = (
        CheckConstraint("duration_hours > 0", name="ck_time_entries_duration_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id"), nullable=False)
    date: Mapped[date] = mapped_column(db.Date, default=date.today, nullable=False)
    start_time: Mapped[time | None] = mapped_column(db.Time)
    end_time: Mapped[time | None] = mapped_column(db.Time)
    duration_hours: Mapped[float] = mapped_column(db.Float, nullable=False)
    notes: Mapped[str | None] = mapped_column(db.Text)

    project: Mapped[Project] = relationship(back_populates="time_entries")
    person: Mapped[Person] = relationship(back_populates="time_entries")

    def update_duration(self) -> None:
        """Compute ``duration_hours`` from ``start_time``/``end_time`` when available."""

        if self.start_time and self.end_time:
            start_dt = datetime.combine(self.date, self.start_time)
            end_dt = datetime.combine(self.date, self.end_time)
            delta = end_dt - start_dt
            if delta <= timedelta(0):
                msg = "end_time must be after start_time"
                raise ValueError(msg)
            self.duration_hours = delta.total_seconds() / 3600

    def __repr__(self) -> str:  # pragma: no cover - repr helper
        return (
            f"<TimeEntry id={self.id} project_id={self.project_id} "
            f"person_id={self.person_id}>"
        )


__all__ = ["Project", "Person", "TimeEntry"]
