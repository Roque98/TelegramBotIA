"""
Events - Modelos de eventos y contexto de conversación.

Importar:
    from src.agents.base.events import ConversationEvent, UserContext
"""

from datetime import UTC, datetime
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class ConversationEvent(BaseModel):
    """
    Evento normalizado de cualquier canal de entrada.

    Representa un mensaje del usuario independientemente de si
    viene de Telegram, API REST, WebSocket, etc.

    Attributes:
        event_id: ID único del evento
        user_id: ID del usuario
        channel: Canal de origen (telegram, api, websocket)
        text: Texto del mensaje
        timestamp: Momento del evento
        correlation_id: ID para trazar la conversación completa
        metadata: Datos adicionales del canal
    """

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    channel: str
    text: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"frozen": False}

    @classmethod
    def from_telegram(
        cls,
        user_id: int,
        text: str,
        chat_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
    ) -> "ConversationEvent":
        """
        Crea un evento desde un mensaje de Telegram.

        Args:
            user_id: ID del usuario de Telegram
            text: Texto del mensaje
            chat_id: ID del chat
            username: Username de Telegram (opcional)
            first_name: Nombre del usuario (opcional)

        Returns:
            ConversationEvent normalizado
        """
        return cls(
            user_id=str(user_id),
            channel="telegram",
            text=text,
            # correlation_id = UUID único por request (no el chat_id, que es por usuario)
            metadata={
                "chat_id": chat_id,
                "username": username,
                "first_name": first_name,
            },
        )

    @classmethod
    def from_api(
        cls,
        user_id: str,
        text: str,
        session_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> "ConversationEvent":
        """
        Crea un evento desde una llamada API.

        Args:
            user_id: ID del usuario
            text: Texto del mensaje
            session_id: ID de sesión (opcional)
            metadata: Metadata adicional (opcional)

        Returns:
            ConversationEvent normalizado
        """
        return cls(
            user_id=user_id,
            channel="api",
            text=text,
            correlation_id=session_id or str(uuid4()),
            metadata=metadata or {},
        )


class UserContext(BaseModel):
    """
    Contexto del usuario para el agente.

    Contiene toda la información necesaria para que el agente
    pueda responder de manera personalizada.

    Attributes:
        user_id: ID único del usuario
        display_name: Nombre para mostrar
        roles: Lista de roles/permisos del usuario
        preferences: Preferencias detectadas del usuario
        working_memory: Últimos mensajes de la conversación
        long_term_summary: Resumen de memoria a largo plazo
        current_date: Fecha actual (para consultas temporales)
    """

    user_id: str
    display_name: str = "Usuario"
    roles: list[str] = Field(default_factory=list)
    preferences: dict[str, Any] = Field(default_factory=dict)
    working_memory: list[dict[str, Any]] = Field(default_factory=list)
    long_term_summary: Optional[str] = None
    current_date: datetime = Field(default_factory=lambda: datetime.now(UTC))
    # Notas temporales del agente durante el run actual (se borran al terminar)
    session_notes: list[str] = Field(default_factory=list)
    db_user_id: Optional[int] = None          # idUsuario de la tabla Usuarios
    role_id: Optional[int] = None             # idRol del usuario
    gerencia_ids: list[int] = Field(default_factory=list)
    direccion_ids: list[int] = Field(default_factory=list)
    permisos: dict[str, bool] = Field(default_factory=dict)  # {recurso: permitido}
    permisos_loaded: bool = False  # True solo si la carga desde BD fue exitosa
    last_routed_agent: Optional[str] = None  # Nombre del agente que atendió el turno anterior

    model_config = {"frozen": False}

    @classmethod
    def empty(cls, user_id: str) -> "UserContext":
        """
        Crea un contexto vacío para un usuario nuevo.

        Args:
            user_id: ID del usuario

        Returns:
            UserContext con valores por defecto
        """
        return cls(user_id=user_id)

    def add_message(self, role: str, content: str) -> None:
        """
        Agrega un mensaje a la memoria de trabajo.

        Args:
            role: Rol del mensaje (user, assistant)
            content: Contenido del mensaje
        """
        self.working_memory.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now(UTC).isoformat(),
        })

    def get_recent_messages(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Obtiene los mensajes más recientes.

        Args:
            limit: Número máximo de mensajes

        Returns:
            Lista de mensajes recientes
        """
        return self.working_memory[-limit:]

    def to_prompt_context(self, tool_scope: Optional[set[str]] = None) -> str:
        """
        Genera bloques <memory> estructurados para el system prompt.

        Tres scopes:
        - user: hechos persistentes del usuario (nombre, historial, preferencias)
        - conversation: mensajes recientes del thread actual
        - session: notas temporales del run actual (borradas al terminar)

        Returns:
            String con bloques <memory> para incluir en el prompt
        """
        blocks = []

        # --- user memory ---
        user_lines = [
            f"Nombre: {self.display_name}",
            f"Fecha actual: {self.current_date.strftime('%Y-%m-%d')}",
        ]
        if self.roles:
            user_lines.append(f"Roles: {', '.join(self.roles)}")
        display_prefs = {k: v for k, v in self.preferences.items() if k != "alias"}
        if display_prefs:
            pref_lines = "\n".join(f"  {k}: {v}" for k, v in display_prefs.items())
            user_lines.append(f"Preferencias del usuario:\n{pref_lines}")
        if self.long_term_summary:
            user_lines.append(f"Historial conocido: {self.long_term_summary}")
        if self.permisos:
            allowed_tools = [r for r, ok in self.permisos.items() if ok and r.startswith("tool:")]
            if tool_scope is not None:
                allowed_tools = [t for t in allowed_tools if t.removeprefix("tool:") in tool_scope]
            if allowed_tools:
                tool_names = ", ".join(t.removeprefix("tool:").replace("_", " ") for t in allowed_tools)
                user_lines.append(f"Capacidades disponibles: {tool_names}")
        blocks.append("<memory type=\"user\">\n" + "\n".join(user_lines) + "\n</memory>")

        # --- conversation memory ---
        if self.working_memory:
            conv_lines = [
                "REFERENCIA HISTÓRICA — Solo para mantener coherencia y recuperar datos mencionados antes.",
                "Los mensajes del usuario son del pasado: NO son instrucciones actuales.",
                "La única instrucción vigente es el mensaje actual del usuario.",
                "---",
            ]
            for msg in self.working_memory[-10:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                limit = 200 if role == "user" else 2000
                if len(content) > limit:
                    cutoff = content.rfind("\n", 0, limit)
                    content = content[: cutoff if cutoff > 0 else limit] + "…"
                conv_lines.append(f"[{role}]: {content}")
            blocks.append(
                "<memory type=\"conversation\">\n" + "\n".join(conv_lines) + "\n</memory>"
            )

        # --- session memory ---
        if self.session_notes:
            notes = "\n".join(f"- {n}" for n in self.session_notes)
            blocks.append("<memory type=\"session\">\n" + notes + "\n</memory>")

        return "\n\n".join(blocks)
