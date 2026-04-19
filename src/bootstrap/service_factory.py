"""
service_factory — Construcción de servicios de dominio reutilizables.

Responsabilidad única: instanciar PermissionService y MemoryService
con sus repositorios y configuración estándar.
"""

from __future__ import annotations

import logging
from typing import Any

from src.domain.auth.permission_repository import PermissionRepository
from src.domain.auth.permission_service import PermissionService
from src.domain.memory.memory_repository import MemoryRepository
from src.domain.memory.memory_service import MemoryService

logger = logging.getLogger(__name__)


def create_permission_service(db_manager: Any = None) -> PermissionService:
    """Crea el servicio de permisos SEC-01."""
    repository = PermissionRepository(db_manager=db_manager)
    service = PermissionService(repository=repository)
    logger.info("PermissionService created")
    return service


def create_memory_service(
    db_manager: Any = None,
    permission_service: Any = None,
) -> MemoryService:
    """Crea el servicio de memoria."""
    repository = MemoryRepository(db_manager=db_manager)
    service = MemoryService(
        repository=repository,
        permission_service=permission_service,
        cache_ttl_seconds=300,
        max_cache_size=1000,
        max_working_memory=10,
    )
    logger.info("MemoryService created")
    return service
