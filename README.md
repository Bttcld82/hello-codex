# hello-codex

Bootstrap project Flask + SQLite per demo Codex.

## Requisiti

- Python 3.12+
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
