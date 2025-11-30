"""
Tests para KnowledgeRepository.

Valida lectura desde base de datos y conversión a objetos KnowledgeEntry.
"""
import pytest
from unittest.mock import Mock, MagicMock
from src.agent.knowledge import KnowledgeRepository, KnowledgeEntry, KnowledgeCategory


class TestKnowledgeRepositoryInitialization:
    """Tests de inicialización del repositorio."""

    def test_initialization_without_db_manager(self):
        """Debe inicializar con db_manager por defecto."""
        repo = KnowledgeRepository()
        assert repo is not None
        assert repo.db_manager is not None

    def test_initialization_with_db_manager(self):
        """Debe aceptar db_manager personalizado."""
        mock_db = Mock()
        repo = KnowledgeRepository(db_manager=mock_db)
        assert repo.db_manager is mock_db


class TestKnowledgeRepositoryRowConversion:
    """Tests de conversión de filas BD a objetos."""

    @pytest.fixture
    def repo(self):
        """Fixture del repositorio."""
        mock_db = Mock()
        return KnowledgeRepository(db_manager=mock_db)

    def test_row_to_entry_complete(self, repo):
        """Debe convertir fila completa correctamente."""
        row = {
            'id': 1,
            'category_name': 'FAQS',
            'question': '¿Cómo solicito vacaciones?',
            'answer': 'Debes ingresar al portal...',
            'keywords': '["vacaciones", "solicitar"]',
            'related_commands': '["/help"]',
            'priority': 2
        }

        entry = repo._row_to_entry(row)

        assert entry is not None
        assert isinstance(entry, KnowledgeEntry)
        assert entry.category == KnowledgeCategory.FAQS
        assert entry.question == '¿Cómo solicito vacaciones?'
        assert 'vacaciones' in entry.keywords
        assert entry.related_commands == ['/help']
        assert entry.priority == 2

    def test_row_to_entry_without_related_commands(self, repo):
        """Debe manejar entradas sin related_commands."""
        row = {
            'category_name': 'POLITICAS',
            'question': '¿Cuál es el horario?',
            'answer': 'El horario es 9-5',
            'keywords': '["horario", "trabajo"]',
            'related_commands': None,
            'priority': 1
        }

        entry = repo._row_to_entry(row)

        assert entry is not None
        assert entry.related_commands is None

    def test_row_to_entry_with_invalid_json(self, repo):
        """Debe manejar JSON inválido gracefully."""
        row = {
            'id': 1,
            'category_name': 'FAQS',
            'question': 'Test',
            'answer': 'Test answer',
            'keywords': 'invalid json',
            'related_commands': None,
            'priority': 1
        }

        entry = repo._row_to_entry(row)

        assert entry is not None
        assert entry.keywords == []  # Debe usar lista vacía como fallback

    def test_row_to_entry_with_unknown_category(self, repo):
        """Debe retornar None si categoría es desconocida."""
        row = {
            'category_name': 'UNKNOWN_CATEGORY',
            'question': 'Test',
            'answer': 'Test',
            'keywords': '[]',
            'priority': 1
        }

        entry = repo._row_to_entry(row)
        assert entry is None

    def test_row_to_entry_without_category(self, repo):
        """Debe retornar None si no hay categoría."""
        row = {
            'question': 'Test',
            'answer': 'Test',
            'keywords': '[]',
            'priority': 1
        }

        entry = repo._row_to_entry(row)
        assert entry is None


class TestKnowledgeRepositoryHealthCheck:
    """Tests de health check."""

    def test_health_check_success(self):
        """Debe retornar True si BD responde."""
        mock_db = Mock()
        mock_db.execute_query.return_value = [{'total': 10}]

        repo = KnowledgeRepository(db_manager=mock_db)
        result = repo.health_check()

        assert result is True
        mock_db.execute_query.assert_called_once()

    def test_health_check_failure(self):
        """Debe retornar False si BD falla."""
        mock_db = Mock()
        mock_db.execute_query.side_effect = Exception("Connection error")

        repo = KnowledgeRepository(db_manager=mock_db)
        result = repo.health_check()

        assert result is False

    def test_health_check_empty_result(self):
        """Debe retornar False si result es vacío."""
        mock_db = Mock()
        mock_db.execute_query.return_value = []

        repo = KnowledgeRepository(db_manager=mock_db)
        result = repo.health_check()

        assert result is False


class TestKnowledgeRepositoryGetAllEntries:
    """Tests de obtención de todas las entradas."""

    def test_get_all_entries_success(self):
        """Debe retornar lista de entradas."""
        mock_db = Mock()
        mock_db.execute_query.return_value = [
            {
                'id': 1,
                'category_name': 'FAQS',
                'question': 'Test 1',
                'answer': 'Answer 1',
                'keywords': '["test"]',
                'related_commands': None,
                'priority': 1
            },
            {
                'id': 2,
                'category_name': 'POLITICAS',
                'question': 'Test 2',
                'answer': 'Answer 2',
                'keywords': '["policy"]',
                'related_commands': '["/help"]',
                'priority': 2
            }
        ]

        repo = KnowledgeRepository(db_manager=mock_db)
        entries = repo.get_all_entries()

        assert len(entries) == 2
        assert all(isinstance(e, KnowledgeEntry) for e in entries)
        assert entries[0].question == 'Test 1'
        assert entries[1].priority == 2

    def test_get_all_entries_filters_invalid(self):
        """Debe filtrar filas que no se pueden convertir."""
        mock_db = Mock()
        mock_db.execute_query.return_value = [
            {
                'id': 1,
                'category_name': 'FAQS',
                'question': 'Valid',
                'answer': 'Answer',
                'keywords': '["test"]',
                'priority': 1
            },
            {
                'id': 2,
                'category_name': 'INVALID_CAT',  # Categoría inválida
                'question': 'Invalid',
                'answer': 'Answer',
                'keywords': '["test"]',
                'priority': 1
            }
        ]

        repo = KnowledgeRepository(db_manager=mock_db)
        entries = repo.get_all_entries()

        # Solo debe retornar la entrada válida
        assert len(entries) == 1
        assert entries[0].question == 'Valid'

    def test_get_all_entries_db_error_raises(self):
        """Debe propagar excepción de BD."""
        mock_db = Mock()
        mock_db.execute_query.side_effect = Exception("DB Error")

        repo = KnowledgeRepository(db_manager=mock_db)

        with pytest.raises(Exception):
            repo.get_all_entries()


class TestKnowledgeRepositoryGetByCategory:
    """Tests de búsqueda por categoría."""

    def test_get_entries_by_category_success(self):
        """Debe retornar entradas de categoría específica."""
        mock_db = Mock()
        mock_db.execute_query.return_value = [
            {
                'category_name': 'FAQS',
                'question': 'FAQ 1',
                'answer': 'Answer 1',
                'keywords': '["faq"]',
                'priority': 1
            }
        ]

        repo = KnowledgeRepository(db_manager=mock_db)
        entries = repo.get_entries_by_category(KnowledgeCategory.FAQS)

        assert len(entries) == 1
        assert entries[0].category == KnowledgeCategory.FAQS
        mock_db.execute_query.assert_called_once()

    def test_get_entries_by_category_empty(self):
        """Debe retornar lista vacía si no hay resultados."""
        mock_db = Mock()
        mock_db.execute_query.return_value = []

        repo = KnowledgeRepository(db_manager=mock_db)
        entries = repo.get_entries_by_category(KnowledgeCategory.SISTEMAS)

        assert entries == []
