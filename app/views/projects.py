"""Blueprint to manage projects CRUD."""
from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, url_for
from flask.typing import ResponseReturnValue
from flask_login import login_required

from ..auth import admin_required
from ..extensions import db
from ..forms import ProjectForm
from ..models import Project

bp = Blueprint("projects", __name__, url_prefix="/projects")


@bp.route("/")
@login_required
def list_projects() -> ResponseReturnValue:
    projects = Project.query.order_by(Project.name).all()
    return render_template("projects_list.html", projects=projects)


@bp.route("/new", methods=["GET", "POST"])
@admin_required
def create_project() -> ResponseReturnValue:
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            name=form.name.data,
            code=form.code.data,
            client=form.client.data,
            is_active=form.is_active.data,
        )
        db.session.add(project)
        db.session.commit()
        flash("Progetto creato", "success")
        return redirect(url_for("projects.list_projects"))
    return render_template("project_form.html", form=form, title="Nuovo progetto")


@bp.route("/<int:project_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_project(project_id: int) -> ResponseReturnValue:
    project = Project.query.get_or_404(project_id)
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        project.name = form.name.data
        project.code = form.code.data
        project.client = form.client.data
        project.is_active = form.is_active.data
        db.session.commit()
        flash("Progetto aggiornato", "success")
        return redirect(url_for("projects.list_projects"))
    return render_template("project_form.html", form=form, title="Modifica progetto")


@bp.route("/<int:project_id>/delete", methods=["POST"])
@admin_required
def delete_project(project_id: int) -> ResponseReturnValue:
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash("Progetto eliminato", "info")
    return redirect(url_for("projects.list_projects"))
