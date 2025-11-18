

# instruction.md
Titolo: Crea un sito Flask + SQLite per il tracking ore di lavoro per progetto (multi-utente) con mini dashboard

## Obiettivo
Realizzare una web-app **Flask** con **SQLite** (unico DB) per registrare ore lavorate su progetti da più persone, con:
- CRUD di progetti, persone, time entries.
- Dashboard con riepiloghi (per periodo, progetto, persona).
- Export CSV.
- Setup semplice (Python only), avvio locale con `flask run`.
- Test automatici (pytest) e lint (ruff).

> Nota: preferire Python per calcoli/aggregazioni; frontend minimo (Jinja2 + un tocco di JS solo per i grafici).

---

## Requisiti funzionali
1. **Anagrafiche**
   - **Progetto**: `id`, `name` (unique), `code` (opz), `client` (opz), `is_active` (bool), `created_at`.
   - **Persona**: `id`, `full_name`, `email` (unique), `hourly_rate` (DECIMAL, opz), `is_active`, `created_at`.

2. **Time entry** (registrazione ore)
   - Campi: `id`, `project_id`, `person_id`, `date` (YYYY-MM-DD), `start_time` (HH:MM), `end_time` (HH:MM) **oppure** `duration_hours` (float, se non si usa start/end), `notes` (text).
   - **Regola**: se presenti `start_time` e `end_time`, calcola `duration_hours = (end - start)` lato server.
   - **Vincoli**:
     - `duration_hours > 0`.
     - `start_time < end_time` quando usati.
     - Progetto/persona devono essere attivi (o warning se non attivi).
   - **Opzionale**: prevenzione sovrapposizioni per stessa persona+data (warning + blocco se overlap).

3. **Dashboard**
   - Filtri: intervallo date (default settimana corrente), progetto, persona.
   - KPI:
     - Ore totali nel periodo.
     - Top 5 progetti per ore.
     - Ore per persona.
   - Grafici (server-side compute, client-side render con Chart.js minimale):
     - Barre: ore per progetto.
     - Linea: ore per giorno (nel periodo selezionato).
   - Tabelle di dettaglio con paginazione.

4. **Ricerca/filtri**
   - Vista “Timesheet” filtrabile per data/progetto/persona con tabella e pulsanti “Duplica riga”, “Elimina”.

5. **Export**
   - CSV delle time entries filtrate (stessi filtri della dashboard).

6. **Autenticazione (semplice)**
   - Login con email+password (Flask-Login). Ruoli base:
     - **admin**: CRUD pieno.
     - **user**: può creare/modificare/eliminare solo le proprie time entries; read su progetti e dashboard.

7. **UX minima**
   - Layout base: navbar (Dashboard, Timesheet, Progetti, Persone, Export, Login/Logout).
   - Form semplici (WTForms o Flask-WTF).
   - Validazioni chiare e messaggi flash.

---

## Stack tecnico
- Python 3.11+, Flask, Jinja2, Flask-Login, SQLAlchemy (ORM), SQLite (file `app.db`).
- Migrazioni: opzionale **alembic** (se semplice, si può iniziare senza).
- Test: `pytest` (+ `pytest-cov`).
- Lint/format: `ruff`.
- Chart: **Chart.js** (solo rendering; i dati arrivano già aggregati da Python).
- Template e static: Bootstrap minimale da CDN.

---

## Struttura progetto


.
├─ app/
│ ├─ init.py
│ ├─ extensions.py # db, login_manager, csrf
│ ├─ models.py # SQLAlchemy models
│ ├─ auth/ # blueprint auth
│ │ ├─ init.py
│ │ └─ routes.py
│ ├─ core/ # business logic / services
│ │ ├─ services.py # funzioni per CRUD e aggregation
│ │ └─ validators.py
│ ├─ views/ # blueprints ui
│ │ ├─ dashboard.py
│ │ ├─ timesheet.py
│ │ ├─ projects.py
│ │ └─ people.py
│ ├─ api/ (opzionale) # REST endpoints se servono
│ ├─ templates/
│ │ ├─ base.html
│ │ ├─ dashboard.html
│ │ ├─ timesheet_list.html
│ │ ├─ timeentry_form.html
│ │ ├─ projects_list.html
│ │ ├─ project_form.html
│ │ ├─ people_list.html
│ │ ├─ person_form.html
│ │ └─ auth_login.html
│ └─ static/
│ └─ (css/js)
├─ tests/
│ ├─ conftest.py
│ ├─ test_models.py
│ ├─ test_timesheet_routes.py
│ └─ test_dashboard_aggregations.py
├─ instance/ # .gitignored (config, app.db)
├─ .env.example
├─ requirements.txt
├─ pyproject.toml
├─ wsgi.py # per gunicorn (futuro)
└─ app.py # entrypoint flask dev


---

