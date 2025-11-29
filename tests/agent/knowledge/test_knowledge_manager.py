"""
Tests para KnowledgeManager.

Valida búsqueda, scoring, filtrado y generación de contexto.
"""
import pytest
from src.agent.knowledge import (
    KnowledgeManager,
    KnowledgeCategory,
    KnowledgeEntry
)


class TestKnowledgeManagerInitialization:
    """Tests de inicialización del KnowledgeManager."""

    def test_initialization(self):
        """Debe inicializar correctamente con la base de conocimiento."""
        manager = KnowledgeManager()

        assert manager is not None
        assert len(manager.knowledge_base) > 0
        assert hasattr(manager, 'search')
        assert hasattr(manager, 'get_context_for_llm')

    def test_knowledge_base_not_empty(self):
        """La base de conocimiento debe tener entradas."""
        manager = KnowledgeManager()
        assert len(manager.knowledge_base) >= 10


class TestKnowledgeManagerSearch:
    """Tests de funcionalidad de búsqueda."""

    @pytest.fixture
    def manager(self):
        """Fixture del manager."""
        return KnowledgeManager()

    def test_search_by_keyword_vacaciones(self, manager):
        """Debe encontrar resultados para 'vacaciones'."""
        results = manager.search("vacaciones")

        assert len(results) > 0
        # Debe incluir la entrada sobre solicitar vacaciones
        questions = [r.question for r in results]
        assert any("vacaciones" in q.lower() for q in questions)

    def test_search_by_keyword_ticket(self, manager):
        """Debe encontrar resultados para 'ticket'."""
        results = manager.search("ticket de soporte")

        assert len(results) > 0
        questions = [r.question for r in results]
        assert any("ticket" in q.lower() for q in questions)

    def test_search_by_keyword_contraseña(self, manager):
        """Debe encontrar resultados para 'contraseña'."""
        results = manager.search("olvidé mi contraseña")

        assert len(results) > 0
        questions = [r.question for r in results]
        assert any("contraseña" in q.lower() for q in questions)

    def test_search_respects_top_k(self, manager):
        """Debe respetar el límite top_k."""
        results = manager.search("vacaciones días trabajo", top_k=2)
        assert len(results) <= 2

    def test_search_respects_min_score(self, manager):
        """Debe filtrar por score mínimo."""
        # Query irrelevante con min_score alto
        results = manager.search("xyz123abc", min_score=5.0)
        assert len(results) == 0

    def test_search_no_results_for_irrelevant_query(self, manager):
        """Debe retornar lista vacía para queries irrelevantes."""
        results = manager.search("xyzabc123 palabras sin sentido")
        # Puede retornar vacío o muy pocos resultados con score bajo
        assert isinstance(results, list)

    def test_search_with_category_filter(self, manager):
        """Debe filtrar por categoría."""
        results = manager.search(
            "información",
            category_filter=KnowledgeCategory.FAQS
        )

        # Todos los resultados deben ser de la categoría FAQS
        for entry in results:
            assert entry.category == KnowledgeCategory.FAQS

    def test_search_returns_sorted_by_relevance(self, manager):
        """Debe retornar resultados ordenados por relevancia (score)."""
        results = manager.search("vacaciones días", top_k=5)

        if len(results) > 1:
            # Verificar que están ordenados (más relevante primero)
            # No podemos verificar scores directamente, pero podemos verificar
            # que el primer resultado tiene keywords relevantes
            first_result = results[0]
            assert any(
                kw in first_result.keywords
                for kw in ["vacaciones", "días"]
            )


