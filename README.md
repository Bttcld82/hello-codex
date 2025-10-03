

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
=======
- [Poetry](https://python-poetry.org/) **non necessario**: il progetto usa `pip` classico via `pyproject.toml`

## Setup locale

```bash
python -m venv .venv
source .venv/bin/activate  # oppure .venv\\Scripts\\activate su Windows
pip install -U pip
pip install -e .[dev]
```

Copia `.env.example` in `.env` se devi personalizzare la configurazione. In mancanza delle variabili d'ambiente il progetto usa un database SQLite in `instance/app.db` e una secret key di sviluppo.

## Avvio server di sviluppo

```bash
flask --app app_flask run --debug
```

Al primo avvio l'applicazione crea automaticamente le tabelle. Puoi anche forzare la creazione/ripristino via CLI:

```bash
flask --app app_flask init-db
```

Rotte disponibili:

- `GET /` → payload JSON di benvenuto
- `GET /projects` → elenco dei progetti presenti nel database

## Test

```bash
pytest
```

## Struttura progetto

- `app_flask/` → applicazione Flask, modelli e blueprint
- `tests/` → test Pytest
- `instance/` → directory creata runtime contenente il database SQLite

