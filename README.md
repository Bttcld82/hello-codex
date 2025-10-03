# Worktime Tracker

Applicazione web Flask + SQLite per registrare le ore lavorate sui progetti da parte di un team,
con gestione autenticata degli utenti, CRUD di progetti/persone/time entry, dashboard con KPI e
export CSV.

## Requisiti

- Python 3.12+
- SQLite (incluso con Python)

## Setup ambiente di sviluppo

```bash
python -m venv .venv
source .venv/bin/activate  # Su Windows: .\.venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
```

## Configurazione

1. Copia `.env.example` in `.env` e personalizza almeno `SECRET_KEY`.
2. In assenza di `DATABASE_URI` verrà utilizzato automaticamente `sqlite:///instance/app.db`.
3. Inizializza il database e crea un amministratore:

   ```bash
   flask --app app.py init-db
   flask --app app.py create-admin --email admin@example.com --password change-me
   ```

## Avvio in locale

```bash
flask --app app.py run --debug
```

La prima esecuzione crea la cartella `instance/` e il database SQLite se non presenti.

Credenziali di esempio (dopo il comando `create-admin`): `admin@example.com` / password scelta.

## Test e lint

```bash
pytest --cov=app
ruff check .
```

## Struttura del progetto

```
.
├── app/
│   ├── __init__.py        # factory Flask e registrazione blueprint/CLI
│   ├── auth/              # autenticazione e decorators
│   ├── core/              # servizi di dominio e validatori
│   ├── forms.py           # WTForms per le viste
│   ├── models.py          # modelli SQLAlchemy
│   ├── templates/         # template Jinja2 (Bootstrap + Chart.js)
│   └── views/             # blueprint UI (dashboard, timesheet, progetti, persone)
├── app.py                 # entrypoint per `flask run`
├── instance/              # configurazioni locali e SQLite DB (non versionato)
├── requirements.txt       # dipendenze base e strumenti dev
├── tests/                 # test pytest (fixtures e copertura funzionale)
└── pyproject.toml         # configurazione tooling (ruff, pytest, coverage)
```
