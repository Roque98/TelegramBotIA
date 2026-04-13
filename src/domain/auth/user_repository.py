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

    def get_user_by_chat_id(self, chat_id: int) -> Optional[TelegramUser]:
        try:
            query = text("EXEC abcmasplus..BotIAv2_sp_GetUsuarioByChatId @telegramChatId = :chat_id")
            result = self.session.execute(query, {"chat_id": chat_id})
            row = result.fetchone()
            return TelegramUser(dict(zip(result.keys(), row))) if row else None
        except Exception as e:
            logger.error(f"Error obteniendo usuario por chat_id {chat_id}: {e}")
            raise

    def get_user_by_id(self, user_id: int) -> Optional[TelegramUser]:
        try:
            query = text("EXEC abcmasplus..BotIAv2_sp_GetUsuarioById @idUsuario = :user_id")
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
            query = text("EXEC abcmasplus..BotIAv2_sp_EstaRegistrado @telegramChatId = :chat_id")
            result = self.session.execute(query, {"chat_id": chat_id})
            row = result.fetchone()
            return bool(row and row[0])
        except Exception as e:
            logger.error(f"Error verificando registro de chat_id {chat_id}: {e}")
            return False

    def get_registration_info(self, chat_id: int) -> Optional[dict]:
        try:
            query = text("EXEC abcmasplus..BotIAv2_sp_GetInfoRegistro @telegramChatId = :chat_id")
            result = self.session.execute(query, {"chat_id": chat_id})
            row = result.fetchone()
            return dict(zip(result.keys(), row)) if row else None
        except Exception as e:
            logger.error(f"Error obteniendo info de registro para chat_id {chat_id}: {e}")
            return None

    def update_last_activity(self, chat_id: int) -> bool:
        try:
            query = text("EXEC abcmasplus..BotIAv2_sp_ActualizarActividad @telegramChatId = :chat_id")
            result = self.session.execute(query, {"chat_id": chat_id})
            self.session.commit()
            row = result.fetchone()
            return bool(row and row[0] > 0)
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
            query = text("EXEC abcmasplus..BotIAv2_sp_GetCuentasTelegram @idUsuario = :user_id")
            result = self.session.execute(query, {"user_id": user_id})
            rows = result.fetchall()
            return [dict(zip(result.keys(), row)) for row in rows]
        except Exception as e:
            logger.error(f"Error obteniendo cuentas de Telegram del usuario {user_id}: {e}")
            raise

    def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        try:
            query = text("EXEC abcmasplus..BotIAv2_sp_BuscarPorEmail @email = :email")
            result = self.session.execute(query, {"email": email})
            row = result.fetchone()
            return dict(zip(result.keys(), row)) if row else None
        except Exception as e:
            logger.error(f"Error buscando usuario por email {email}: {e}")
            raise

    def find_user_by_employee_id(self, employee_id: int) -> Optional[Dict[str, Any]]:
        try:
            query = text("EXEC abcmasplus..BotIAv2_sp_GetUsuarioById @idUsuario = :employee_id")
            result = self.session.execute(query, {"employee_id": employee_id})
            row = result.fetchone()
            return dict(zip(result.keys(), row)) if row else None
        except Exception as e:
            logger.error(f"Error buscando usuario por employee_id {employee_id}: {e}")
            raise

    def has_telegram_account(self, chat_id: int) -> bool:
        query = text("EXEC abcmasplus..BotIAv2_sp_TieneCuentaTelegram @telegramChatId = :chat_id")
        result = self.session.execute(query, {"chat_id": chat_id})
        row = result.fetchone()
        return bool(row and row[0])

    def has_principal_account(self, user_id: int) -> bool:
        query = text("EXEC abcmasplus..BotIAv2_sp_TieneCuentaPrincipal @idUsuario = :user_id")
        result = self.session.execute(query, {"user_id": user_id})
        row = result.fetchone()
        return bool(row and row[0])

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
            EXEC abcmasplus..BotIAv2_sp_InsertarCuentaTelegram
                @idUsuario          = :user_id,
                @telegramChatId     = :chat_id,
                @telegramUsername   = :username,
                @telegramFirstName  = :first_name,
                @telegramLastName   = :last_name,
                @alias              = :alias,
                @esPrincipal        = :es_principal,
                @codigoVerificacion = :verification_code
        """)
        self.session.execute(query, {
            "user_id": user_id, "chat_id": chat_id, "username": username,
            "first_name": first_name, "last_name": last_name, "alias": alias,
            "es_principal": 1 if es_principal else 0,
            "verification_code": verification_code
        })
        self.session.commit()

    def get_pending_verification(self, chat_id: int) -> Optional[Dict[str, Any]]:
        query = text("EXEC abcmasplus..BotIAv2_sp_GetPendienteVerificacion @telegramChatId = :chat_id")
        result = self.session.execute(query, {"chat_id": chat_id})
        row = result.fetchone()
        return dict(zip(result.keys(), row)) if row else None

    def mark_account_verified(self, chat_id: int) -> None:
        query = text("EXEC abcmasplus..BotIAv2_sp_MarcarCuentaVerificada @telegramChatId = :chat_id")
        self.session.execute(query, {"chat_id": chat_id})
        self.session.commit()

    def increment_verification_attempts(self, chat_id: int) -> None:
        query = text("EXEC abcmasplus..BotIAv2_sp_IncrementarIntentos @telegramChatId = :chat_id")
        self.session.execute(query, {"chat_id": chat_id})
        self.session.commit()

    def update_verification_code(self, chat_id: int, new_code: str) -> None:
        query = text("""
            EXEC abcmasplus..BotIAv2_sp_ActualizarCodigoVerificacion
                @telegramChatId     = :chat_id,
                @codigoVerificacion = :new_code
        """)
        self.session.execute(query, {"new_code": new_code, "chat_id": chat_id})
        self.session.commit()

    def block_account(self, chat_id: int) -> None:
        try:
            query = text("EXEC abcmasplus..BotIAv2_sp_BloquearCuenta @telegramChatId = :chat_id")
            self.session.execute(query, {"chat_id": chat_id})
            self.session.commit()
            logger.warning(f"Cuenta bloqueada: chat_id={chat_id}")
        except Exception as e:
            logger.error(f"Error bloqueando cuenta: {e}")
            self.session.rollback()

    def get_registration_status(self, chat_id: int) -> Optional[Dict[str, Any]]:
        try:
            query = text("EXEC abcmasplus..BotIAv2_sp_GetEstadoRegistro @telegramChatId = :chat_id")
            result = self.session.execute(query, {"chat_id": chat_id})
            row = result.fetchone()
            return dict(zip(result.keys(), row)) if row else None
        except Exception as e:
            logger.error(f"Error obteniendo estado de registro: {e}")
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
