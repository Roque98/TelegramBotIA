"""
Repositorio de usuarios.

Centraliza todas las consultas a base de datos relacionadas con usuarios,
cuentas de Telegram, registro y permisos.
"""

import json
import logging
from typing import Optional, Dict, Any, List
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.domain.auth.user_entity import TelegramUser, PermissionResult, Operation

logger = logging.getLogger(__name__)


class UserRepository:
    """Repositorio de acceso a datos de usuarios."""

    def __init__(self, db_session: Session):
        self.session = db_session

    # -------------------------------------------------------------------------
    # Consultas de usuario
    # -------------------------------------------------------------------------

    def get_user_by_chat_id(self, chat_id: int) -> Optional[TelegramUser]:
        try:
            query = text("""
                SELECT
                    u.idUsuario, u.Nombre, u.email, u.idRol, u.puesto,
                    u.Empresa, u.Activa,
                    r.nombre AS rolNombre,
                    ut.idUsuarioTelegram, ut.telegramChatId, ut.telegramUsername,
                    ut.telegramFirstName, ut.telegramLastName, ut.alias,
                    ut.esPrincipal, ut.estado, ut.verificado, ut.fechaUltimaActividad
                FROM abcmasplus..UsuariosTelegram ut
                INNER JOIN abcmasplus..Usuarios u ON ut.idUsuario = u.idUsuario
                LEFT JOIN abcmasplus..Roles r ON u.idRol = r.idRol
                WHERE ut.telegramChatId = :chat_id AND ut.activo = 1
            """)
            result = self.session.execute(query, {"chat_id": chat_id})
            row = result.fetchone()
            return TelegramUser(dict(zip(result.keys(), row))) if row else None
        except Exception as e:
            logger.error(f"Error obteniendo usuario por chat_id {chat_id}: {e}")
            raise

    def get_user_by_id(self, user_id: int) -> Optional[TelegramUser]:
        try:
            query = text("""
                SELECT
                    u.idUsuario, u.Nombre, u.email, u.idRol, u.puesto,
                    u.Empresa, u.Activa,
                    r.nombre AS rolNombre,
                    ut.idUsuarioTelegram, ut.telegramChatId, ut.telegramUsername,
                    ut.telegramFirstName, ut.telegramLastName, ut.alias,
                    ut.esPrincipal, ut.estado, ut.verificado, ut.fechaUltimaActividad
                FROM abcmasplus..Usuarios u
                LEFT JOIN abcmasplus..Roles r ON u.idRol = r.idRol
                LEFT JOIN abcmasplus..UsuariosTelegram ut
                    ON u.idUsuario = ut.idUsuario AND ut.esPrincipal = 1 AND ut.activo = 1
                WHERE u.idUsuario = :user_id
            """)
            result = self.session.execute(query, {"user_id": user_id})
            row = result.fetchone()
            return TelegramUser(dict(zip(result.keys(), row))) if row else None
        except Exception as e:
            logger.error(f"Error obteniendo usuario por ID {user_id}: {e}")
            raise

    def get_user_by_telegram_chat_id(self, chat_id: int) -> Optional[TelegramUser]:
        """Alias de get_user_by_chat_id para compatibilidad."""
        return self.get_user_by_chat_id(chat_id)

    def is_user_registered(self, chat_id: int) -> bool:
        try:
            query = text("""
                SELECT COUNT(*) FROM abcmasplus..UsuariosTelegram
                WHERE telegramChatId = :chat_id AND activo = 1
            """)
            count = self.session.execute(query, {"chat_id": chat_id}).scalar()
            return count > 0
        except Exception as e:
            logger.error(f"Error verificando registro de chat_id {chat_id}: {e}")
            return False

    def get_registration_info(self, chat_id: int) -> Optional[dict]:
        try:
            query = text("""
                SELECT idUsuario, verificado, estado
                FROM abcmasplus..UsuariosTelegram
                WHERE telegramChatId = :chat_id AND activo = 1
            """)
            result = self.session.execute(query, {"chat_id": chat_id})
            row = result.fetchone()
            return dict(zip(result.keys(), row)) if row else None
        except Exception as e:
            logger.error(f"Error obteniendo info de registro para chat_id {chat_id}: {e}")
            return None

    def update_last_activity(self, chat_id: int) -> bool:
        try:
            query = text("""
                UPDATE abcmasplus..UsuariosTelegram
                SET fechaUltimaActividad = GETDATE()
                WHERE telegramChatId = :chat_id AND activo = 1
            """)
            result = self.session.execute(query, {"chat_id": chat_id})
            self.session.commit()
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error actualizando última actividad para chat_id {chat_id}: {e}")
            self.session.rollback()
            return False

    def get_user_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        try:
            query = text("""
                SELECT
                    COUNT(*) AS totalOperaciones,
                    SUM(CASE WHEN resultado = 'EXITOSO' THEN 1 ELSE 0 END) AS exitosas,
                    SUM(CASE WHEN resultado = 'ERROR' THEN 1 ELSE 0 END) AS errores,
                    SUM(CASE WHEN resultado = 'DENEGADO' THEN 1 ELSE 0 END) AS denegadas,
                    AVG(CAST(duracionMs AS FLOAT)) AS duracionPromedio,
                    MAX(fechaEjecucion) AS ultimaOperacion
                FROM abcmasplus..LogOperaciones
                WHERE idUsuario = :user_id
            """)
            result = self.session.execute(query, {"user_id": user_id})
            row = result.fetchone()
            return dict(zip(result.keys(), row)) if row else None
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas del usuario {user_id}: {e}")
            raise

    def get_all_user_telegram_accounts(self, user_id: int) -> list:
        try:
            query = text("""
                SELECT
                    idUsuarioTelegram, telegramChatId, telegramUsername,
                    alias, esPrincipal, estado, verificado,
                    fechaRegistro, fechaUltimaActividad
                FROM abcmasplus..UsuariosTelegram
                WHERE idUsuario = :user_id AND activo = 1
                ORDER BY esPrincipal DESC, fechaRegistro DESC
            """)
            result = self.session.execute(query, {"user_id": user_id})
            rows = result.fetchall()
            return [dict(zip(result.keys(), row)) for row in rows]
        except Exception as e:
            logger.error(f"Error obteniendo cuentas de Telegram del usuario {user_id}: {e}")
            raise

    # -------------------------------------------------------------------------
    # Consultas de registro
    # -------------------------------------------------------------------------

    def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        try:
            query = text("""
                SELECT idUsuario, Nombre, email, idRol, puesto, Activa
                FROM abcmasplus..Usuarios
                WHERE email = :email AND Activa = 1
            """)
            result = self.session.execute(query, {"email": email})
            row = result.fetchone()
            return dict(zip(result.keys(), row)) if row else None
        except Exception as e:
            logger.error(f"Error buscando usuario por email {email}: {e}")
            raise

    def find_user_by_employee_id(self, employee_id: int) -> Optional[Dict[str, Any]]:
        try:
            query = text("""
                SELECT idUsuario, Nombre, email, idRol, puesto, Activa
                FROM abcmasplus..Usuarios
                WHERE idUsuario = :employee_id AND Activa = 1
            """)
            result = self.session.execute(query, {"employee_id": employee_id})
            row = result.fetchone()
            return dict(zip(result.keys(), row)) if row else None
        except Exception as e:
            logger.error(f"Error buscando usuario por employee_id {employee_id}: {e}")
            raise

    def has_telegram_account(self, chat_id: int) -> bool:
        query = text("""
            SELECT COUNT(*) FROM abcmasplus..UsuariosTelegram
            WHERE telegramChatId = :chat_id AND activo = 1
        """)
        return self.session.execute(query, {"chat_id": chat_id}).scalar() > 0

    def has_principal_account(self, user_id: int) -> bool:
        query = text("""
            SELECT COUNT(*) FROM abcmasplus..UsuariosTelegram
            WHERE idUsuario = :user_id AND esPrincipal = 1 AND activo = 1
        """)
        return self.session.execute(query, {"user_id": user_id}).scalar() > 0

    def insert_telegram_account(
        self,
        user_id: int,
        chat_id: int,
        verification_code: str,
        es_principal: bool,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        alias: Optional[str] = None
    ) -> None:
        query = text("""
            INSERT INTO abcmasplus..UsuariosTelegram (
                idUsuario, telegramChatId, telegramUsername,
                telegramFirstName, telegramLastName, alias,
                esPrincipal, estado, codigoVerificacion,
                verificado, intentosVerificacion, fechaRegistro, activo
            ) VALUES (
                :user_id, :chat_id, :username, :first_name, :last_name,
                :alias, :es_principal, 'ACTIVO', :verification_code,
                0, 0, GETDATE(), 1
            )
        """)
        self.session.execute(query, {
            "user_id": user_id, "chat_id": chat_id, "username": username,
            "first_name": first_name, "last_name": last_name, "alias": alias,
            "es_principal": 1 if es_principal else 0,
            "verification_code": verification_code
        })
        self.session.commit()

    def get_pending_verification(self, chat_id: int) -> Optional[Dict[str, Any]]:
        query = text("""
            SELECT idUsuarioTelegram, idUsuario, codigoVerificacion,
                   intentosVerificacion, fechaRegistro, verificado
            FROM abcmasplus..UsuariosTelegram
            WHERE telegramChatId = :chat_id AND activo = 1
        """)
        result = self.session.execute(query, {"chat_id": chat_id})
        row = result.fetchone()
        return dict(zip(result.keys(), row)) if row else None

    def mark_account_verified(self, chat_id: int) -> None:
        query = text("""
            UPDATE abcmasplus..UsuariosTelegram
            SET verificado = 1, fechaVerificacion = GETDATE(), codigoVerificacion = NULL
            WHERE telegramChatId = :chat_id
        """)
        self.session.execute(query, {"chat_id": chat_id})
        self.session.commit()

    def increment_verification_attempts(self, chat_id: int) -> None:
        query = text("""
            UPDATE abcmasplus..UsuariosTelegram
            SET intentosVerificacion = intentosVerificacion + 1
            WHERE telegramChatId = :chat_id
        """)
        self.session.execute(query, {"chat_id": chat_id})
        self.session.commit()

    def update_verification_code(self, chat_id: int, new_code: str) -> None:
        query = text("""
            UPDATE abcmasplus..UsuariosTelegram
            SET codigoVerificacion = :new_code,
                intentosVerificacion = 0,
                fechaRegistro = GETDATE()
            WHERE telegramChatId = :chat_id
        """)
        self.session.execute(query, {"new_code": new_code, "chat_id": chat_id})
        self.session.commit()

    def block_account(self, chat_id: int) -> None:
        try:
            query = text("""
                UPDATE abcmasplus..UsuariosTelegram
                SET estado = 'BLOQUEADO'
                WHERE telegramChatId = :chat_id
            """)
            self.session.execute(query, {"chat_id": chat_id})
            self.session.commit()
            logger.warning(f"Cuenta bloqueada: chat_id={chat_id}")
        except Exception as e:
            logger.error(f"Error bloqueando cuenta: {e}")
            self.session.rollback()

    def get_registration_status(self, chat_id: int) -> Optional[Dict[str, Any]]:
        try:
            query = text("""
                SELECT ut.verificado, ut.estado, ut.intentosVerificacion,
                       ut.fechaRegistro, u.Nombre, u.email
                FROM abcmasplus..UsuariosTelegram ut
                INNER JOIN abcmasplus..Usuarios u ON ut.idUsuario = u.idUsuario
                WHERE ut.telegramChatId = :chat_id AND ut.activo = 1
            """)
            result = self.session.execute(query, {"chat_id": chat_id})
            row = result.fetchone()
            return dict(zip(result.keys(), row)) if row else None
        except Exception as e:
            logger.error(f"Error obteniendo estado de registro: {e}")
            raise

    # -------------------------------------------------------------------------
    # Consultas de permisos
    # -------------------------------------------------------------------------

    def check_permission(self, user_id: int, comando: str) -> PermissionResult:
        try:
            query = text("""
                EXEC abcmasplus..sp_VerificarPermisoOperacion
                    @idUsuario = :user_id, @comando = :comando
            """)
            result = self.session.execute(query, {"user_id": user_id, "comando": comando})
            row = result.fetchone()
            if row:
                return PermissionResult(dict(zip(result.keys(), row)))
            return PermissionResult({'TienePermiso': False, 'Mensaje': 'Operación no encontrada'})
        except Exception as e:
            logger.error(f"Error verificando permiso para usuario {user_id}, comando {comando}: {e}")
            raise

    def get_user_operations(self, user_id: int) -> List[Operation]:
        try:
            query = text("""
                EXEC abcmasplus..sp_ObtenerOperacionesUsuario @idUsuario = :user_id
            """)
            result = self.session.execute(query, {"user_id": user_id})
            rows = result.fetchall()
            return [Operation(dict(zip(result.keys(), row))) for row in rows]
        except Exception as e:
            logger.error(f"Error obteniendo operaciones del usuario {user_id}: {e}")
            raise

    def log_operation(
        self,
        user_id: int,
        comando: str,
        telegram_chat_id: Optional[int] = None,
        telegram_username: Optional[str] = None,
        parametros: Optional[Dict[str, Any]] = None,
        resultado: str = 'EXITOSO',
        mensaje_error: Optional[str] = None,
        duracion_ms: Optional[int] = None,
        ip_origen: Optional[str] = None
    ) -> bool:
        try:
            parametros_json = json.dumps(parametros, ensure_ascii=False) if parametros else None
            query = text("""
                EXEC abcmasplus..sp_RegistrarLogOperacion
                    @idUsuario = :user_id, @comando = :comando,
                    @telegramChatId = :telegram_chat_id,
                    @telegramUsername = :telegram_username,
                    @parametros = :parametros, @resultado = :resultado,
                    @mensajeError = :mensaje_error, @duracionMs = :duracion_ms,
                    @ipOrigen = :ip_origen
            """)
            self.session.execute(query, {
                "user_id": user_id, "comando": comando,
                "telegram_chat_id": telegram_chat_id,
                "telegram_username": telegram_username,
                "parametros": parametros_json, "resultado": resultado,
                "mensaje_error": mensaje_error, "duracion_ms": duracion_ms,
                "ip_origen": ip_origen
            })
            self.session.commit()
            logger.info(f"Log registrado: usuario={user_id}, comando={comando}, resultado={resultado}")
            return True
        except Exception as e:
            logger.error(f"Error registrando log de operación: {e}")
            self.session.rollback()
            return False
