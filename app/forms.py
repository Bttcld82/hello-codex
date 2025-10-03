"""Forms used across the web application."""
from __future__ import annotations

from datetime import date

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    DecimalField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    TimeField,
)
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange, Optional, Regexp


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Length(max=255),
            Regexp(r"^[^@]+@[^@]+\.[^@]+$", message="Inserire un'email valida"),
        ],
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class ProjectForm(FlaskForm):
    name = StringField("Nome", validators=[DataRequired(), Length(max=120)])
    code = StringField("Codice", validators=[Optional(), Length(max=50)])
    client = StringField("Cliente", validators=[Optional(), Length(max=120)])
    is_active = BooleanField("Attivo", default=True)
    submit = SubmitField("Salva")


class PersonCreateForm(FlaskForm):
    full_name = StringField("Nome completo", validators=[DataRequired(), Length(max=120)])
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Length(max=255),
            Regexp(r"^[^@]+@[^@]+\.[^@]+$", message="Inserire un'email valida"),
        ],
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        "Conferma Password",
        validators=[DataRequired(), EqualTo("password")],
    )
    hourly_rate = DecimalField(
        "Tariffa oraria",
        validators=[Optional(), NumberRange(min=0)],
        places=2,
    )
    is_active = BooleanField("Attivo", default=True)
    role = SelectField(
        "Ruolo",
        choices=[("admin", "Admin"), ("user", "Utente")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Salva")


class PersonEditForm(FlaskForm):
    full_name = StringField("Nome completo", validators=[DataRequired(), Length(max=120)])
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Length(max=255),
            Regexp(r"^[^@]+@[^@]+\.[^@]+$", message="Inserire un'email valida"),
        ],
    )
    hourly_rate = DecimalField(
        "Tariffa oraria",
        validators=[Optional(), NumberRange(min=0)],
        places=2,
    )
    is_active = BooleanField("Attivo")
    role = SelectField(
        "Ruolo",
        choices=[("admin", "Admin"), ("user", "Utente")],
        validators=[DataRequired()],
    )
    password = PasswordField("Nuova password", validators=[Optional(), Length(min=8)])
    submit = SubmitField("Salva")


class TimeEntryForm(FlaskForm):
    project_id = SelectField("Progetto", coerce=int, validators=[DataRequired()])
    person_id = SelectField("Persona", coerce=int, validators=[DataRequired()])
    date = DateField("Data", default=date.today, validators=[DataRequired()])
    start_time = TimeField("Ora inizio", validators=[Optional()])
    end_time = TimeField("Ora fine", validators=[Optional()])
    duration_hours = DecimalField(
        "Durata ore",
        validators=[Optional(), NumberRange(min=0, message="La durata deve essere positiva")],
        places=2,
    )
    notes = TextAreaField("Note", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Salva")


class FilterForm(FlaskForm):
    start_date = DateField("Dal", validators=[Optional()])
    end_date = DateField("Al", validators=[Optional()])
    project_id = SelectField("Progetto", coerce=int, validators=[Optional()])
    person_id = SelectField("Persona", coerce=int, validators=[Optional()])
    include_inactive = BooleanField("Includi inattivi")
    submit = SubmitField("Applica filtri")
