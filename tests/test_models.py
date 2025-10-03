from __future__ import annotations

from datetime import date, time

import pytest
from app_flask.models import TimeEntry


def test_time_entry_update_duration(sample_project, admin_user):
    entry = TimeEntry(
        project=sample_project,
        person=admin_user,
        date=date(2024, 1, 1),
        start_time=time(9, 0),
        end_time=time(12, 30),
        duration_hours=0,
    )
    entry.update_duration()
    assert entry.duration_hours == pytest.approx(3.5)


def test_time_entry_update_duration_invalid(sample_project, admin_user):
    entry = TimeEntry(
        project=sample_project,
        person=admin_user,
        date=date(2024, 1, 1),
        start_time=time(10, 0),
        end_time=time(9, 0),
        duration_hours=0,
    )

    with pytest.raises(ValueError):
        entry.update_duration()
