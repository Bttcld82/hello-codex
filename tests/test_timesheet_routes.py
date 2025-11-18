from __future__ import annotations

from datetime import date

import pytest
from app.extensions import db
from app.models import TimeEntry


def test_create_entry_calculates_duration(
    client, login, admin_user, regular_user, sample_project
):
    login(admin_user.email, "password123")
    response = client.post(
        "/timesheet/new",
        data={
            "project_id": sample_project.id,
            "person_id": regular_user.id,
            "date": "2024-01-01",
            "start_time": "09:00",
            "end_time": "11:30",
            "notes": "Pair programming",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    entry = TimeEntry.query.filter_by(notes="Pair programming").first()
    assert entry is not None
    assert entry.duration_hours == pytest.approx(2.5)


def test_user_cannot_edit_other_entry(
    client, login, admin_user, regular_user, sample_project
):
    # Create entry for admin user
    entry = TimeEntry(
        project=sample_project,
        person=admin_user,
        date=date(2024, 1, 1),
        duration_hours=2,
    )
    db.session.add(entry)
    db.session.commit()

    login(regular_user.email, "password123")
    response = client.get(f"/timesheet/{entry.id}/edit")
    assert response.status_code == 403
