"""
fill_result_docs.py — Llena automáticamente los docs de resultados de alertas.

Parsea los archivos en docs/uso/resultados-alertas/, detecta secciones sin llenar
(con el placeholder <!-- pegar respuesta del bot aquí -->), envía cada pregunta
al orquestador del bot y actualiza el archivo con la respuesta real.

Uso:
    python scripts/fill_result_docs.py [opciones]

Opciones:
    --user-id ID    ID de usuario para las consultas (default: 99999)
    --file FILE     Procesar solo un archivo (ej: 01-resumen-general.md)
    --dry-run       Muestra qué haría sin ejecutar ni escribir nada
    --force         Reemplaza también secciones ya llenadas

Ejemplos:
    python scripts/fill_result_docs.py --dry-run
    python scripts/fill_result_docs.py --file 01-resumen-general.md --user-id 12345
    python scripts/fill_result_docs.py --user-id 12345
"""

import argparse
import asyncio
import logging
import re
import sys
from datetime import date
from pathlib import Path

# Agregar raíz del proyecto al path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.infra.database.connection import DatabaseManager
from src.pipeline.factory import get_handler_manager

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

DOCS_DIR = PROJECT_ROOT / "docs" / "uso" / "resultados-alertas"
SKIP_FILES = {"README.md", "00-Agente-Definicion.md"}
PLACEHOLDER = "<!-- pegar respuesta del bot aquí -->"
TODAY = date.today().strftime("%Y-%m-%d")

# Regex: sección de nivel 2 que NO sea "Notas generales"
# Captura: group(1)=heading_line, group(2)=title, group(3)=body hasta siguiente ## o fin
SECTION_RE = re.compile(
    r"^(## (?!Notas generales)(.+?))\n(.*?)(?=^## |\Z)",
    re.MULTILINE | re.DOTALL,
)

# Patterns para detectar/rellenar la fecha
DATE_PLACEHOLDER_RE = re.compile(r"(\*\*Fecha:\*\*\s*)<!--[^>]*-->")
DATE_EMPTY_RE = re.compile(r"(\*\*Fecha:\*\*)([ \t]*)\n")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger("fill_docs")


# ---------------------------------------------------------------------------
# Lógica de parseo y reemplazo
# ---------------------------------------------------------------------------

def _is_filled(body: str) -> bool:
    """True si la sección ya tiene un resultado (no placeholder)."""
    return PLACEHOLDER not in body


def _fill_date(body: str) -> str:
    """Rellena el campo **Fecha:** con la fecha de hoy."""
    # Caso: **Fecha:** <!-- 2026-04- -->
    body = DATE_PLACEHOLDER_RE.sub(rf"\g<1>{TODAY}", body)
    # Caso: **Fecha:**  (vacío)
    body = DATE_EMPTY_RE.sub(rf"\g<1>\g<2> {TODAY}\n", body)
    return body


def _fill_result(body: str, response: str) -> str:
    """Reemplaza el placeholder con la respuesta del bot."""
    return body.replace(PLACEHOLDER, response)


def get_unfilled_sections(content: str) -> list[tuple[str, re.Match]]:
    """
    Retorna lista de (title, match) para secciones sin llenar.
    """
    return [
        (m.group(2).strip(), m)
        for m in SECTION_RE.finditer(content)
        if not _is_filled(m.group(3))
    ]


def apply_response(content: str, match: re.Match, response: str) -> str:
    """
    Reemplaza en el contenido completo la sección apuntada por `match`
    con la fecha y respuesta rellenas.
    """
    full_section = match.group(0)
    heading = match.group(1) + "\n"
    body = match.group(3)

    new_body = _fill_date(body)
    new_body = _fill_result(new_body, response)

    new_section = heading + new_body
    return content[:match.start()] + new_section + content[match.end():]


# ---------------------------------------------------------------------------
# Interacción con el bot
# ---------------------------------------------------------------------------

