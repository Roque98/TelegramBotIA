"""
run_migration.py — Ejecuta archivos de migración SQL contra la BD del proyecto.

Los archivos de migración usan sentencias GO (separadores de batch SQL Server).
Este script divide el SQL en batches por GO y los ejecuta uno a uno.

Uso:
    python scripts/run_migration.py database/migrations/arq35_dynamic_orchestrator.sql
    python scripts/run_migration.py --dry-run database/migrations/arq35_dynamic_orchestrator.sql
"""
import argparse
import re
import sys
from pathlib import Path

# Agregar raíz del proyecto al path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config.settings import settings
from sqlalchemy import create_engine, text


def get_engine():
    return create_engine(
        settings.database_url,
        echo=False,
        pool_size=1,
        max_overflow=0,
        pool_pre_ping=True,
        connect_args={"timeout": 30},
    )


def split_batches(sql: str) -> list[str]:
    """Divide el SQL en batches usando GO como separador (ignora GO dentro de strings)."""
    # Dividir por GO en línea propia (case-insensitive)
    batches = re.split(r"^\s*GO\s*$", sql, flags=re.MULTILINE | re.IGNORECASE)
    return [b.strip() for b in batches if b.strip()]


def run_migration(sql_file: Path, dry_run: bool = False) -> bool:
    """Ejecuta un archivo de migración SQL. Retorna True si tuvo éxito."""
    if not sql_file.exists():
        print(f"ERROR: Archivo no encontrado: {sql_file}", file=sys.stderr)
        return False

    sql_content = sql_file.read_text(encoding="utf-8")
    batches = split_batches(sql_content)

    print(f"Migración: {sql_file.name}")
    print(f"Batches encontrados: {len(batches)}")
    print("-" * 60)

    if dry_run:
        for i, batch in enumerate(batches, 1):
            preview = batch[:120].replace("\n", " ")
            print(f"[DRY-RUN] Batch {i}: {preview}...")
        print("\nDRY-RUN completado. No se ejecutó nada.")
        return True

    engine = get_engine()
    errors = 0

    with engine.connect() as conn:
        for i, batch in enumerate(batches, 1):
            preview = batch[:80].replace("\n", " ")
            try:
                conn.execute(text(batch))
                conn.commit()
                print(f"  [OK] Batch {i}: {preview}...")
            except Exception as e:
                errors += 1
                print(f"  [ERR] Batch {i}: {preview}...")
                print(f"        Error: {e}")

    print("-" * 60)
    if errors == 0:
        print(f"Migración completada exitosamente ({len(batches)} batches).")
        return True
    else:
        print(f"Migración completada con {errors} error(es).")
        return False


def main():
    parser = argparse.ArgumentParser(description="Ejecuta migraciones SQL contra la BD")
    parser.add_argument("sql_file", help="Archivo SQL de migración")
    parser.add_argument("--dry-run", action="store_true", help="Solo mostrar batches, no ejecutar")
    args = parser.parse_args()

    sql_path = Path(args.sql_file)
    if not sql_path.is_absolute():
        sql_path = PROJECT_ROOT / sql_path

    success = run_migration(sql_path, dry_run=args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
