"""
Tests para src/domain/knowledge/

Cobertura:
- KnowledgeCategory: enum, display names
- KnowledgeEntry: dataclass
- KnowledgeService: search, scoring, category detection, stats
"""
import pytest
from unittest.mock import MagicMock, patch

from src.domain.knowledge.knowledge_entity import KnowledgeCategory, KnowledgeEntry
from src.domain.knowledge.knowledge_service import KnowledgeService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_entry(
    category=KnowledgeCategory.FAQS,
    question="¿Cómo pido vacaciones?",
    answer="Debes solicitarlas en el sistema RRHH.",
    keywords=None,
    priority=1,
):
    return KnowledgeEntry(
        category=category,
        question=question,
        answer=answer,
        keywords=keywords or ["vacaciones", "permiso"],
        priority=priority,
    )


def make_service(entries=None):
    """Crea KnowledgeService con repositorio mockeado."""
    mock_repo = MagicMock()
    mock_repo.health_check.return_value = True
    mock_repo.get_all_entries.return_value = entries or [make_entry()]

    with patch(
        "src.domain.knowledge.knowledge_service.KnowledgeRepository",
        return_value=mock_repo,
    ):
        service = KnowledgeService()

    return service


# ---------------------------------------------------------------------------
# KnowledgeCategory
# ---------------------------------------------------------------------------

class TestKnowledgeCategory:

    def test_get_all_returns_all_categories(self):
        categories = KnowledgeCategory.get_all()
        assert KnowledgeCategory.FAQS in categories
        assert KnowledgeCategory.POLITICAS in categories
        assert len(categories) == 7

    def test_get_display_name(self):
        assert KnowledgeCategory.get_display_name(KnowledgeCategory.FAQS) == "Preguntas Frecuentes"
        assert KnowledgeCategory.get_display_name(KnowledgeCategory.PROCESOS) == "Procesos"
        assert KnowledgeCategory.get_display_name(KnowledgeCategory.RECURSOS_HUMANOS) == "Recursos Humanos"

    def test_str_returns_value(self):
        assert str(KnowledgeCategory.PROCESOS) == "procesos"


# ---------------------------------------------------------------------------
# KnowledgeEntry
# ---------------------------------------------------------------------------

class TestKnowledgeEntry:

    def test_repr_truncates_question(self):
        entry = make_entry(question="A" * 100)
        assert "KnowledgeEntry" in repr(entry)
        assert "faqs" in repr(entry)

    def test_default_related_commands_empty(self):
        entry = make_entry()
        assert entry.related_commands == []

    def test_priority_default(self):
        entry = make_entry()
        assert entry.priority == 1


# ---------------------------------------------------------------------------
# KnowledgeService — inicialización
# ---------------------------------------------------------------------------

class TestKnowledgeServiceInit:

    def test_raises_when_db_unavailable(self):
        mock_repo = MagicMock()
        mock_repo.health_check.return_value = False

        with patch(
            "src.domain.knowledge.knowledge_service.KnowledgeRepository",
            return_value=mock_repo,
        ):
            with pytest.raises(RuntimeError, match="Base de datos no disponible"):
                KnowledgeService()

    def test_raises_when_no_entries(self):
        mock_repo = MagicMock()
        mock_repo.health_check.return_value = True
        mock_repo.get_all_entries.return_value = []

        with patch(
            "src.domain.knowledge.knowledge_service.KnowledgeRepository",
            return_value=mock_repo,
        ):
            with pytest.raises(RuntimeError):
                KnowledgeService()

    def test_source_is_database_on_success(self):
        service = make_service()
        assert service.get_source() == "database"

    def test_init_with_role_filter(self):
        mock_repo = MagicMock()
        mock_repo.health_check.return_value = True
        mock_repo.get_all_entries_by_role.return_value = [make_entry()]

        with patch(
            "src.domain.knowledge.knowledge_service.KnowledgeRepository",
            return_value=mock_repo,
        ):
            service = KnowledgeService(id_rol=2)

        mock_repo.get_all_entries_by_role.assert_called_once_with(2)
        assert service.id_rol == 2


# ---------------------------------------------------------------------------
# KnowledgeService — search y scoring
# ---------------------------------------------------------------------------

