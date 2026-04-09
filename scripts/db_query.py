"""
db_query.py — Herramienta de consulta SQL para Claude Code.

Permite ejecutar queries directamente contra la BD del proyecto
para que Claude pueda inspeccionar datos reales durante el desarrollo.

Uso:
    python scripts/db_query.py "SELECT TOP 5 * FROM BotIAv2_InteractionLogs"
    python scripts/db_query.py --file scripts/my_query.sql
    python scripts/db_query.py --json "SELECT * FROM BotIAv2_InteractionLogs WHERE idUsuario = 1"
    echo "SELECT 1" | python scripts/db_query.py

Flags:
    --json      Salida en JSON (default: tabla ASCII)
    --csv       Salida en CSV
    --maxrows N Límite de filas (default: 50)
    --file F    Leer SQL desde archivo
    --write     Permite INSERT/UPDATE/DELETE (por defecto solo SELECT/EXEC)
"""
import argparse
import json
import sys
import os
from pathlib import Path

# Forzar UTF-8 en stdout/stderr (Windows usa cp1252 por defecto)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = open(sys.stderr.fileno(), mode="w", encoding="utf-8", buffering=1)

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
        connect_args={"timeout": 15},
    )


def execute_sql(sql: str, allow_write: bool = False) -> tuple[list[dict], list[str]]:
    """Ejecuta SQL y retorna (filas, columnas)."""
    sql = sql.strip()
    upper = sql.upper()

    read_prefixes  = ("SELECT", "EXEC", "WITH", "DECLARE")
    write_prefixes = ("INSERT", "UPDATE", "DELETE", "MERGE", "EXEC")
    ddl_prefixes   = ("ALTER", "CREATE", "DROP", "TRUNCATE", "IF")

    is_read  = any(upper.startswith(p) for p in read_prefixes)
    is_write = any(upper.startswith(p) for p in write_prefixes)
    is_ddl   = any(upper.startswith(p) for p in ddl_prefixes)

    if not is_read and not is_write and not is_ddl:
        allowed = read_prefixes + write_prefixes + ddl_prefixes
        raise ValueError(f"Tipo de query no permitido. Debe comenzar con: {', '.join(sorted(set(allowed)))}")

    if not is_read and not allow_write:
        raise ValueError("Escritura/DDL no permitido. Usar --write para INSERT/UPDATE/DELETE/ALTER/CREATE/DROP.")

    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql))

        if result.returns_rows:
            cols = list(result.keys())
            rows = [dict(zip(cols, row)) for row in result.fetchall()]
            return rows, cols
        else:
            conn.commit()
            affected = result.rowcount if result.rowcount >= 0 else 0
            return [{"rows_affected": affected}], ["rows_affected"]


def format_table(rows: list[dict], cols: list[str], maxrows: int) -> str:
    """Formatea resultado como tabla ASCII."""
    if not rows:
        return "(sin resultados)"

    total = len(rows)
    rows = rows[:maxrows]

    # Calcular anchos de columna
    widths = {col: len(col) for col in cols}
    for row in rows:
        for col in cols:
            val = str(row.get(col, ""))
            # Truncar valores muy largos para la tabla
            if len(val) > 80:
                val = val[:77] + "..."
            widths[col] = max(widths[col], len(val))

    # Separador
    sep = "+" + "+".join("-" * (w + 2) for w in widths.values()) + "+"

    # Header
    header = "|" + "|".join(f" {col:<{widths[col]}} " for col in cols) + "|"

    lines = [sep, header, sep]

    for row in rows:
        cells = []
        for col in cols:
            val = str(row.get(col, ""))
            if val == "None":
                val = "NULL"
            if len(val) > 80:
                val = val[:77] + "..."
            cells.append(f" {val:<{widths[col]}} ")
        lines.append("|" + "|".join(cells) + "|")

    lines.append(sep)

    if total > maxrows:
        lines.append(f"  (mostrando {maxrows} de {total} filas — usar --maxrows N para ver más)")

    return "\n".join(lines)


def format_csv(rows: list[dict], cols: list[str]) -> str:
    """Formatea como CSV."""
    import csv
    import io
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def main():
    parser = argparse.ArgumentParser(description="Consulta SQL para Claude Code")
    parser.add_argument("query", nargs="?", help="Query SQL a ejecutar")
    parser.add_argument("--file", "-f", help="Archivo .sql a ejecutar")
    parser.add_argument("--json", "-j", action="store_true", help="Salida JSON")
    parser.add_argument("--csv", "-c", action="store_true", help="Salida CSV")
    parser.add_argument("--maxrows", "-n", type=int, default=50, help="Máximo de filas (default: 50)")
    parser.add_argument("--write", "-w", action="store_true", help="Permitir escritura")
    args = parser.parse_args()

    # Determinar SQL fuente
    if args.file:
        sql = Path(args.file).read_text(encoding="utf-8")
    elif args.query:
        sql = args.query
    elif not sys.stdin.isatty():
        sql = sys.stdin.read()
    else:
        parser.print_help()
        sys.exit(1)

    if not sql.strip():
        print("Error: query vacío", file=sys.stderr)
        sys.exit(1)

    try:
        rows, cols = execute_sql(sql, allow_write=args.write)

        if args.json:
            # Serializar valores no-JSON-nativos
            def default(o):
                import datetime
                if isinstance(o, (datetime.date, datetime.datetime)):
                    return o.isoformat()
                return str(o)
            print(json.dumps(rows, ensure_ascii=False, indent=2, default=default))

        elif args.csv:
            print(format_csv(rows, cols))

        else:
            print(format_table(rows, cols, args.maxrows))
            print(f"\n  {len(rows)} fila(s)")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error ejecutando query: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
