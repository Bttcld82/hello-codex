"""Authentication routes for login/logout."""
from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue
from flask_login import current_user, login_required, login_user, logout_user

from ..forms import LoginForm
from ..models import Person

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login() -> ResponseReturnValue:
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = Person.query.filter_by(email=form.email.data.lower()).first()
        if not user or not user.check_password(form.password.data):
            flash("Credenziali non valide", "danger")
        elif not user.is_active:
            flash("L'utente è disattivato", "warning")
        else:
            login_user(user)
            flash("Accesso effettuato", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("dashboard.index"))

    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout() -> ResponseReturnValue:
    logout_user()
    flash("Logout effettuato", "info")
    return redirect(url_for("auth.login"))