## Modelli (indicazione)
```python
# app/models.py (indicativo)
class Project(db.Model):
    id = ...
    name = db.Column(db.String(120), unique=True, nullable=False)
    code = db.Column(db.String(50))
    client = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

class Person(db.Model):
    id = ...
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))  # Flask-Login
    role = db.Column(db.String(20), default="user")  # user/admin
    hourly_rate = db.Column(db.Numeric(10,2))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

class TimeEntry(db.Model):
    id = ...
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time)   # opzionale
    end_time = db.Column(db.Time)     # opzionale
    duration_hours = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utcnow)


Logica di calcolo durata

Se start_time & end_time: calcolare duration_hours in services.py (convalidare >0).

Se si inserisce direttamente duration_hours: convalidare >0 e max 24.

Overlap check (opzionale)

In validators.py: query time entries della stessa persona+data, verificare intervalli.

Rotte richieste (minimo)

Auth: /login, /logout.

Dashboard: /dashboard?from=YYYY-MM-DD&to=YYYY-MM-DD&project_id=&person_id=

Ritorna: KPI + dataset per grafici (aggregati Python).

Timesheet

GET /timesheet lista filtrabile.

GET /timesheet/new, POST /timesheet/new (crea).

GET /timesheet/<id>/edit, POST (update).

POST /timesheet/<id>/delete.

Progetti

/projects, /projects/new, /projects/<id>/edit, /projects/<id>/delete.

Persone

/people, /people/new, /people/<id>/edit, /people/<id>/delete.

Export

/export.csv (rispetta filtri querystring).

Permessi

admin: pieno accesso CRUD.

user: CRUD limitato alle proprie time entries; read su dashboard/progetti/persone attive.

UI/Template

base.html: navbar con link principali, messaggi flash, blocchi content.

dashboard.html:

form filtri (from/to, progetto, persona).

3 KPI (ore totali, n. persone, n. progetti attivi nel periodo).

2 grafici Chart.js (bar per progetto, line per giorno).

tabella dettaglio (prime 20 righe con paginazione).

timesheet_list.html: tabella con azioni edit/delete, duplicazione riga.

form (WTForms): validazioni coerenti; dropdown progetti/persone attive.

Aggregazioni (Python)

Ore per progetto: SUM(duration_hours) GROUP BY project_id.

Ore per persona: SUM(duration_hours) GROUP BY person_id.

Serie giornaliera: SUM(duration_hours) GROUP BY date.

Periodo default: settimana corrente (Europe/Paris).

Validazioni & locale

Timezone: Europe/Paris.

Date in input: YYYY-MM-DD.

Arrotondamenti: duration_hours a 0.25h (opzionale, configurabile).

hourly_rate opzionale; se presente, calcolare costo totale in export (colonna extra).

Sicurezza e configurazione

Secret key da .env (caricare con python-dotenv).

CSRF abilitata sui form.

Password hash con werkzeug.security.

Ruoli enforced nei decorator/route.

Setup & comandi (da documentare in README)

Install:

python -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt


Init DB:

Minimal: creare tabelle via db.create_all() al primo avvio.

(Opz) Alembic: alembic init, alembic revision --autogenerate -m "init", alembic upgrade head.

Run:

export FLASK_APP=app.py
export FLASK_ENV=development
flask run


Test/Lint:

pytest -q --cov=app
ruff check .
ruff format .

Dipendenze minime (requirements.txt)

flask

flask-login

flask-wtf

sqlalchemy

flask-sqlalchemy

python-dotenv

pytest

pytest-cov

ruff

(Opzionali: alembic, email-validator per WTForms, gunicorn per deploy futuro.)

Criteri di accettazione (Definition of Done)

 Avvio locale senza errori, DB SQLite creato in instance/app.db.

 Login funzionante; seed utente admin via comando o script.

 CRUD completi per Progetti, Persone, Time entries con validazioni.

 Dashboard con KPI, 2 grafici, tabella filtrabile; calcoli server-side.

 Export CSV coerente con i filtri applicati.

 Test: copertura ≥ 85% per core/services.py (aggregazioni + validazioni).

 ruff check . senza errori (o solo warn giustificati).

 README con istruzioni di setup, uso e credenziali seed.

 Niente dipendenze DB esterne (solo SQLite).

Task iniziali per l’agente

Bootstrap progetto (struttura cartelle, config Flask/SQLite, blueprint).

Implementare modelli e migrazione iniziale (o create_all()).

Implementare autenticazione (Flask-Login) e seed admin.

Implementare CRUD Progetti/Persone/Time entries con form e validazioni.

Implementare aggregazioni Python e Dashboard (KPI + grafici).

Implementare Export CSV con filtri.

Aggiungere test tests/ per:

creazione time entry con calcolo durata

rilevazione overlap (se abilitata)

aggregazioni per progetto/persona/giorno

permessi (user vs admin)

Integrare ruff e pytest-cov; assicurare DoD.

Aprire PR con descrizione, checklist DoD, istruzioni run.
