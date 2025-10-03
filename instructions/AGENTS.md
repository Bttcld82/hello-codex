# AGENTS.md

## Project overview
- Linguaggi: Python 3.11+
- Stack tipico: Flask + SQLAlchemy + SQLite (dev) / PostgreSQL (prod)
- Cartelle chiave:
  - `app/` (app, blueprint, services)
  - `analyzers/` (statistica/metrologia)
  - `tests/` (pytest)
  - `migrations/` (Alembic, se presente)
  - `infra/` (docker, compose, CI)
- Obiettivo: codice pulito, testato, riproducibile, pronto per PT/17025.

## Setup commands
- Creazione venv:
  - Linux/macOS: `python -m venv .venv && . .venv/bin/activate`
  - Windows: `python -m venv .venv && .\\.venv\\Scripts\\activate`
- Install deps: `pip install -U pip && pip install -r requirements.txt`
- Env file: copia `.env.example` -> `.env`
- DB dev (se Alembic): `alembic upgrade head`
- Pre-commit (opz.): `pre-commit install`

## Run commands
- Dev server: `flask --app app run --debug`
- Tests: `pytest -q`
- Lint: `ruff check .`
- Format: `ruff format .`
- Type-check (opz.): `mypy` (o `pyright` se configurato)

## Code style & conventions
- Formatting: `ruff format` (PEP 8)
- Lint: `ruff` con regole definite in `pyproject.toml`
- Tipi: type hints obbligatori in `analyzers/*` e `services/*`
- Nomi branch: `feat/...`, `fix/...`, `chore/...`, `docs/...`
- Conventional Commits per messaggi

## Test policy
- Copertura minima: 85% linee
- Marcatori:
  - Test rapidi: `pytest -m "not slow"`
  - Integrazione/lenti: `pytest -m slow`
- Regola: test sempre su nuove funzioni/bugfix

## Execution policy (per l'agente)
- **Permesso modifiche**: `app/`, `analyzers/`, `services/`, `tests/`, `migrations/`
- **Vietato toccare**: `infra/terraform`, `secrets/`, `docs/legal/`
- **Dipendenze nuove**: PR separata `chore/deps-<pkg>` con motivazione
- **Migrazioni DB**: generare Alembic + note in PR
- **Rete**: abilitarla solo per installare deps o test di integrazione

## CI hints
- La CI (GitHub Actions) esegue: ruff + pytest + coverage
- PR verso `develop` (feature) o `main` (hotfix)
- Blocca merge se coverage < 85%

## Known issues
- SQLite locking nei test: serializzare test che scrivono su DB
- Path Windows: preferire `pathlib` nei nuovi moduli

## Example tasks for @codex
- "Crea endpoint `/api/v1/matrici` (CRUD), schema pydantic e test"
- "Aggiungi Levene test in `analyzers/variance.py` + unit test + docstring"
- "Separa plotting dai calcoli in `StatisticalAnalyzer` e aggiungi residual plots"
- "Porta coverage `analyzers/` > 90%"
- "Implementa heatmap delle correlazioni con salvataggio PNG + test su shape"
