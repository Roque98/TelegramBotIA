"""
Tests para src/infra/database/

Cobertura:
- SQLValidator: validate, is_safe_query, helpers internos
- DatabaseManager: execute_query, execute_non_query, get_session (con engine mockeado)
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from src.infra.database.sql_validator import SQLValidator


# ===========================================================================
# SQLValidator
# ===========================================================================

@pytest.fixture
def validator():
    return SQLValidator()


class TestSQLValidatorValid:

    def test_simple_select(self, validator):
        ok, err = validator.validate("SELECT * FROM Ventas")
        assert ok is True
        assert err == ""

    def test_select_with_where(self, validator):
        ok, err = validator.validate("SELECT id, nombre FROM Usuarios WHERE activo = 1")
        assert ok is True

    def test_select_with_join(self, validator):
        ok, err = validator.validate(
            "SELECT v.id, u.nombre FROM Ventas v JOIN Usuarios u ON v.user_id = u.id"
        )
        assert ok is True

    def test_select_with_trailing_semicolon(self, validator):
        ok, err = validator.validate("SELECT 1;")
        assert ok is True

    def test_select_lowercase(self, validator):
        ok, err = validator.validate("select * from tabla")
        assert ok is True

    def test_select_mixed_case(self, validator):
        ok, err = validator.validate("Select * From Tabla")
        assert ok is True


class TestSQLValidatorInvalid:

    def test_empty_query(self, validator):
        ok, err = validator.validate("")
        assert ok is False
        assert "vacía" in err

    def test_whitespace_only(self, validator):
        ok, err = validator.validate("   ")
        assert ok is False

    def test_not_select(self, validator):
        ok, err = validator.validate("SHOW TABLES")
        assert ok is False
        assert "SELECT" in err

    def test_drop_table(self, validator):
        # Falla antes de llegar al check de keywords (no comienza con SELECT)
        ok, err = validator.validate("DROP TABLE Usuarios")
        assert ok is False

    def test_delete(self, validator):
        ok, err = validator.validate("DELETE FROM Usuarios WHERE id = 1")
        assert ok is False

    def test_update(self, validator):
        ok, err = validator.validate("UPDATE Usuarios SET activo = 0")
        assert ok is False

    def test_insert(self, validator):
        ok, err = validator.validate("INSERT INTO Usuarios VALUES (1, 'test')")
        assert ok is False

    def test_truncate(self, validator):
        ok, err = validator.validate("TRUNCATE TABLE Logs")
        assert ok is False

    def test_alter(self, validator):
        ok, err = validator.validate("ALTER TABLE Usuarios ADD COLUMN email VARCHAR(100)")
        assert ok is False

    def test_exec(self, validator):
        ok, err = validator.validate("EXEC sp_help")
        assert ok is False

    def test_create(self, validator):
        ok, err = validator.validate("CREATE TABLE nueva (id INT)")
        assert ok is False

    def test_grant(self, validator):
        ok, err = validator.validate("GRANT SELECT ON tabla TO usuario")
        assert ok is False

    def test_xp_cmdshell(self, validator):
        ok, err = validator.validate("SELECT xp_cmdshell('dir')")
        assert ok is False
        assert "xp_cmdshell" in err

    def test_sp_executesql(self, validator):
        ok, err = validator.validate("SELECT sp_executesql")
        assert ok is False

    def test_openrowset(self, validator):
        ok, err = validator.validate("SELECT * FROM openrowset('Provider', 'conn', 'query')")
        assert ok is False

    def test_multiple_statements(self, validator):
        ok, err = validator.validate("SELECT 1; SELECT 2")
        assert ok is False
        assert "múltiples" in err

    def test_suspicious_comment_with_drop(self, validator):
        # XDROP contiene DROP como substring (elude \bDROP\b del paso 4),
        # pero _has_suspicious_comments lo detecta como substring en comentario
        ok, err = validator.validate("SELECT 1 /* XDROP */")
        assert ok is False
        assert "comentarios" in err

    def test_forbidden_keyword_in_subquery(self, validator):
        """DELETE dentro de un SELECT debe ser detectado."""
        ok, err = validator.validate("SELECT (DELETE FROM tabla)")
        assert ok is False


class TestSQLValidatorHelpers:

    def test_contains_keyword_with_boundary(self, validator):
        """SELECTED no debe detectarse como SELECT."""
        assert not validator._contains_keyword("SELECTED", "SELECT")
        assert validator._contains_keyword("SELECT * FROM t", "SELECT")

    def test_has_multiple_statements_false(self, validator):
        assert not validator._has_multiple_statements("SELECT 1")
        assert not validator._has_multiple_statements("SELECT 1;")

    def test_has_multiple_statements_true(self, validator):
        assert validator._has_multiple_statements("SELECT 1; SELECT 2")

    def test_has_multiple_statements_ignores_string_semicolons(self, validator):
        """Punto y coma dentro de string no es múltiple statement."""
        assert not validator._has_multiple_statements("SELECT 'val;ue' FROM t")

    def test_has_suspicious_comments_clean(self, validator):
        assert not validator._has_suspicious_comments("SELECT 1 /* comentario normal */")

    def test_has_suspicious_comments_with_keyword(self, validator):
        assert validator._has_suspicious_comments("SELECT 1 /* DROP TABLE x */")

    def test_is_safe_query_true(self, validator):
        assert validator.is_safe_query("SELECT * FROM Tabla") is True

    def test_is_safe_query_false(self, validator):
        assert validator.is_safe_query("DROP TABLE Tabla") is False


# ===========================================================================
# DatabaseManager — mockeando create_engine para no necesitar BD real
# ===========================================================================

class TestDatabaseManagerExecuteQuery:

    @pytest.fixture
    def mock_db(self):
        """DatabaseManager con engine y sesión totalmente mockeados."""
        with patch("src.infra.database.connection.create_engine") as mock_engine, \
             patch("src.infra.database.connection.sessionmaker") as mock_session_maker:

            mock_engine.return_value = MagicMock()
            mock_session_maker.return_value = MagicMock()

            from src.infra.database.connection import DatabaseManager
            db = DatabaseManager.__new__(DatabaseManager)
            db.engine = mock_engine.return_value
            db.SessionLocal = MagicMock()

            yield db

    def test_execute_query_rejects_non_select(self, mock_db):
        with pytest.raises(ValueError, match="SELECT"):
            mock_db.execute_query("UPDATE tabla SET x = 1")

    def test_execute_query_rejects_delete(self, mock_db):
        with pytest.raises(ValueError):
            mock_db.execute_query("DELETE FROM tabla")

    def test_execute_non_query_rejects_select(self, mock_db):
        with pytest.raises(ValueError, match="escritura"):
            mock_db.execute_non_query("SELECT * FROM tabla")

    def test_execute_query_returns_rows(self, mock_db):
        """execute_query con sesión mockeada devuelve lista de dicts."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [(1, "test")]
        mock_result.keys.return_value = ["id", "nombre"]
        mock_session.execute.return_value = mock_result
        mock_session.commit.return_value = None
        mock_session.close.return_value = None

        mock_db.SessionLocal.return_value = mock_session

        result = mock_db.execute_query("SELECT id, nombre FROM tabla")

        assert isinstance(result, list)
        assert result[0]["id"] == 1
        assert result[0]["nombre"] == "test"

    def test_execute_query_returns_empty_when_no_rows(self, mock_db):
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_session.execute.return_value = mock_result
        mock_session.commit.return_value = None
        mock_session.close.return_value = None

        mock_db.SessionLocal.return_value = mock_session

        result = mock_db.execute_query("SELECT * FROM tabla")
        assert result == []

    def test_execute_non_query_returns_rowcount(self, mock_db):
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.rowcount = 3
        mock_session.execute.return_value = mock_result
        mock_session.commit.return_value = None
        mock_session.close.return_value = None

        mock_db.SessionLocal.return_value = mock_session

        result = mock_db.execute_non_query("INSERT INTO tabla VALUES (1)")
        assert result == 3

    def test_execute_query_allows_exec(self, mock_db):
        """EXEC para stored procedures debe ser permitido."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_session.execute.return_value = mock_result
        mock_session.commit.return_value = None
        mock_session.close.return_value = None

        mock_db.SessionLocal.return_value = mock_session

        result = mock_db.execute_query("EXEC sp_stored_procedure")
        assert result == []

    @pytest.mark.asyncio
    async def test_execute_query_async_delegates(self, mock_db):
        """execute_query_async debe llamar execute_query en thread."""
        mock_db.execute_query = MagicMock(return_value=[{"id": 1}])

        result = await mock_db.execute_query_async("SELECT 1")
        mock_db.execute_query.assert_called_once_with("SELECT 1", None)
        assert result == [{"id": 1}]

    @pytest.mark.asyncio
    async def test_execute_non_query_async_delegates(self, mock_db):
        mock_db.execute_non_query = MagicMock(return_value=5)

        result = await mock_db.execute_non_query_async("INSERT INTO t VALUES (1)")
        mock_db.execute_non_query.assert_called_once()
        assert result == 5

    def test_close_disposes_engine(self, mock_db):
        mock_db.close()
        mock_db.engine.dispose.assert_called_once()
