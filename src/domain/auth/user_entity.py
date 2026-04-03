"""
Entidades del módulo de autenticación.

Define los modelos de datos que representan usuarios, permisos y operaciones.
"""

from typing import Dict, Any, Optional


class TelegramUser:
    """Representa un usuario de Telegram registrado en el sistema."""

    def __init__(self, data: Dict[str, Any]):
        # Datos del usuario (abcmasplus..Usuarios)
        self.id_usuario = data.get('idUsuario')
        self.nombre = data.get('Nombre')
        self.email = data.get('email')
        self.rol_id = data.get('idRol')
        self.rol_nombre = data.get('rolNombre')
        self.activo = data.get('Activa', 0)   # default seguro: inactivo hasta confirmar
        self.puesto = data.get('puesto')
        self.empresa = data.get('Empresa')

        # Datos de la cuenta de Telegram
        self.id_usuario_telegram = data.get('idUsuarioTelegram')
        self.telegram_chat_id = data.get('telegramChatId')
        self.telegram_username = data.get('telegramUsername')
        self.telegram_first_name = data.get('telegramFirstName')
        self.telegram_last_name = data.get('telegramLastName')
        self.alias = data.get('alias')
        self.es_principal = data.get('esPrincipal', False)
        self.estado = data.get('estado', 'BLOQUEADO')  # default seguro: bloqueado hasta confirmar
        self.verificado = data.get('verificado', False)
        self.fecha_ultima_actividad = data.get('fechaUltimaActividad')

    @property
    def nombre_completo(self) -> str:
        return self.nombre or ''

    @property
    def is_active(self) -> bool:
        return bool(self.activo) and self.estado == 'ACTIVO'

    @property
    def is_verified(self) -> bool:
        return self.verificado

    def __repr__(self) -> str:
        return (
            f"TelegramUser(id={self.id_usuario}, "
            f"nombre='{self.nombre_completo}', "
            f"chat_id={self.telegram_chat_id}, "
            f"rol='{self.rol_nombre}')"
        )


class PermissionResult:
    """Resultado de verificación de permisos."""

    def __init__(self, data: Dict[str, Any]):
        self.tiene_permiso = data.get('TienePermiso', False)
        self.mensaje = data.get('Mensaje', '')
        self.nombre_operacion = data.get('NombreOperacion')
        self.descripcion_operacion = data.get('DescripcionOperacion')
        self.requiere_parametros = data.get('RequiereParametros', False)
        self.parametros_ejemplo = data.get('ParametrosEjemplo')

    @property
    def is_allowed(self) -> bool:
        return bool(self.tiene_permiso)

    def __repr__(self) -> str:
        return (
            f"PermissionResult(permitido={self.tiene_permiso}, "
            f"operacion='{self.nombre_operacion}')"
        )


class Operation:
    """Representa una operación disponible."""

    def __init__(self, data: Dict[str, Any]):
        self.modulo = data.get('Modulo')
        self.icono_modulo = data.get('IconoModulo')
        self.id_operacion = data.get('idOperacion')
        self.operacion = data.get('Operacion')
        self.descripcion = data.get('descripcion')
        self.comando = data.get('comando')
        self.requiere_parametros = data.get('requiereParametros', False)
        self.parametros_ejemplo = data.get('parametrosEjemplo')
        self.nivel_criticidad = data.get('nivelCriticidad', 1)
        self.origen_permiso = data.get('OrigenPermiso')
        self.permitido = data.get('Permitido', False)

    def __repr__(self) -> str:
        return f"Operation(comando='{self.comando}', permitido={self.permitido})"


class RegistrationError(Exception):
    """Excepción para errores en el proceso de registro."""
    pass
