"""
Conftest para tests de pipeline.

Mockea los módulos que requieren dependencias externas (telegram, pyodbc)
antes de que factory.py los importe transitivamente.
"""
import sys
from unittest.mock import MagicMock

# telegram y submodulos
for _mod in ["telegram", "telegram.ext", "telegram.error", "telegram.ext.filters"]:
    sys.modules.setdefault(_mod, MagicMock())

# pyodbc / sqlalchemy y todos los submodulos usados por DatabaseManager
for _mod in [
    "pyodbc",
    "sqlalchemy",
    "sqlalchemy.orm",
    "sqlalchemy.engine",
    "sqlalchemy.pool",
    "sqlalchemy.exc",
    "sqlalchemy.ext",
    "sqlalchemy.ext.asyncio",
]:
    sys.modules.setdefault(_mod, MagicMock())