class TestKnowledgeServiceSearch:

    def test_search_returns_matching_entry(self):
        service = make_service([
            make_entry(question="¿Cómo pido vacaciones?", keywords=["vacaciones"]),
        ])
        results = service.search("vacaciones")
        assert len(results) == 1

    def test_search_min_score_filters_out(self):
        service = make_service([
            make_entry(question="Sistemas internos", keywords=["ERP"]),
        ])
        results = service.search("vacaciones", min_score=0.5)
        assert len(results) == 0

    def test_search_respects_top_k(self):
        entries = [
            make_entry(question=f"Pregunta {i}", keywords=["permiso", "vacaciones"])
            for i in range(5)
        ]
        service = make_service(entries)
        results = service.search("vacaciones permiso", top_k=2)
        assert len(results) <= 2

    def test_search_category_filter_boosts_matching_category(self):
        """El filtro de categoría agrega boost +0.3 a las entradas que coinciden."""
        entries = [
            make_entry(category=KnowledgeCategory.FAQS, keywords=["permiso", "vacaciones"]),
            make_entry(category=KnowledgeCategory.POLITICAS, keywords=["permiso", "vacaciones"]),
        ]
        service = make_service(entries)
        # Con las mismas keywords, el boost de FAQS debe hacer que aparezca primero
        results = service.search("permiso vacaciones", category_filter=KnowledgeCategory.FAQS, top_k=2)
        assert len(results) >= 1
        assert results[0].category == KnowledgeCategory.FAQS

    def test_search_category_detection_in_query(self):
        entries = [
            make_entry(category=KnowledgeCategory.SISTEMAS, keywords=["erp", "sistema"]),
        ]
        service = make_service(entries)
        # "qué sabes sobre sistemas" dispara detección de categoría
        results = service.search("qué sabes sobre sistemas")
        assert len(results) == 1
        assert results[0].category == KnowledgeCategory.SISTEMAS

    def test_priority_multiplier_boosts_score(self):
        low_priority = make_entry(keywords=["bono"], priority=1)
        high_priority = make_entry(keywords=["bono"], question="¿Hay bonos?", priority=3)
        service = make_service([low_priority, high_priority])
        results = service.search("bono", top_k=2)
        assert results[0] == high_priority  # alta prioridad primero


# ---------------------------------------------------------------------------
# KnowledgeService — otros métodos
# ---------------------------------------------------------------------------

class TestKnowledgeServiceMethods:

    def test_get_entries_by_category(self):
        entries = [
            make_entry(category=KnowledgeCategory.FAQS),
            make_entry(category=KnowledgeCategory.POLITICAS),
        ]
        service = make_service(entries)
        results = service.get_entries_by_category(KnowledgeCategory.FAQS)
        assert all(e.category == KnowledgeCategory.FAQS for e in results)

    def test_get_all_categories(self):
        service = make_service()
        categories = service.get_all_categories()
        assert isinstance(categories, list)
        assert len(categories) == 7

    def test_find_by_keywords(self):
        service = make_service([make_entry(keywords=["vacaciones", "permiso"])])
        results = service.find_by_keywords(["vacaciones"])
        assert len(results) == 1

    def test_find_by_keywords_no_match(self):
        service = make_service([make_entry(keywords=["erp"])])
        results = service.find_by_keywords(["vacaciones"])
        assert results == []

    def test_get_high_priority_entries(self):
        entries = [
            make_entry(priority=1),
            make_entry(priority=2, question="Alta prioridad"),
            make_entry(priority=3, question="Crítica"),
        ]
        service = make_service(entries)
        high = service.get_high_priority_entries()
        assert all(e.priority >= 2 for e in high)
        assert len(high) == 2

    def test_get_stats(self):
        entries = [
            make_entry(category=KnowledgeCategory.FAQS, priority=1),
            make_entry(category=KnowledgeCategory.FAQS, priority=2),
            make_entry(category=KnowledgeCategory.POLITICAS, priority=3),
        ]
        service = make_service(entries)
        stats = service.get_stats()
        assert stats["total_entries"] == 3
        assert stats["categories"]["faqs"] == 2
        assert stats["priority_distribution"][3] == 1

    def test_get_context_for_llm_returns_empty_on_no_results(self):
        # Umbral min_score alto en search para que no haya resultados
        service = make_service([make_entry(keywords=["xyz_improbable_12345"])])
        ctx = service.get_context_for_llm("pregunta completamente diferente aaabbbccc", top_k=1)
        # La query no coincide con ninguna keyword ni word → score < threshold → ctx vacío
        assert ctx == ""

    def test_get_context_for_llm_contains_question(self):
        service = make_service([make_entry(question="¿Cómo pido vacaciones?", keywords=["vacaciones"])])
        ctx = service.get_context_for_llm("vacaciones", top_k=1)
        assert "vacaciones" in ctx.lower()

    def test_reload_from_database_success(self):
        service = make_service()
        new_entries = [make_entry(question="Nuevo")]
        service.repository.health_check.return_value = True
        service.repository.get_all_entries.return_value = new_entries
        result = service.reload_from_database()
        assert result is True
        assert service.knowledge_base == new_entries

    def test_reload_from_database_fails_gracefully(self):
        service = make_service()
        service.repository.health_check.return_value = False
        result = service.reload_from_database()
        assert result is False

    def test_repr(self):
        service = make_service()
        assert "KnowledgeService" in repr(service)

    def test_stem_es_strips_suffix(self):
        assert KnowledgeService._stem_es("vacaciones") != "vacaciones"  # debe truncar

    def test_clean_text_removes_punctuation(self):
        assert "?" not in KnowledgeService._clean_text("¿Cómo?")
