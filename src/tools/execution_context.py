"""
Contexto de ejecución para tools.

Proporciona acceso centralizado a todos los componentes del sistema
que un tool puede necesitar durante su ejecución.
"""
import logging
from typing import Any, Dict, Optional
from dataclasses import dataclass
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


@dataclass
class ExecutionContext:
    """
    Contexto de ejecución que encapsula todas las dependencias
    necesarias para ejecutar un tool.

    Actúa como un contenedor de dependencias que desacopla los tools
    de los detalles de implementación de Telegram y otros servicios.

    Attributes:
        telegram_update: Update de Telegram (si aplica)
        telegram_context: Context de Telegram (si aplica)
        db_manager: Gestor de base de datos
        llm_agent: Agente LLM refactorizado
        user_manager: Gestor de usuarios
        permission_checker: Verificador de permisos
        extra_services: Servicios adicionales por nombre
    """

    # Componentes de Telegram
    telegram_update: Optional[Update] = None
    telegram_context: Optional[ContextTypes.DEFAULT_TYPE] = None

    # Componentes core del sistema
    db_manager: Optional["DatabaseManager"] = None
    llm_agent: Optional["LLMAgent"] = None

    # Componentes de autenticación y autorización
    user_manager: Optional["UserManager"] = None
    permission_checker: Optional["PermissionChecker"] = None

    # Servicios adicionales
    extra_services: Dict[str, Any] = None

    def __post_init__(self):
        """Inicializar servicios extra si no están definidos."""
        if self.extra_services is None:
            self.extra_services = {}

    # === Propiedades de acceso a componentes LLM ===

    @property
    def llm_provider(self) -> Optional["LLMProvider"]:
        """
        Obtener el proveedor LLM actual.

        Returns:
            LLMProvider o None si no hay LLMAgent
        """
        if self.llm_agent:
            return self.llm_agent.llm_provider
        return None

    @property
    def query_classifier(self) -> Optional["QueryClassifier"]:
        """
        Obtener el clasificador de queries.

        Returns:
            QueryClassifier o None si no hay LLMAgent
        """
        if self.llm_agent:
            return self.llm_agent.query_classifier
        return None

    @property
    def sql_generator(self) -> Optional["SQLGenerator"]:
        """
        Obtener el generador de SQL.

        Returns:
            SQLGenerator o None si no hay LLMAgent
        """
        if self.llm_agent:
            return self.llm_agent.sql_generator
        return None

    @property
    def sql_validator(self) -> Optional["SQLValidator"]:
        """
        Obtener el validador de SQL.

        Returns:
            SQLValidator o None si no hay LLMAgent
        """
        if self.llm_agent:
            return self.llm_agent.sql_validator
        return None

    @property
    def response_formatter(self) -> Optional["ResponseFormatter"]:
        """
        Obtener el formateador de respuestas.

        Returns:
            ResponseFormatter o None si no hay LLMAgent
        """
        if self.llm_agent:
            return self.llm_agent.response_formatter
        return None

    @property
    def prompt_manager(self) -> Optional["PromptManager"]:
        """
        Obtener el gestor de prompts.

        Returns:
            PromptManager o None si no hay LLMAgent
        """
        if self.llm_agent:
            return self.llm_agent.prompt_manager
        return None

    # === Métodos de utilidad ===

    def get_service(self, name: str) -> Optional[Any]:
        """
        Obtener un servicio adicional por nombre.

        Args:
            name: Nombre del servicio

        Returns:
            El servicio o None si no existe
        """
        return self.extra_services.get(name)

    def add_service(self, name: str, service: Any) -> None:
        """
        Agregar un servicio adicional al contexto.

        Args:
            name: Nombre del servicio
            service: Instancia del servicio
        """
        self.extra_services[name] = service
        logger.debug(f"Servicio '{name}' agregado al contexto")

    def get_user_id(self) -> Optional[int]:
        """
        Obtener el ID del usuario desde el update de Telegram.

        Returns:
            ID del usuario o None si no hay update
        """
        if self.telegram_update and self.telegram_update.effective_user:
            return self.telegram_update.effective_user.id
        return None

    def get_chat_id(self) -> Optional[int]:
        """
        Obtener el ID del chat desde el update de Telegram.

        Returns:
            ID del chat o None si no hay update
        """
        if self.telegram_update and self.telegram_update.effective_chat:
            return self.telegram_update.effective_chat.id
        return None

    def get_username(self) -> Optional[str]:
        """
        Obtener el username desde el update de Telegram.

        Returns:
            Username o None si no hay update
        """
        if self.telegram_update and self.telegram_update.effective_user:
            return self.telegram_update.effective_user.username
        return None

    def has_llm_agent(self) -> bool:
        """
        Verificar si hay un LLMAgent disponible.

        Returns:
            bool: True si hay LLMAgent
        """
        return self.llm_agent is not None

    def has_db_manager(self) -> bool:
        """
        Verificar si hay un DatabaseManager disponible.

        Returns:
            bool: True si hay DatabaseManager
        """
        return self.db_manager is not None

    def has_telegram_context(self) -> bool:
        """
        Verificar si hay contexto de Telegram disponible.

        Returns:
            bool: True si hay contexto de Telegram
        """
        return self.telegram_update is not None and self.telegram_context is not None

    def validate_required_components(self, *components: str) -> tuple[bool, Optional[str]]:
        """
        Validar que los componentes requeridos estén disponibles.

        Args:
            *components: Nombres de componentes requeridos
                        (ej: 'llm_agent', 'db_manager', 'telegram_context')

        Returns:
            tuple: (todos_disponibles, mensaje_error)
        """
        component_map = {
            'llm_agent': self.llm_agent,
            'db_manager': self.db_manager,
            'telegram_update': self.telegram_update,
            'telegram_context': self.telegram_context,
            'user_manager': self.user_manager,
            'permission_checker': self.permission_checker
        }

        for component in components:
            if component not in component_map:
                return False, f"Componente desconocido: {component}"
            if component_map[component] is None:
                return False, f"Componente requerido no disponible: {component}"

        return True, None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertir el contexto a diccionario (para logging/debugging).

        Returns:
            Diccionario con información del contexto
        """
        return {
            "has_telegram_context": self.has_telegram_context(),
            "has_llm_agent": self.has_llm_agent(),
            "has_db_manager": self.has_db_manager(),
            "user_id": self.get_user_id(),
            "chat_id": self.get_chat_id(),
            "username": self.get_username(),
            "extra_services": list(self.extra_services.keys())
        }

    def __repr__(self) -> str:
        """Representación en string del contexto."""
        components = []
        if self.llm_agent:
            components.append("LLM")
        if self.db_manager:
            components.append("DB")
        if self.has_telegram_context():
            components.append("Telegram")
        if self.user_manager:
            components.append("UserMgr")
        if self.permission_checker:
            components.append("Perms")

        return f"<ExecutionContext({', '.join(components)})>"


class ExecutionContextBuilder:
    """
    Builder para crear ExecutionContext de manera fluida.

    Facilita la construcción de contextos con configuración paso a paso.
    """

    def __init__(self):
        """Inicializar el builder."""
        self._telegram_update: Optional[Update] = None
        self._telegram_context: Optional[ContextTypes.DEFAULT_TYPE] = None
        self._db_manager: Optional["DatabaseManager"] = None
        self._llm_agent: Optional["LLMAgent"] = None
        self._user_manager: Optional["UserManager"] = None
        self._permission_checker: Optional["PermissionChecker"] = None
        self._extra_services: Dict[str, Any] = {}

    def with_telegram(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> "ExecutionContextBuilder":
        """Agregar componentes de Telegram."""
        self._telegram_update = update
        self._telegram_context = context
        return self

    def with_db_manager(
        self,
        db_manager: "DatabaseManager"
    ) -> "ExecutionContextBuilder":
        """Agregar DatabaseManager."""
        self._db_manager = db_manager
        return self

    def with_llm_agent(
        self,
        llm_agent: "LLMAgent"
    ) -> "ExecutionContextBuilder":
        """Agregar LLMAgent."""
        self._llm_agent = llm_agent
        return self

    def with_user_manager(
        self,
        user_manager: "UserManager"
    ) -> "ExecutionContextBuilder":
        """Agregar UserManager."""
        self._user_manager = user_manager
        return self

    def with_permission_checker(
        self,
        permission_checker: "PermissionChecker"
    ) -> "ExecutionContextBuilder":
        """Agregar PermissionChecker."""
        self._permission_checker = permission_checker
        return self

    def with_service(
        self,
        name: str,
        service: Any
    ) -> "ExecutionContextBuilder":
        """Agregar un servicio adicional."""
        self._extra_services[name] = service
        return self

    def build(self) -> ExecutionContext:
        """
        Construir el ExecutionContext.

        Returns:
            ExecutionContext configurado
        """
        return ExecutionContext(
            telegram_update=self._telegram_update,
            telegram_context=self._telegram_context,
            db_manager=self._db_manager,
            llm_agent=self._llm_agent,
            user_manager=self._user_manager,
            permission_checker=self._permission_checker,
            extra_services=self._extra_services.copy()
        )
