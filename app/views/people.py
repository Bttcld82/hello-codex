"""Blueprint for managing people records."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, url_for
from flask.typing import ResponseReturnValue
from flask_login import login_required

from ..auth import admin_required
from ..extensions import db
from ..forms import PersonCreateForm, PersonEditForm
from ..models import Person

bp = Blueprint("people", __name__, url_prefix="/people")


@bp.route("/")
@login_required
def list_people() -> ResponseReturnValue:
    people = Person.query.order_by(Person.full_name).all()
    return render_template("people_list.html", people=people)


@bp.route("/new", methods=["GET", "POST"])
@admin_required
def create_person() -> ResponseReturnValue:
    form = PersonCreateForm()
    if form.validate_on_submit():
        if Person.query.filter_by(email=form.email.data.lower()).first():
            flash("Email già registrata", "danger")
        else:
            person = Person(
                full_name=form.full_name.data,
                email=form.email.data.lower(),
                hourly_rate=form.hourly_rate.data,
                is_active=form.is_active.data,
                role=form.role.data,
            )
            person.set_password(form.password.data)
            db.session.add(person)
            db.session.commit()
            flash("Persona creata", "success")
            return redirect(url_for("people.list_people"))
    return render_template("person_form.html", form=form, title="Nuova persona")


@bp.route("/<int:person_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_person(person_id: int) -> ResponseReturnValue:
    person = Person.query.get_or_404(person_id)
    form = PersonEditForm(obj=person)
    if form.validate_on_submit():
        existing = Person.query.filter(
            Person.email == form.email.data.lower(),
            Person.id != person.id,
        ).first()
        if existing:
            flash("Email già registrata", "danger")
        else:
            person.full_name = form.full_name.data
            person.email = form.email.data.lower()
            person.hourly_rate = form.hourly_rate.data
            person.is_active = form.is_active.data
            person.role = form.role.data
            if form.password.data:
                person.set_password(form.password.data)
            db.session.commit()
            flash("Persona aggiornata", "success")
            return redirect(url_for("people.list_people"))
    return render_template("person_form.html", form=form, title="Modifica persona")


@bp.route("/<int:person_id>/delete", methods=["POST"])
@admin_required
def delete_person(person_id: int) -> ResponseReturnValue:
    person = Person.query.get_or_404(person_id)
    db.session.delete(person)
    db.session.commit()
    flash("Persona eliminata", "info")
    return redirect(url_for("people.list_people"))
