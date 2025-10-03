"""Domain validation helpers for time entry management."""
from __future__ import annotations

from datetime import date, datetime, time

from ..models import Person, Project, TimeEntry


class ValidationProblem(ValueError):
    """Raised when domain validation fails."""


def ensure_entities_active(project: Project, person: Person) -> None:
    if not project.is_active:
        raise ValidationProblem("Il progetto selezionato non è attivo.")
    if not person.is_active:
        raise ValidationProblem("La persona selezionata non è attiva.")


def compute_duration(
    entry_date: date,
    start: time | None,
    end: time | None,
    duration_hours: float | None,
) -> float:
    if start and end:
        start_dt = datetime.combine(entry_date, start)
        end_dt = datetime.combine(entry_date, end)
        delta = end_dt - start_dt
        if delta.total_seconds() <= 0:
            raise ValidationProblem("L'ora di fine deve essere successiva all'inizio.")
        return delta.total_seconds() / 3600

    if duration_hours is None:
        raise ValidationProblem("Specificare una durata o l'intervallo orario.")

    if duration_hours <= 0:
        raise ValidationProblem("La durata deve essere positiva.")

    return float(duration_hours)


def ensure_no_overlap(
    person_id: int,
    entry_date: date,
    start: time | None,
    end: time | None,
    *,
    exclude_id: int | None = None,
) -> None:
    if not (start and end):
        return

    overlap_query = TimeEntry.query.filter(
        TimeEntry.person_id == person_id,
        TimeEntry.date == entry_date,
    )
    if exclude_id:
        overlap_query = overlap_query.filter(TimeEntry.id != exclude_id)

    def _to_minutes(value: time) -> int:
        return value.hour * 60 + value.minute

    start_minutes = _to_minutes(start)
    end_minutes = _to_minutes(end)

    for existing in overlap_query:
        if not (existing.start_time and existing.end_time):
            continue
        existing_start = _to_minutes(existing.start_time)
        existing_end = _to_minutes(existing.end_time)
        if start_minutes < existing_end and end_minutes > existing_start:
            raise ValidationProblem("Esiste già una registrazione sovrapposta per questa persona.")


__all__ = [
    "ValidationProblem",
    "ensure_entities_active",
    "compute_duration",
    "ensure_no_overlap",
]
