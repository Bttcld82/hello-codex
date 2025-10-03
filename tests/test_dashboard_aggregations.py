from __future__ import annotations

from datetime import date

from app.core.services import TimesheetFilters, get_dashboard_data
from app.extensions import db
from app.models import TimeEntry


def test_dashboard_summary(app, sample_project, admin_user, regular_user):
    entry1 = TimeEntry(
        project=sample_project,
        person=admin_user,
        date=date(2024, 1, 1),
        duration_hours=4,
    )
    entry2 = TimeEntry(
        project=sample_project,
        person=regular_user,
        date=date(2024, 1, 2),
        duration_hours=3,
    )
    db.session.add_all([entry1, entry2])
    db.session.commit()

    filters = TimesheetFilters(start_date=date(2023, 12, 31), end_date=date(2024, 1, 5))
    data = get_dashboard_data(filters)

    assert data["total_hours"] == 7
    assert data["hours_by_project"][0][1] == 7
    assert len(data["hours_by_person"]) == 2
    assert len(data["hours_by_day"]) == 2
