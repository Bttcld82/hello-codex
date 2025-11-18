"""Dashboard blueprint with KPI aggregations."""

from __future__ import annotations

from flask import Blueprint, current_app, render_template, request
from flask.typing import ResponseReturnValue
from flask_login import login_required

from ..core.services import TimesheetFilters, default_period, get_dashboard_data
from ..forms import FilterForm
from ..models import Person, Project

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@bp.route("/")
@login_required
def index() -> ResponseReturnValue:
    form = FilterForm(request.args, meta={"csrf": False})

    projects = Project.query.order_by(Project.name).all()
    people = Person.query.order_by(Person.full_name).all()

    form.project_id.choices = [(0, "Tutti")] + [
        (project.id, project.name) for project in projects
    ]
    form.person_id.choices = [(0, "Tutti")] + [
        (person.id, person.full_name) for person in people
    ]

    if not form.start_date.data or not form.end_date.data:
        start, end = default_period(current_app.config)
        form.start_date.data = start
        form.end_date.data = end
    if form.project_id.data is None:
        form.project_id.data = 0
    if form.person_id.data is None:
        form.person_id.data = 0

    filters = TimesheetFilters.from_form(form)
    data = get_dashboard_data(filters)

    return render_template(
        "dashboard.html",
        form=form,
        filters=filters,
        data=data,
    )
