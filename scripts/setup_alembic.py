"""Script per inizializzare Alembic e creare la prima migrazione."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

def run_command(cmd: list[str], description: str) -> None:
    """Esegue un comando e stampa il risultato."""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"❌ Errore durante: {description}")
        sys.exit(1)
    else:
        print(f"✅ {description} completato!")


def main() -> None:
    """Inizializza Alembic e crea la migrazione per aggiungere il campo country."""
    
    project_root = Path(__file__).parent.parent
    migrations_dir = project_root / "migrations"
    
    # Step 1: Inizializza migrations se non esiste
    if not migrations_dir.exists():
        run_command(
            ["flask", "db", "init"],
            "Inizializzazione cartella migrations"
        )
    else:
        print("\n✓ Cartella migrations già esistente, salto inizializzazione")
    
    # Step 2: Crea migrazione per aggiungere country
    run_command(
        ["flask", "db", "migrate", "-m", "Add country field to Person"],
        "Generazione migrazione per campo country"
    )
    
    print("\n" + "="*60)
    print("🎉 Setup Alembic completato!")
    print("="*60)
    print("\nProssimi passi:")
    print("1. Rivedi la migrazione in migrations/versions/")
    print("2. Applica la migrazione con: flask db upgrade")
    print("3. Usa 'flask db migrate -m \"messaggio\"' per future modifiche")
    print("="*60)


if __name__ == "__main__":
    main()
