"""
test_message.py — Envía un mensaje al bot y valida los logs en BD.

Uso:
    python scripts/test_message.py "cuánto es el 15% de 200"
    python scripts/test_message.py "hola" --user 1835573278
"""
import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Forzar UTF-8 en stdout/stderr (Windows usa cp1252 por defecto)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from src.config.settings import settings  # noqa: E402 — necesita sys.path primero
from src.infra.database.connection import DatabaseManager
from src.pipeline.factory import create_main_handler


async def send_message(user_id: str, text: str) -> dict:
    db = DatabaseManager()
    handler = create_main_handler(db)
    response = await handler.handle_api(user_id=user_id, text=text)
    db.close()
    return {
        "success": response.success,
        "message": response.message,
        "steps": response.steps_taken,
        "error": response.error,
        "correlation_id": (response.data or {}).get("correlation_id") if response.data else None,
    }


def query_logs(correlation_id: str) -> None:
    from sqlalchemy import create_engine, text
    engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args={"timeout": 15})

    with engine.connect() as conn:
        # ── InteractionLogs ──────────────────────────────────────────────
        r = conn.execute(text("""
            SELECT correlationId, idUsuario, telegramChatId, exitoso,
                   stepsTomados, toolsUsadas, memoryMs, reactMs, duracionMs,
                   mensajeError, fechaEjecucion
            FROM abcmasplus..BotIAv2_InteractionLogs
            WHERE correlationId = :cid
        """), {"cid": correlation_id})
        rows = [dict(zip(r.keys(), row)) for row in r.fetchall()]

        print("\n── InteractionLogs ─────────────────────────────────────────")
        if rows:
            row = rows[0]
            print(f"  correlationId : {row['correlationId']}")
            print(f"  idUsuario     : {row['idUsuario']}")
            print(f"  telegramChatId: {row['telegramChatId']}")
            print(f"  exitoso       : {bool(row['exitoso'])}")
            print(f"  stepsTomados  : {row['stepsTomados']}")
            print(f"  toolsUsadas   : {row['toolsUsadas']}")
            print(f"  memoryMs      : {row['memoryMs']}ms")
            print(f"  reactMs       : {row['reactMs']}ms")
            print(f"  duracionMs    : {row['duracionMs']}ms")
            print(f"  mensajeError  : {row['mensajeError']}")
            print(f"  fechaEjecucion: {row['fechaEjecucion']}")
        else:
            print("  ⚠ NO SE ENCONTRÓ LA FILA — posible bug en save_interaction()")

        # ── InteractionSteps ─────────────────────────────────────────────
        r = conn.execute(text("""
            SELECT stepNum, tipo, nombre, tokensIn, tokensOut, duracionMs, fechaInicio
            FROM abcmasplus..BotIAv2_InteractionSteps
            WHERE correlationId = :cid
            ORDER BY stepNum
        """), {"cid": correlation_id})
        steps = [dict(zip(r.keys(), row)) for row in r.fetchall()]

        print(f"\n── InteractionSteps ({len(steps)} pasos) ───────────────────────")
        if steps:
            for s in steps:
                tokens = f"in={s['tokensIn']} out={s['tokensOut']}" if s['tokensIn'] else "—"
                print(f"  [{s['stepNum']}] {s['tipo']:<10} {str(s['nombre']):<20} "
                      f"{s['duracionMs']:>5}ms  tokens:{tokens}  inicio:{s['fechaInicio']}")
        else:
            print("  ⚠ SIN STEPS — posible bug en save_steps()")

        # ── CostSesiones ─────────────────────────────────────────────────
        r = conn.execute(text("""
            SELECT correlationId, modelo, inputTokens, outputTokens,
                   cacheReadTokens, llamadasLLM, costoUSD, pasos, fechaSesion
            FROM abcmasplus..BotIAv2_CostSesiones
            WHERE correlationId = :cid
        """), {"cid": correlation_id})
        costs = [dict(zip(r.keys(), row)) for row in r.fetchall()]

        print("\n── CostSesiones ────────────────────────────────────────────")
        if costs:
            c = costs[0]
            print(f"  correlationId : {c['correlationId']}")
            print(f"  modelo        : {c['modelo']}")
            print(f"  tokens        : in={c['inputTokens']} out={c['outputTokens']} cache={c['cacheReadTokens']}")
            print(f"  llamadasLLM   : {c['llamadasLLM']}")
            print(f"  costoUSD      : ${c['costoUSD']:.6f}")
            print(f"  fechaSesion   : {c['fechaSesion']}")
        else:
            print("  ⚠ SIN REGISTRO DE COSTO")

        # ── ApplicationLogs (errores de este request) ────────────────────
        r = conn.execute(text("""
            SELECT level, event, message, extra, createdAt
            FROM abcmasplus..BotIAv2_ApplicationLogs
            WHERE correlationId = :cid
            ORDER BY createdAt
        """), {"cid": correlation_id})
        logs = [dict(zip(r.keys(), row)) for row in r.fetchall()]

        print(f"\n── ApplicationLogs ({len(logs)} entradas) ───────────────────────")
        if logs:
            for l in logs:
                print(f"  [{l['level']}] {l['event']}")
                print(f"    {l['message'][:120]}")
                if l['extra']:
                    extra = json.loads(l['extra']) if isinstance(l['extra'], str) else l['extra']
                    tb = extra.get("traceback", "")
                    if tb:
                        print(f"    traceback: ...{tb[-200:]}")
        else:
            print("  (sin errores/warnings — OK)")

    engine.dispose()


async def main():
    parser = argparse.ArgumentParser(description="Test end-to-end del bot")
    parser.add_argument("message", help="Mensaje a enviar al bot")
    parser.add_argument("--user", default="1835573278", help="user_id (default: 1835573278)")
    args = parser.parse_args()

    print(f"\n▶ Enviando mensaje como user={args.user}")
    print(f"  \"{args.message}\"\n")

    t0 = time.perf_counter()
    result = await send_message(args.user, args.message)
    elapsed = (time.perf_counter() - t0) * 1000

    print(f"── Respuesta del bot ({elapsed:.0f}ms) ──────────────────────────")
    print(f"  success : {result['success']}")
    print(f"  steps   : {result['steps']}")
    if result["error"]:
        print(f"  error   : {result['error']}")
    print(f"\n{result['message']}")

    # Esperar un momento para que los background tasks (save_interaction) terminen
    await asyncio.sleep(1.5)

    # Buscar el correlationId en BD (el más reciente del usuario)
    from sqlalchemy import create_engine, text
    engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args={"timeout": 15})
    with engine.connect() as conn:
        r = conn.execute(text("""
            SELECT TOP 1 correlationId
            FROM abcmasplus..BotIAv2_InteractionLogs
            WHERE telegramChatId = :uid
            ORDER BY fechaEjecucion DESC
        """), {"uid": args.user})
        row = r.fetchone()
        correlation_id = row[0] if row else None
    engine.dispose()

    if not correlation_id:
        print("\n⚠ No se encontró correlationId en BD — el INSERT falló completamente")
        return

    print(f"\n  correlationId: {correlation_id}")
    query_logs(correlation_id)
    print("\n── Validación completa ─────────────────────────────────────\n")


if __name__ == "__main__":
    asyncio.run(main())