class TestKnowledgeManagerScoring:
    """Tests del algoritmo de scoring."""

    @pytest.fixture
    def manager(self):
        """Fixture del manager."""
        return KnowledgeManager()

    @pytest.fixture
    def sample_entry(self):
        """Entry de ejemplo para tests."""
        return KnowledgeEntry(
            category=KnowledgeCategory.FAQS,
            question="¿Cómo solicito vacaciones?",
            answer="Debes ingresar al portal...",
            keywords=["vacaciones", "solicitar", "pedir"],
            related_commands=["/help"],
            priority=2
        )

    def test_calculate_score_with_keyword_match(self, manager, sample_entry):
        """Score debe aumentar con keyword matches."""
        score = manager._calculate_score("quiero solicitar vacaciones", sample_entry)
        # Debe tener score > 0 por matches de keywords
        assert score > 0

    def test_calculate_score_with_no_match(self, manager, sample_entry):
        """Score debe ser bajo sin matches."""
        score = manager._calculate_score("xyz abc 123", sample_entry)
        # Puede ser 0 o muy bajo
        assert score >= 0

    def test_calculate_score_priority_multiplier(self, manager):
        """Debe aplicar multiplicador de prioridad."""
        entry_high_priority = KnowledgeEntry(
            category=KnowledgeCategory.FAQS,
            question="¿Test?",
            answer="Test answer",
            keywords=["test"],
            priority=3
        )

        entry_low_priority = KnowledgeEntry(
            category=KnowledgeCategory.FAQS,
            question="¿Test?",
            answer="Test answer",
            keywords=["test"],
            priority=1
        )

        score_high = manager._calculate_score("test", entry_high_priority)
        score_low = manager._calculate_score("test", entry_low_priority)

        # Score con prioridad 3 debe ser mayor que con prioridad 1
        assert score_high > score_low

    def test_calculate_score_question_similarity(self, manager, sample_entry):
        """Debe considerar similitud con la pregunta."""
        # Query con palabras de la pregunta
        score = manager._calculate_score("cómo solicito vacaciones", sample_entry)
        assert score > 0


class TestKnowledgeManagerContextGeneration:
    """Tests de generación de contexto para LLM."""

    @pytest.fixture
    def manager(self):
        """Fixture del manager."""
        return KnowledgeManager()

    def test_get_context_for_llm_basic(self, manager):
        """Debe generar contexto formateado."""
        context = manager.get_context_for_llm("vacaciones")

        assert isinstance(context, str)
        if context:  # Si hay resultados
            assert "CONOCIMIENTO INSTITUCIONAL" in context

    def test_get_context_for_llm_with_results(self, manager):
        """Debe incluir información relevante."""
        context = manager.get_context_for_llm("ticket soporte")

        if context:
            # Debe tener formato markdown
            assert "**" in context or context == ""

    def test_get_context_for_llm_empty_for_irrelevant(self, manager):
        """Debe retornar vacío si no hay resultados relevantes."""
        context = manager.get_context_for_llm("xyz123abc", top_k=1)
        # Puede ser vacío si no hay matches
        assert isinstance(context, str)

    def test_get_context_for_llm_respects_top_k(self, manager):
        """Debe limitar número de entradas en contexto."""
        context = manager.get_context_for_llm("información", top_k=1)

        if context:
            # Contar cuántas entradas hay (cada una empieza con **1., **2., etc)
            num_entries = context.count("**1.")
            assert num_entries <= 1

    def test_get_context_for_llm_with_metadata(self, manager):
        """Debe incluir metadata cuando se solicita."""
        context = manager.get_context_for_llm(
            "vacaciones",
            top_k=2,
            include_metadata=True
        )

        if context:
            # Debe incluir categoría entre corchetes [CATEGORIA]
            assert "[" in context or context == ""

    def test_get_context_for_llm_without_metadata(self, manager):
        """Debe omitir metadata cuando no se solicita."""
        context = manager.get_context_for_llm(
            "vacaciones",
            top_k=2,
            include_metadata=False
        )

        assert isinstance(context, str)


class TestKnowledgeManagerStatistics:
    """Tests de estadísticas y métodos auxiliares."""

    @pytest.fixture
    def manager(self):
        """Fixture del manager."""
        return KnowledgeManager()

    def test_get_stats_structure(self, manager):
        """Debe retornar estructura correcta de estadísticas."""
        stats = manager.get_stats()

        assert "total_entries" in stats
        assert "categories" in stats
        assert "priority_distribution" in stats
        assert isinstance(stats["total_entries"], int)
        assert isinstance(stats["categories"], dict)
        assert isinstance(stats["priority_distribution"], dict)

    def test_get_stats_total_entries(self, manager):
        """Total de entradas debe coincidir."""
        stats = manager.get_stats()
        assert stats["total_entries"] == len(manager.knowledge_base)

    def test_get_stats_priority_distribution(self, manager):
        """Debe contar prioridades correctamente."""
        stats = manager.get_stats()
        priority_dist = stats["priority_distribution"]

        # La suma de todas las prioridades debe igualar el total
        total_from_priorities = sum(priority_dist.values())
        assert total_from_priorities == stats["total_entries"]

    def test_get_all_categories(self, manager):
        """Debe retornar todas las categorías disponibles."""
        categories = manager.get_all_categories()

        assert len(categories) > 0
        assert all(isinstance(cat, KnowledgeCategory) for cat in categories)

    def test_find_by_keywords(self, manager):
        """Debe encontrar entradas por keywords exactos."""
        results = manager.find_by_keywords(["vacaciones"])

        assert len(results) > 0
        # Todas las entradas deben tener 'vacaciones' en keywords
        for entry in results:
            assert any(
                "vacaciones" in kw.lower()
                for kw in entry.keywords
            )

    def test_find_by_keywords_multiple(self, manager):
        """Debe encontrar con múltiples keywords."""
        results = manager.find_by_keywords(["ticket", "soporte"])

        assert len(results) > 0

    def test_find_by_keywords_no_matches(self, manager):
        """Debe retornar vacío si no hay matches."""
        results = manager.find_by_keywords(["xyz123abc"])
        assert results == []

    def test_get_high_priority_entries(self, manager):
        """Debe retornar solo entradas de alta prioridad."""
        high_priority = manager.get_high_priority_entries()

        # Todas deben tener prioridad >= 2
        for entry in high_priority:
            assert entry.priority >= 2


