"""Authentication routes for login/logout."""
from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue
from flask_login import current_user, login_required, login_user, logout_user

from ..extensions import db
from ..forms import LoginForm, RequestPasswordResetForm, ResetPasswordForm
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


@bp.route("/request-password-reset", methods=["GET", "POST"])
def request_password_reset() -> ResponseReturnValue:
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = Person.query.filter_by(email=form.email.data.lower()).first()
        if user and user.is_active:
            token = user.generate_reset_token()
            db.session.commit()
            
            # In a real application, this would send an email with the reset link
            # For now, we'll display the reset link directly to the user
            reset_url = url_for("auth.reset_password", token=token, _external=True)
            flash(
                f"Link di reset generato. In un'applicazione reale, questo verrebbe inviato via email. "
                f"Per ora, usa questo link: {reset_url}",
                "info"
            )
        else:
            # Don't reveal if the email exists or not for security
            flash(
                "Se l'email esiste nel sistema, riceverai un link per reimpostare la password.",
                "info"
            )
        return redirect(url_for("auth.login"))

    return render_template("auth/request_password_reset.html", form=form)


@bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token: str) -> ResponseReturnValue:
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    user = Person.query.filter_by(reset_token=token).first()
    if not user or not user.verify_reset_token(token):
        flash("Link di reset non valido o scaduto", "danger")
        return redirect(url_for("auth.login"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.clear_reset_token()
        db.session.commit()
        flash("Password reimpostata con successo. Ora puoi effettuare il login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form, token=token)
