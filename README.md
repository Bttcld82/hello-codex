# Worktime Tracker

Progetto Flask + SQLite per tracciare le ore lavorate su progetti da parte di più utenti.
Questa versione iniziale fornisce la struttura di base dell'applicazione, pronta per essere
estesa con blueprint, servizi e dashboard.

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

1. Copia `.env.example` in `.env` (se presente) oppure definisci le variabili `SECRET_KEY`
   e `DATABASE_URI` nel tuo ambiente.
2. In assenza di `DATABASE_URI` verrà utilizzato automaticamente `instance/app.db`.

## Avvio in locale

```bash
export FLASK_APP=app.py
flask run --debug
```

La prima esecuzione crea automaticamente la cartella `instance/` e il database SQLite se non
esistono.

## Test e lint

```bash
pytest
ruff check .
```

## Struttura del progetto

```
.
├── app/
│   ├── __init__.py        # factory Flask e inizializzazione estensioni
│   └── models.py          # modelli SQLAlchemy
├── app.py                 # entrypoint per `flask run`
├── instance/              # configurazioni locali e SQLite DB (non versionato)
├── requirements.txt       # dipendenze base e strumenti dev
├── tests/                 # test pytest (da implementare)
└── pyproject.toml         # configurazione tooling (ruff, pytest, coverage)
```

Aggiungi blueprint, template, logica di business e test nelle rispettive cartelle per
completare le funzionalità descritte in `instruction.md`.
