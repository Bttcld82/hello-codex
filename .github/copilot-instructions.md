# GitHub Copilot Instructions - Hello Codex

## Panoramica del Progetto

Questo è un **worktime tracker** costruito con Flask per tracciare le ore lavorate dai membri del team sui progetti. L'applicazione permette di gestire progetti, persone e timesheet con autenticazione e reset password.

## Stack Tecnologico

- **Framework**: Flask 3.1+
- **ORM**: SQLAlchemy con Flask-SQLAlchemy
- **Database**: SQLite (development)
- **Migrazioni**: Flask-Migrate (Alembic)
- **Autenticazione**: Flask-Login
- **Form**: Flask-WTF con WTForms
- **Template**: Jinja2
- **Testing**: pytest con pytest-cov
- **Linting**: Ruff
- **Type Checking**: mypy
- **Package Manager**: UV (moderno, veloce)
- **Python Version**: 3.13

## Struttura del Progetto

```
app/
  ├── __init__.py          # Application factory
  ├── extensions.py        # Flask extensions (db, migrate, login_manager, csrf)
  ├── models.py            # SQLAlchemy models (Project, Person, TimeEntry)
  ├── forms.py             # WTForms definitions
  ├── auth/                # Authentication blueprint (login, password reset)
  ├── views/               # Application blueprints (dashboard, projects, people, timesheet)
  ├── templates/           # Jinja2 templates
  └── static/              # Static files (CSS, JS)
instance/
  └── app.db               # SQLite database
scripts/                   # Utility scripts (seed data, migrations)
tests/                     # Test suite
```

## Convenzioni di Codifica

### Generale
- **Type hints**: Usa sempre type hints con `from __future__ import annotations`
- **Docstrings**: Usa docstrings stile Google per classi e funzioni pubbliche
- **Formatting**: Segui le regole di Ruff (line length 88, modern Python)
- **Imports**: Ordina con `from __future__` per primo, poi standard library, poi third-party, poi local

### Modelli SQLAlchemy
- Usa `Mapped` e `mapped_column` (SQLAlchemy 2.0 style)
- Eredita da `TimestampMixin` per `created_at`
- Usa `UserMixin` per modelli che richiedono autenticazione
- Definisci `__repr__` per debug
- Usa relationships bidirezionali con `back_populates`

Esempio:
```python
class Person(UserMixin, TimestampMixin, db.Model):
    __tablename__ = "people"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(db.String(120), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False)
```

### Routes e Views
- Usa blueprints per organizzare le routes
- Applica `@login_required` per routes protette
- Usa `@roles_required("admin")` per routes admin-only
- Ritorna `ResponseReturnValue` come type hint
- Gestisci form con POST/redirect/GET pattern

### Form
- Eredita da `FlaskForm`
- Usa validators appropriati (DataRequired, Email, Length, etc.)
- Implementa custom validators come metodi `validate_<field>`

### Password e Sicurezza
- **IMPORTANTE**: Usa sempre `user.set_password(password)` per hashare le password
- Non salvare mai password in chiaro
- Usa `werkzeug.security.generate_password_hash` e `check_password_hash`
- Token di reset: usa `secrets.token_urlsafe(32)` con expiry di 1 ora

### Database Migrations (Alembic)
- Usa Flask-Migrate per gestire le migrazioni
- Comandi principali:
  - `flask db init` - Inizializza migrations (già fatto)
  - `flask db migrate -m "descrizione"` - Genera migrazione automatica
  - `flask db upgrade` - Applica migrazioni
  - `flask db downgrade` - Rollback migrazioni
- Non creare script Python manuali per modifiche al DB, usa sempre migrations

### Testing
- Test in `tests/` con pytest
- Usa fixtures in `conftest.py` per setup comune
- Nomina test con `test_*`
- Usa `client.get()` e `client.post()` per testare routes
- Testa sia success che failure cases

## Comandi Utili

```bash
# Attivare virtual environment
.venv/Scripts/Activate.ps1

# Installare dipendenze (il progetto usa UV)
uv sync                    # Installa tutte le dipendenze
uv add <package>          # Aggiungi nuova dipendenza
uv add --dev <package>    # Aggiungi dev dependency

# Creare admin user
flask create-admin --email admin@example.com --password xxx

# Database migrations
flask db init             # Prima volta (già fatto)
flask db migrate -m "Add new field"
flask db upgrade
flask db downgrade

# Run tests
pytest
pytest --cov=app tests/

# Linting
ruff check .
ruff format .

# Type checking
mypy app/
```

## Pattern Comuni

### Creare una nuova feature
1. Aggiungi/modifica model in `models.py`
2. Crea migration: `flask db migrate -m "Add feature"`
3. Applica migration: `flask db upgrade`
4. Aggiungi form in `forms.py`
5. Crea view/blueprint in `app/views/`
6. Aggiungi template in `app/templates/`
7. Scrivi test in `tests/`

### Aggiungere una colonna a una tabella esistente
```bash
# 1. Modifica il model in models.py
# 2. Genera migration
flask db migrate -m "Add column_name to table_name"
# 3. Rivedi il file generato in migrations/versions/
# 4. Applica
flask db upgrade
```

### Query comuni
```python
# Get by ID
user = Person.query.get(user_id)

# Filter
projects = Project.query.filter_by(is_active=True).all()

# Join
entries = TimeEntry.query.join(Project).filter(Project.client == "ClientX").all()

# Aggregate
total = db.session.query(db.func.sum(TimeEntry.duration_hours)).scalar()
```

## Best Practices

1. **Non usare raw SQL** - Usa sempre SQLAlchemy ORM
2. **Migrations first** - Ogni cambio al DB deve avere una migration
3. **Type safety** - Usa mypy per catch errors
4. **Test coverage** - Mantieni coverage > 80%
5. **CSRF protection** - Già abilitato, non disabilitare
6. **Session management** - Usa `db.session.commit()` esplicitamente
7. **Error handling** - Gestisci eccezioni SQLAlchemy appropriatamente
8. **Validazione input** - Usa WTForms validators, non validare manualmente

## Note Specifiche del Progetto

- Il progetto usa **Italian language** nei commenti e messaggi utente quando appropriato
- Password reset implementato con token via email (mock in development)
- Dashboard con aggregazioni per periodo configurabile
- Sistema di ruoli: "admin" e "user"
- Hourly rate per persona per calcoli finanziari

## Quando Suggerire Cambiamenti

- Se vedi password in chiaro, suggerisci subito hashing
- Se vedi raw SQL, suggerisci refactor a ORM
- Se mancano type hints, aggiungili
- Se mancano test per nuove feature, suggeriscili
- Se una migration è necessaria, guidami a crearla correttamente

## Evita

- ❌ SQLModel (questo è un progetto Flask, non FastAPI)
- ❌ Script Python manuali per DB changes (usa migrations)
- ❌ Modifiche dirette al database senza migrations
- ❌ Password in chiaro nel database
- ❌ SQL injection vulnerabilities
- ❌ Disabilitare CSRF protection
- ❌ Usare `db.create_all()` in production (usa migrations)