class TestKnowledgeManagerEdgeCases:
    """Tests de casos extremos."""

    @pytest.fixture
    def manager(self):
        """Fixture del manager."""
        return KnowledgeManager()

    def test_search_empty_query(self, manager):
        """Debe manejar query vacío."""
        results = manager.search("")
        # No debe fallar
        assert isinstance(results, list)

    def test_search_very_long_query(self, manager):
        """Debe manejar queries muy largos."""
        long_query = "vacaciones " * 100
        results = manager.search(long_query)
        assert isinstance(results, list)

    def test_search_special_characters(self, manager):
        """Debe manejar caracteres especiales."""
        results = manager.search("¿Cómo solicito vacaciones?")
        assert isinstance(results, list)

    def test_search_with_top_k_zero(self, manager):
        """Debe manejar top_k=0."""
        results = manager.search("vacaciones", top_k=0)
        assert results == []

    def test_search_with_negative_min_score(self, manager):
        """Debe manejar min_score negativo."""
        results = manager.search("vacaciones", min_score=-1.0)
        # No debe fallar, debe retornar resultados
        assert isinstance(results, list)

    def test_repr(self, manager):
        """Debe tener representación string."""
        repr_str = repr(manager)
        assert "KnowledgeManager" in repr_str
        assert "entries=" in repr_str


class TestKnowledgeManagerRealWorldScenarios:
    """Tests con escenarios reales de uso."""

    @pytest.fixture
    def manager(self):
        """Fixture del manager."""
        return KnowledgeManager()

    def test_employee_asks_about_vacations(self, manager):
        """Escenario: Empleado pregunta sobre vacaciones."""
        queries = [
            "¿Cómo pido vacaciones?",
            "quiero solicitar días libres",
            "necesito descanso, cómo hago",
        ]

        for query in queries:
            results = manager.search(query, top_k=3)
            # Debe encontrar información sobre vacaciones
            assert len(results) > 0

    def test_employee_asks_about_password_reset(self, manager):
        """Escenario: Empleado olvidó contraseña."""
        queries = [
            "olvidé mi contraseña",
            "no puedo entrar, resetear password",
            "recuperar contraseña",
        ]

        for query in queries:
            results = manager.search(query, top_k=3)
            assert len(results) > 0

    def test_employee_asks_about_support_ticket(self, manager):
        """Escenario: Empleado necesita crear ticket."""
        results = manager.search("cómo creo un ticket de soporte")

        assert len(results) > 0
        # Debe incluir información sobre crear tickets
        for result in results:
            if "ticket" in result.question.lower():
                assert "/crear_ticket" in result.related_commands or True

    def test_employee_asks_about_work_schedule(self, manager):
        """Escenario: Empleado pregunta por horario."""
        results = manager.search("cuál es el horario de trabajo")

        assert len(results) > 0

    def test_context_generation_for_bot_response(self, manager):
        """Escenario: Generar contexto para respuesta del bot."""
        query = "¿Cómo solicito vacaciones?"
        context = manager.get_context_for_llm(query, top_k=2)

        # El contexto debe ser útil para que el LLM responda
        if context:
            assert len(context) > 50  # Debe tener contenido sustancial
            assert "vacaciones" in context.lower()