async def query_bot(user_id: str, question: str) -> str:
    """Envía `question` al pipeline del bot y retorna la respuesta."""
    handler = get_handler_manager().handler
    agent_response = await handler.handle_api(
        user_id=user_id,
        text=question,
        metadata={"source": "fill_result_docs"},
    )
    if agent_response.success:
        return agent_response.message or "(sin respuesta)"
    return f"[ERROR] {agent_response.error or 'sin detalle'}"


# ---------------------------------------------------------------------------
# Procesamiento de archivos
# ---------------------------------------------------------------------------

async def process_file(
    doc_file: Path,
    user_id: str,
    dry_run: bool,
    force: bool,
) -> int:
    """
    Procesa un archivo de docs.

    Returns:
        Número de secciones llenadas.
    """
    content = doc_file.read_text(encoding="utf-8")

    if force:
        # En modo --force también considera secciones ya llenadas como candidatas
        # (las vuelve a llenar con la respuesta actual)
        matches = [
            (m.group(2).strip(), m)
            for m in SECTION_RE.finditer(content)
        ]
    else:
        matches = get_unfilled_sections(content)

    if not matches:
        print(f"  {doc_file.name}: sin secciones pendientes")
        return 0

    label = "sección" if len(matches) == 1 else "secciones"
    print(f"  {doc_file.name}: {len(matches)} {label} pendiente(s)")

    filled = 0
    # Iterar en reversa para que los índices del content no se corrompan
    # al hacer sustituciones parciales
    for title, match in reversed(matches):
        short = title if len(title) <= 70 else title[:67] + "..."
        print(f"    [{filled + 1}/{len(matches)}] '{short}'")

        if dry_run:
            print("      → [DRY RUN] se enviaría la pregunta al bot")
            filled += 1
            continue

        response = await query_bot(user_id, title)
        content = apply_response(content, match, response)
        filled += 1
        preview = response[:80].replace("\n", " ")
        print(f"      → OK ({len(response)} chars): {preview}…" if len(response) > 80 else f"      → OK: {response[:80]}")

        # Re-escanear el contenido actualizado para que los match offsets sean válidos
        # (lo hacemos al revés, así no necesitamos re-escanear)

    if filled > 0 and not dry_run:
        doc_file.write_text(content, encoding="utf-8")
        print(f"    Guardado ✓")

    return filled


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Llena docs de resultados de alertas con respuestas reales del bot"
    )
    parser.add_argument(
        "--user-id",
        default="99999",
        metavar="ID",
        help="ID de usuario para las consultas (default: 99999)",
    )
    parser.add_argument(
        "--file",
        metavar="FILE",
        help="Procesar solo este archivo (ej: 01-resumen-general.md)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Muestra qué haría sin ejecutar ni escribir nada",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-llena también secciones que ya tienen resultado",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("fill_result_docs.py")
    print(f"  user_id : {args.user_id}")
    print(f"  dry_run : {args.dry_run}")
    print(f"  force   : {args.force}")
    print(f"  fecha   : {TODAY}")
    print("=" * 60)

    # Inicializar pipeline (solo si no es dry-run)
    if not args.dry_run:
        db = DatabaseManager()
        get_handler_manager().initialize(db)
        print("Pipeline inicializado.\n")
    else:
        print("[DRY RUN] Pipeline no inicializado.\n")

    # Seleccionar archivos a procesar
    if args.file:
        files = [DOCS_DIR / args.file]
        if not files[0].exists():
            print(f"ERROR: archivo no encontrado: {files[0]}")
            sys.exit(1)
    else:
        files = sorted(
            f for f in DOCS_DIR.glob("*.md") if f.name not in SKIP_FILES
        )

    if not files:
        print("No se encontraron archivos para procesar.")
        sys.exit(0)

    # Procesar
    total = 0
    for doc_file in files:
        total += await process_file(doc_file, args.user_id, args.dry_run, args.force)

    print()
    print("=" * 60)
    action = "se llenarían" if args.dry_run else "llenadas"
    print(f"Total: {total} sección(es) {action}.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
