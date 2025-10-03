#!/usr/bin/env python3
"""Populate the development database with deterministic demo data."""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

# Add parent directory to sys.path to import app module
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from app.extensions import db
from app.models import Person, Project, TimeEntry


PROJECTS = [
    {
        "name": "Banco Prova Publiacqua",
        "code": "BPP",
        "client": "Publiacqua",
    },
    {
        "name": "Progetto X",
        "code": "PROJX",
        "client": "Client X",
    },
    {
        "name": "Integrazione ERP",
        "code": "ERP-INT",
        "client": "Tech Solutions",
    },
]

PEOPLE = [
    {
        "full_name": "Administrator",
        "email": "admin@example.com",
        "password": "change-me",
        "role": "admin",
        "hourly_rate": 80.0,
    },
    {
        "full_name": "Bettinelli Claudio",
        "email": "claudio@example.com",
        "password": "password123",
        "role": "user",
        "hourly_rate": 60.0,
    },
    {
        "full_name": "Giulia Rossi",
        "email": "giulia@example.com",
        "password": "password123",
        "role": "user",
        "hourly_rate": 55.0,
    },
]


TIME_ENTRIES = [
    {"project": "Banco Prova Publiacqua", "person": "Administrator", "days_ago": 2, "hours": 4.0, "notes": "Setup ambiente di test"},
    {"project": "Banco Prova Publiacqua", "person": "Bettinelli Claudio", "days_ago": 1, "hours": 5.0, "notes": "Sviluppo feature dashboard"},
    {"project": "Progetto X", "person": "Giulia Rossi", "days_ago": 3, "hours": 3.5, "notes": "Analisi requisiti"},
    {"project": "Progetto X", "person": "Bettinelli Claudio", "days_ago": 4, "hours": 2.0, "notes": "Bug fixing"},
    {"project": "Integrazione ERP", "person": "Giulia Rossi", "days_ago": 0, "hours": 6.5, "notes": "Workshop con il cliente"},
]


def seed() -> None:
    app = create_app()

    with app.app_context():
        projects_by_name: dict[str, Project] = {}
        for project_data in PROJECTS:
            project = Project.query.filter_by(name=project_data["name"]).first()
            if project is None:
                project = Project(
                    name=project_data["name"],
                    code=project_data["code"],
                    client=project_data["client"],
                    is_active=True,
                )
                db.session.add(project)
            projects_by_name[project.name] = project

        people_by_name: dict[str, Person] = {}
        for person_data in PEOPLE:
            person = Person.query.filter_by(email=person_data["email"]).first()
            if person is None:
                person = Person(
                    full_name=person_data["full_name"],
                    email=person_data["email"],
                    role=person_data["role"],
                    is_active=True,
                    hourly_rate=person_data["hourly_rate"],
                )
                db.session.add(person)
            else:
                person.full_name = person_data["full_name"]
                person.role = person_data["role"]
                person.is_active = True
                person.hourly_rate = person_data["hourly_rate"]

            if person_data.get("password"):
                person.set_password(person_data["password"])
            people_by_name[person.full_name] = person

        db.session.flush()

        for entry in TIME_ENTRIES:
            project = projects_by_name[entry["project"]]
            person = people_by_name[entry["person"]]
            entry_date = date.today() - timedelta(days=entry["days_ago"])

            existing = TimeEntry.query.filter_by(
                project_id=project.id,
                person_id=person.id,
                date=entry_date,
                notes=entry["notes"],
            ).first()
            if existing:
                existing.duration_hours = entry["hours"]
            else:
                db.session.add(
                    TimeEntry(
                        project=project,
                        person=person,
                        date=entry_date,
                        duration_hours=entry["hours"],
                        notes=entry["notes"],
                    )
                )

        db.session.commit()
        print("Seed data inserted successfully.")
        print(f"Projects: {Project.query.count()} | People: {Person.query.count()} | Time entries: {TimeEntry.query.count()}")


if __name__ == "__main__":
    seed()
