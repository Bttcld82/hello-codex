"""Timesheet management blueprint."""

from __future__ import annotations

import csv
from io import StringIO

from flask import (
    Blueprint,
    Response,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask.typing import ResponseReturnValue
from flask_login import current_user, login_required

from ..core import services
from ..core.validators import (
    ValidationProblem,
    compute_duration,
    ensure_entities_active,
    ensure_no_overlap,
)
from ..extensions import db
from ..forms import FilterForm, TimeEntryForm
from ..models import Person, Project, TimeEntry

bp = Blueprint("timesheet", __name__, url_prefix="/timesheet")


def _set_filter_choices(form: FilterForm) -> None:
    projects = Project.query.order_by(Project.name).all()
    people = Person.query.order_by(Person.full_name).all()

    form.project_id.choices = [(0, "Tutti")] + [
        (project.id, project.name) for project in projects
    ]
    form.person_id.choices = [(0, "Tutti")] + [
        (person.id, person.full_name) for person in people
    ]

    if form.project_id.data is None:
        form.project_id.data = 0
    if form.person_id.data is None:
        form.person_id.data = 0


def _set_time_entry_choices(
    form: TimeEntryForm, *, include_inactive: bool = False
) -> None:
    projects_query = Project.query
    people_query = Person.query
    if not include_inactive:
        projects_query = projects_query.filter_by(is_active=True)
        people_query = people_query.filter_by(is_active=True)

    projects = projects_query.order_by(Project.name).all()
    people = people_query.order_by(Person.full_name).all()

    form.project_id.choices = [(project.id, project.name) for project in projects]

    if current_user.role == "admin":
        form.person_id.choices = [(person.id, person.full_name) for person in people]
    else:
        form.person_id.choices = [(current_user.id, current_user.full_name)]
        form.person_id.data = current_user.id


@bp.route("/", methods=["GET"])
@login_required
def list_entries() -> ResponseReturnValue:
    form = FilterForm(request.args, meta={"csrf": False})
    _set_filter_choices(form)

    if current_user.role != "admin":
        form.person_id.data = current_user.id

    filters = services.TimesheetFilters.from_form(form)
    entries = services.get_timesheet_entries(filters).all()
    total_cost = services.compute_total_cost(entries)

    return render_template(
        "timesheet_list.html",
        form=form,
        entries=entries,
        total_cost=total_cost,
        filters=filters,
    )


@bp.route("/new", methods=["GET", "POST"])
@login_required
def create_entry() -> ResponseReturnValue:
    form = TimeEntryForm()
    _set_time_entry_choices(form)

    if form.validate_on_submit():
        project = Project.query.get_or_404(form.project_id.data)
        person = Person.query.get_or_404(form.person_id.data)

        try:
            ensure_entities_active(project, person)
            duration = compute_duration(
                form.date.data,
                form.start_time.data,
                form.end_time.data,
                form.duration_hours.data,
            )
            ensure_no_overlap(
                person_id=person.id,
                entry_date=form.date.data,
                start=form.start_time.data,
                end=form.end_time.data,
            )
        except ValidationProblem as exc:
            flash(str(exc), "danger")
        else:
            entry = TimeEntry(
                project=project,
                person=person,
                date=form.date.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                duration_hours=duration,
                notes=form.notes.data,
            )
            db.session.add(entry)
            db.session.commit()
            flash("Voce registrata", "success")
            return redirect(url_for("timesheet.list_entries"))

    return render_template(
        "timeentry_form.html", form=form, title="Nuova registrazione"
    )


@bp.route("/<int:entry_id>/edit", methods=["GET", "POST"])
@login_required
def edit_entry(entry_id: int) -> ResponseReturnValue:
    entry = TimeEntry.query.get_or_404(entry_id)
    if current_user.role != "admin" and entry.person_id != current_user.id:
        abort(403)

    form = TimeEntryForm(obj=entry)
    _set_time_entry_choices(form, include_inactive=True)

    if current_user.role != "admin":
        form.person_id.choices = [(current_user.id, current_user.full_name)]
        form.person_id.data = current_user.id

    if form.validate_on_submit():
        project = Project.query.get_or_404(form.project_id.data)
        person = Person.query.get_or_404(form.person_id.data)
        try:
            ensure_entities_active(project, person)
            duration = compute_duration(
                form.date.data,
                form.start_time.data,
                form.end_time.data,
                form.duration_hours.data,
            )
            ensure_no_overlap(
                person_id=person.id,
                entry_date=form.date.data,
                start=form.start_time.data,
                end=form.end_time.data,
                exclude_id=entry.id,
            )
        except ValidationProblem as exc:
            flash(str(exc), "danger")
        else:
            entry.project = project
            entry.person = person
            entry.date = form.date.data
            entry.start_time = form.start_time.data
            entry.end_time = form.end_time.data
            entry.duration_hours = duration
            entry.notes = form.notes.data
            db.session.commit()
            flash("Voce aggiornata", "success")
            return redirect(url_for("timesheet.list_entries"))

    return render_template(
        "timeentry_form.html", form=form, title="Modifica registrazione"
    )


@bp.route("/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete_entry(entry_id: int) -> ResponseReturnValue:
    entry = TimeEntry.query.get_or_404(entry_id)
    if current_user.role != "admin" and entry.person_id != current_user.id:
        abort(403)

    db.session.delete(entry)
    db.session.commit()
    flash("Voce eliminata", "info")
    return redirect(url_for("timesheet.list_entries"))


@bp.route("/<int:entry_id>/duplicate", methods=["POST"])
@login_required
def duplicate_entry(entry_id: int) -> ResponseReturnValue:
    entry = TimeEntry.query.get_or_404(entry_id)
    if current_user.role != "admin" and entry.person_id != current_user.id:
        abort(403)

    duplicate = TimeEntry(
        project=entry.project,
        person=entry.person,
        date=entry.date,
        start_time=entry.start_time,
        end_time=entry.end_time,
        duration_hours=entry.duration_hours,
        notes=entry.notes,
    )
    db.session.add(duplicate)
    db.session.commit()
    flash("Voce duplicata", "success")
    return redirect(url_for("timesheet.list_entries"))


@bp.route("/export", methods=["GET"])
@login_required
def export_csv() -> ResponseReturnValue:
    form = FilterForm(request.args, meta={"csrf": False})
    _set_filter_choices(form)

    if current_user.role != "admin":
        form.person_id.data = current_user.id

    filters = services.TimesheetFilters.from_form(form)
    entries = services.get_timesheet_entries(filters).all()

    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "Data",
            "Progetto",
            "Persona",
            "Ore",
            "Ora inizio",
            "Ora fine",
            "Note",
            "Costo",
        ]
    )

    for entry in entries:
        rate = float(entry.person.hourly_rate or 0)
        cost = rate * entry.duration_hours if rate else 0
        writer.writerow(
            [
                entry.date.isoformat(),
                entry.project.name,
                entry.person.full_name,
                f"{entry.duration_hours:.2f}",
                entry.start_time.strftime("%H:%M") if entry.start_time else "",
                entry.end_time.strftime("%H:%M") if entry.end_time else "",
                entry.notes or "",
                f"{cost:.2f}" if cost else "",
            ]
        )

    response = Response(buffer.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=timesheet.csv"
    return response
