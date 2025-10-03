# Worktime Tracker

Applicazione web Flask + SQLite per registrare le ore lavorate sui progetti da parte di un team,
con gestione autenticata degli utenti, CRUD di progetti/persone/time entry, dashboard con KPI e
export CSV.

## Requisiti

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) - Modern Python package and project manager

## Setup ambiente di sviluppo

```bash
# Installa le dipendenze e crea l'environment virtuale
uv sync

# Oppure installa uv se non è già presente:
# pip install uv
```

## Configurazione

1. Copia `.env.example` in `.env` e personalizza almeno `SECRET_KEY`.
2. In assenza di `DATABASE_URI` verra utilizzato automaticamente `sqlite:///instance/app.db`.
3. Inizializza il database e crea un amministratore:

   ```bash
   uv run flask --app app.py init-db
   uv run python scripts/create_admin.py --email admin@example.com --password change-me
   ```

## Avvio in locale

```bash
# Avvia il server di sviluppo
uv run python app.py

# Oppure usando Flask direttamente
uv run flask --app app.py run --debug
```

La prima esecuzione crea la cartella `instance/` e il database SQLite se non presenti.

Credenziali di esempio (dopo il comando `create-admin`): `admin@example.com` / password scelta.

## Test e lint

```bash
# Esegui i test
uv run pytest --cov=app

# Lint del codice  
uv run ruff check .

# Format del codice
uv run ruff format .
```

## Struttura del progetto

```
.
app/                # package principale con blueprint, servizi e template
    __init__.py
    auth/
    core/
    forms.py
    models.py
    templates/
    views/
app.py              # entrypoint per `flask run`
scripts/            # script di utilità per setup e manutenzione
    create_admin.py # crea utenti amministratore
    seed_dummy_data.py # popola database con dati di test
instance/           # configurazioni locali e database SQLite (non versionato)
tests/              # suite pytest
pyproject.toml      # configurazione uv, dipendenze e tooling
uv.lock             # lock file per dipendenze esatte
```

## Script di utilità

```bash
# Crea un utente amministratore
uv run python scripts/create_admin.py --email admin@test.com --password 123

# Popola il database con dati di esempio  
uv run python scripts/seed_dummy_data.py
```
