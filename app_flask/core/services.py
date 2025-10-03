"""Service layer helpers for CRUD operations and aggregations."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from typing import TYPE_CHECKING, Any

from sqlalchemy import func
from sqlalchemy.orm import Query

from ..models import Person, Project, TimeEntry

if TYPE_CHECKING:
    from ..forms import FilterForm


@dataclass
class TimesheetFilters:
    start_date: date | None = None
    end_date: date | None = None
    project_id: int | None = None
    person_id: int | None = None
    include_inactive: bool = False

    @classmethod
    def from_form(cls, form: FilterForm) -> TimesheetFilters:
        return cls(
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            project_id=form.project_id.data or None,
            person_id=form.person_id.data or None,
            include_inactive=form.include_inactive.data,
        )


def _base_query(filters: TimesheetFilters) -> Query[TimeEntry]:
    query: Query[TimeEntry] = TimeEntry.query.join(TimeEntry.project).join(TimeEntry.person)

    if filters.start_date:
        query = query.filter(TimeEntry.date >= filters.start_date)
    if filters.end_date:
        query = query.filter(TimeEntry.date <= filters.end_date)
    if filters.project_id:
        query = query.filter(TimeEntry.project_id == filters.project_id)
    if filters.person_id:
        query = query.filter(TimeEntry.person_id == filters.person_id)
    if not filters.include_inactive:
        query = query.filter(Project.is_active.is_(True), Person.is_active.is_(True))

    return query


def default_period(app_config: dict[str, object]) -> tuple[date, date]:
    days = int(app_config.get("DEFAULT_DASHBOARD_RANGE_DAYS", 7))
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    return start_date, end_date


def get_dashboard_data(filters: TimesheetFilters) -> dict[str, Any]:
    query = _base_query(filters)

    total_hours_query = query.with_entities(func.coalesce(func.sum(TimeEntry.duration_hours), 0.0))
    total_hours = total_hours_query.scalar() or 0.0

    hours_by_project = (
        query.with_entities(Project.name, func.sum(TimeEntry.duration_hours))
        .group_by(Project.id)
        .order_by(func.sum(TimeEntry.duration_hours).desc())
        .limit(5)
        .all()
    )

    hours_by_person = (
        query.with_entities(Person.full_name, func.sum(TimeEntry.duration_hours))
        .group_by(Person.id)
        .order_by(func.sum(TimeEntry.duration_hours).desc())
        .all()
    )

    hours_by_day = (
        query.with_entities(TimeEntry.date, func.sum(TimeEntry.duration_hours))
        .group_by(TimeEntry.date)
        .order_by(TimeEntry.date.asc())
        .all()
    )

    return {
        "total_hours": float(total_hours),
        "hours_by_project": [(name, float(hours or 0)) for name, hours in hours_by_project],
        "hours_by_person": [(name, float(hours or 0)) for name, hours in hours_by_person],
        "hours_by_day": [(day, float(hours or 0)) for day, hours in hours_by_day],
    }


def get_timesheet_entries(filters: TimesheetFilters) -> Iterable[TimeEntry]:
    return _base_query(filters).order_by(TimeEntry.date.desc(), TimeEntry.start_time.asc())


def compute_total_cost(entries: Iterable[TimeEntry]) -> float:
    total = 0.0
    for entry in entries:
        if entry.person.hourly_rate:
            total += float(entry.person.hourly_rate) * entry.duration_hours
    return round(total, 2)


__all__ = [
    "TimesheetFilters",
    "default_period",
    "get_dashboard_data",
    "get_timesheet_entries",
    "compute_total_cost",
]
