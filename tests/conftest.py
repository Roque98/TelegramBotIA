"""
Configuración global de pytest.

Pre-registra los submodulos de telegram en sys.modules ANTES de que cualquier
test file los importe. Esto evita que el sys.modules["telegram"] = MagicMock()
de test_gateway.py corrompa las importaciones de telegram.error en otros tests.

El truco: las entradas de submodulos en sys.modules son independientes del
módulo padre, por lo que sobreviven aunque sys.modules["telegram"] se reemplace.
"""
import sys
from unittest.mock import MagicMock

# Pre-registrar submodulos de telegram para que sean accesibles incluso
# cuando test_gateway.py reemplaza sys.modules["telegram"] con un MagicMock
for _submod in [
    "telegram.error",
    "telegram.ext",
    "telegram.ext.filters",
]:
    sys.modules.setdefault(_submod, MagicMock())
