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
