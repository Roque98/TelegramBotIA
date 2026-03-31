"""
run_dev.py — Modo desarrollo con hot reload.

Lanza main.py como subproceso y lo reinicia automáticamente
cuando detecta cambios en src/ o main.py.

Uso:
    pipenv run python run_dev.py

Producción:
    pipenv run python main.py
"""

import subprocess
import sys
import time
import signal
import logging
from pathlib import Path

from watchfiles import watch

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [hot-reload] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("hot-reload")

WATCH_PATHS = ["src", "main.py"]
IGNORE_PATTERNS = {"__pycache__", ".pyc", ".pyo", ".log"}
RESTART_COOLDOWN = 1.5  # segundos entre reinicios


def should_ignore(path: str) -> bool:
    return any(p in path for p in IGNORE_PATTERNS)


def start_bot() -> subprocess.Popen:
    logger.info("Iniciando bot...")
    return subprocess.Popen(
        [sys.executable, "main.py"],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )


def stop_bot(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    logger.info("Deteniendo bot...")
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


def main():
    proc = start_bot()
    last_restart = 0.0

    def handle_exit(signum, frame):
        logger.info("Cerrando...")
        stop_bot(proc)
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    watch_targets = [p for p in WATCH_PATHS if Path(p).exists()]
    logger.info(f"Observando: {watch_targets} — Ctrl+C para salir")

    for changes in watch(*watch_targets, raise_interrupt=False):
        relevant = [
            (kind, path) for kind, path in changes
            if not should_ignore(path)
        ]
        if not relevant:
            continue

        now = time.monotonic()
        if now - last_restart < RESTART_COOLDOWN:
            continue

        for _, path in relevant:
            rel = Path(path).relative_to(Path.cwd()) if Path(path).is_absolute() else path
            logger.info(f"{rel} modificado — reiniciando...")

        stop_bot(proc)
        time.sleep(0.3)
        proc = start_bot()
        last_restart = time.monotonic()


if __name__ == "__main__":
    main()
