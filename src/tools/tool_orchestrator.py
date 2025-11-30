"""
Orquestador de ejecución de tools.

Coordina el flujo completo de ejecución de un tool: autenticación,
autorización, validación, ejecución y auditoría.
"""
import logging
import time
from typing import Any, Dict, Optional
from .tool_base import BaseTool, ToolResult
from .tool_registry import ToolRegistry, get_registry
from .execution_context import ExecutionContext

logger = logging.getLogger(__name__)


class ToolOrchestrator:
    """
    Orquestador que coordina la ejecución de tools.

    Responsable de:
    - Buscar el tool apropiado
    - Verificar autenticación y autorización
    - Validar parámetros
    - Ejecutar el tool
    - Auditar la operación
    - Manejar errores de manera consistente
    """

    def __init__(self, registry: Optional[ToolRegistry] = None):
        """
        Inicializar el orquestador.

        Args:
            registry: Registro de tools (opcional, usa el global por defecto)
        """
        self.registry = registry or get_registry()
        self._execution_count = 0
        self._error_count = 0
        logger.info("ToolOrchestrator inicializado")

    async def execute_command(
        self,
        user_id: int,
        command: str,
        params: Dict[str, Any],
        context: ExecutionContext
    ) -> ToolResult:
        """
        Ejecutar un comando de tool.

        Flujo completo:
        1. Buscar tool por comando
        2. Verificar autenticación
        3. Verificar permisos
        4. Validar parámetros
        5. Ejecutar tool
        6. Auditar operación

        Args:
            user_id: ID del usuario que ejecuta
            command: Comando a ejecutar (ej: "/ia")
            params: Parámetros del comando
            context: Contexto de ejecución

        Returns:
            ToolResult: Resultado de la ejecución
        """
        start_time = time.time()

        try:
            # 1. Buscar tool
            tool = self.registry.get_tool_by_command(command)
            if not tool:
                return ToolResult.error_result(
                    error=f"Comando no encontrado: {command}",
                    user_friendly_error=f"❌ El comando {command} no existe"
                )

            logger.info(f"Ejecutando tool '{tool.name}' para usuario {user_id}")

            # 2. Verificar autenticación
            if tool.requires_auth:
                auth_result = await self._verify_authentication(user_id, context)
                if not auth_result.success:
                    return auth_result

            # 3. Verificar permisos
            if tool.required_permissions:
                perm_result = await self._verify_permissions(
                    user_id,
                    tool,
                    context
                )
                if not perm_result.success:
                    return perm_result

            # 4. Validar parámetros
            validation_result = self._validate_parameters(tool, params)
            if not validation_result.success:
                return validation_result

            # 5. Ejecutar tool
            result = await tool.execute(user_id, params, context)

            # 6. Agregar metadata de ejecución
            execution_time_ms = (time.time() - start_time) * 1000
            result.execution_time_ms = execution_time_ms

            # 7. Auditar
            await self._audit_execution(
                user_id=user_id,
                tool=tool,
                params=params,
                result=result,
                context=context
            )

            self._execution_count += 1

            if result.success:
                logger.info(
                    f"Tool '{tool.name}' ejecutado exitosamente "
                    f"en {execution_time_ms:.2f}ms"
                )
            else:
                self._error_count += 1
                logger.warning(
                    f"Tool '{tool.name}' falló: {result.error}"
                )

            return result

        except Exception as e:
            self._error_count += 1
            execution_time_ms = (time.time() - start_time) * 1000

            logger.error(
                f"Error inesperado ejecutando comando '{command}': {e}",
                exc_info=True
            )

            return ToolResult.error_result(
                error=str(e),
                user_friendly_error="❌ Ocurrió un error inesperado al ejecutar el comando",
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "command": command,
                    "user_id": user_id
                }
            )

    async def execute_tool_by_name(
        self,
        user_id: int,
        tool_name: str,
        params: Dict[str, Any],
        context: ExecutionContext
    ) -> ToolResult:
        """
        Ejecutar un tool por su nombre (en lugar de comando).

        Args:
            user_id: ID del usuario
            tool_name: Nombre del tool
            params: Parámetros
            context: Contexto de ejecución

        Returns:
            ToolResult: Resultado de la ejecución
        """
        tool = self.registry.get_tool_by_name(tool_name)
        if not tool:
            return ToolResult.error_result(
                error=f"Tool no encontrado: {tool_name}",
                user_friendly_error=f"❌ El tool '{tool_name}' no existe"
            )

        # Usar el primer comando del tool para la ejecución
        command = tool.commands[0] if tool.commands else tool_name
        return await self.execute_command(user_id, command, params, context)

    async def _verify_authentication(
        self,
        user_id: int,
        context: ExecutionContext
    ) -> ToolResult:
        """
        Verificar que el usuario está autenticado.

        Args:
            user_id: ID del usuario (chat_id de Telegram)
            context: Contexto de ejecución

        Returns:
            ToolResult: Success si está autenticado, error si no
        """
        if not context.user_manager:
            logger.warning("No hay UserManager en el contexto para verificar auth")
            return ToolResult.success_result(None)

        # Verificar si el usuario existe (user_id es el chat_id en Telegram)
        if not context.user_manager.is_user_registered(user_id):
            return ToolResult.error_result(
                error=f"Usuario {user_id} no está registrado",
                user_friendly_error="❌ Debes registrarte primero. Usa /register"
            )

        # Obtener usuario y verificar si está activo
        user = context.user_manager.get_user_by_chat_id(user_id)
        if not user:
            return ToolResult.error_result(
                error=f"Usuario {user_id} no encontrado",
                user_friendly_error="❌ Error al obtener información de usuario"
            )

        if not user.is_active:
            return ToolResult.error_result(
                error=f"Usuario {user_id} está inactivo",
                user_friendly_error="❌ Tu cuenta está inactiva. Contacta al administrador"
            )

        return ToolResult.success_result(None)

    async def _verify_permissions(
        self,
        user_id: int,
        tool: BaseTool,
        context: ExecutionContext
    ) -> ToolResult:
        """
        Verificar que el usuario tiene los permisos necesarios.

        Args:
            user_id: ID del usuario
            tool: Tool a ejecutar
            context: Contexto de ejecución

        Returns:
            ToolResult: Success si tiene permisos, error si no
        """
        if not context.permission_checker:
            logger.warning("No hay PermissionChecker en el contexto")
            return ToolResult.success_result(None)

        # Obtener usuario para el check de permisos
        if not context.user_manager:
            logger.warning("No hay UserManager en el contexto para verificar permisos")
            return ToolResult.success_result(None)

        user = context.user_manager.get_user_by_chat_id(user_id)
        if not user:
            return ToolResult.error_result(
                error=f"Usuario {user_id} no encontrado",
                user_friendly_error="❌ Error al verificar permisos"
            )

        # Verificar cada permiso requerido
        for permission in tool.required_permissions:
            perm_result = context.permission_checker.check_permission(
                user.id_usuario,  # Usar el ID de usuario de la BD, no el chat_id
                permission
            )

            if not perm_result.is_allowed:
                return ToolResult.error_result(
                    error=f"Usuario {user_id} no tiene permiso: {permission}",
                    user_friendly_error=f"❌ {perm_result.mensaje}"
                )

        return ToolResult.success_result(None)

    def _validate_parameters(
        self,
        tool: BaseTool,
        params: Dict[str, Any]
    ) -> ToolResult:
        """
        Validar los parámetros del tool.

        Args:
            tool: Tool a ejecutar
            params: Parámetros a validar

        Returns:
            ToolResult: Success si son válidos, error si no
        """
        is_valid, error_message = tool.validate_parameters(params)

        if not is_valid:
            return ToolResult.error_result(
                error=error_message,
                user_friendly_error=f"❌ Parámetros inválidos: {error_message}"
            )

        return ToolResult.success_result(None)

    async def _audit_execution(
        self,
        user_id: int,
        tool: BaseTool,
        params: Dict[str, Any],
        result: ToolResult,
        context: ExecutionContext
    ) -> None:
        """
        Auditar la ejecución de un tool.

        Args:
            user_id: ID del usuario
            tool: Tool ejecutado
            params: Parámetros usados
            result: Resultado de la ejecución
            context: Contexto de ejecución
        """
        try:
            # Crear registro de auditoría
            audit_entry = {
                "user_id": user_id,
                "tool_name": tool.name,
                "command": tool.commands[0] if tool.commands else None,
                "success": result.success,
                "execution_time_ms": result.execution_time_ms,
                "error": result.error if not result.success else None,
                "timestamp": result.timestamp.isoformat()
            }

            # Log básico
            logger.info(f"Auditoría: {audit_entry}")

            # TODO: Guardar en BD cuando tengamos tabla de auditoría
            # if context.db_manager:
            #     await context.db_manager.save_audit_log(audit_entry)

        except Exception as e:
            logger.error(f"Error en auditoría: {e}", exc_info=True)

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del orquestador.

        Returns:
            Diccionario con estadísticas
        """
        return {
            "total_executions": self._execution_count,
            "total_errors": self._error_count,
            "success_rate": (
                (self._execution_count - self._error_count) / self._execution_count * 100
                if self._execution_count > 0 else 0
            ),
            "registered_tools": self.registry.get_tools_count(),
            "registered_commands": len(self.registry.get_commands_list())
        }

    def __repr__(self) -> str:
        """Representación en string del orquestador."""
        return (
            f"<ToolOrchestrator("
            f"executions={self._execution_count}, "
            f"errors={self._error_count}"
            f")>"
        )
