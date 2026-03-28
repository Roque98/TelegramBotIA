"""
Servicio de conocimiento empresarial.

Proporciona búsqueda inteligente en la base de conocimiento
usando keywords y scoring. Utiliza KnowledgeRepository para
todo acceso a base de datos.
"""
import logging
from typing import List, Optional, Dict, Any
from .knowledge_entity import KnowledgeEntry, KnowledgeCategory
from .knowledge_repository import KnowledgeRepository
from src.infra.database.connection import DatabaseManager

logger = logging.getLogger(__name__)


class KnowledgeService:
    """
    Servicio de conocimiento empresarial.

    Lee desde base de datos (abcmasplus) a través de KnowledgeRepository.
    Proporciona búsqueda por keywords y scoring inteligente.

    Examples:
        >>> service = KnowledgeService()
        >>> results = service.search("¿Cómo pido vacaciones?")
        >>> print(results[0].answer)
    """

    def __init__(self, db_manager: Optional[DatabaseManager] = None, id_rol: Optional[int] = None):
        self.repository = KnowledgeRepository(db_manager)
        self.knowledge_base = []
        self.source = "unknown"
        self.id_rol = id_rol

        try:
            if self.repository.health_check():
                if id_rol is not None:
                    self.knowledge_base = self.repository.get_all_entries_by_role(id_rol)
                    logger.info(f"✅ KnowledgeService inicializado desde BD para rol {id_rol} con {len(self.knowledge_base)} entradas")
                else:
                    self.knowledge_base = self.repository.get_all_entries()
                    logger.info(f"✅ KnowledgeService inicializado desde BD con {len(self.knowledge_base)} entradas (sin filtro de rol)")

                if self.knowledge_base:
                    self.source = "database"
                else:
                    if id_rol is not None:
                        logger.warning(f"Rol {id_rol} no tiene acceso a ninguna categoría de conocimiento")
                    else:
                        raise ValueError("Base de datos sin entradas")
            else:
                raise ConnectionError("Base de datos no disponible")

        except Exception as e:
            logger.error(f"❌ No se pudo cargar conocimiento desde BD: {e}")
            self.knowledge_base = []
            self.source = "none"
            raise RuntimeError(f"Base de datos no disponible y fallback deshabilitado: {e}")

    @staticmethod
    def _clean_text(text: str) -> str:
        import re
        return re.sub(r'[¿?¡!.,;:\-\'"(){}[\]]', '', text).strip()

    @staticmethod
    def _stem_es(word: str) -> str:
        if len(word) <= 4:
            return word
        for suffix in (
            "aciones", "iciones", "amiento", "imiento",
            "acion", "icion", "ando", "endo", "iendo",
            "ador", "edor", "idor",
            "ante", "ente", "iente",
            "able", "ible",
            "ción", "sión",
            "idad", "edad",
            "mente",
            "amos", "emos", "imos",
            "aron", "eron", "ieron",
            "ando", "endo",
            "ado", "ido",
            "aba", "ían",
            "ar", "er", "ir",
            "as", "es", "os",
            "an", "en",
            "ón", "or", "al",
            "o", "a",
        ):
            if word.endswith(suffix) and len(word) - len(suffix) >= 3:
                return word[: -len(suffix)]
        return word

    def _calculate_score(self, query: str, entry: KnowledgeEntry) -> float:
        score = 0.0
        query_words = set(query.split())
        query_stems = {self._stem_es(w) for w in query_words}

        for keyword in entry.keywords:
            kw = keyword.lower()
            if kw in query:
                score += 1.0
            elif self._stem_es(kw) in query_stems:
                score += 0.7

        clean_question = self._clean_text(entry.question.lower())
        question_words = set(clean_question.split())

        stopwords = {
            'qué', 'cómo', 'cuál', 'dónde', 'cuándo', 'cuántos',
            'por', 'para', 'el', 'la', 'los', 'las', 'de', 'del',
            'en', 'a', 'un', 'una', 'es', 'son', 'se', 'si', 'no',
            'que', 'como', 'cual', 'donde', 'cuando', 'hay', 'mi',
            'su', 'al', 'con', 'sin', 'sobre', 'entre', 'más', 'o',
            'y', 'e', 'ni', 'pero',
        }

        meaningful_query = query_words - stopwords
        meaningful_question = question_words - stopwords
        common_words = meaningful_query & meaningful_question
        score += len(common_words) * 0.3

        remaining_query_stems = {self._stem_es(w) for w in meaningful_query - common_words}
        remaining_question_stems = {self._stem_es(w) for w in meaningful_question - common_words}
        score += len(remaining_query_stems & remaining_question_stems) * 0.3

        priority_multipliers = {1: 1.0, 2: 1.2, 3: 1.5}
        score *= priority_multipliers.get(entry.priority, 1.0)

        return score

    def _detect_category_in_query(self, query_lower: str) -> Optional[KnowledgeCategory]:
        category_indicators = [
            "qué sabes sobre", "que sabes sobre", "qué sabes de", "que sabes de",
            "información sobre", "informacion sobre", "háblame de", "hablame de",
            "cuéntame sobre", "cuentame sobre", "dime sobre", "dime de"
        ]
        if not any(indicator in query_lower for indicator in category_indicators):
            return None

        category_keywords = {
            KnowledgeCategory.SISTEMAS: ["sistemas", "sistema", "aplicaciones", "software", "herramientas"],
            KnowledgeCategory.PROCESOS: ["procesos", "proceso", "procedimientos", "procedimiento"],
            KnowledgeCategory.POLITICAS: ["políticas", "politicas", "política", "politica", "normas", "reglas"],
            KnowledgeCategory.FAQS: ["faqs", "faq", "preguntas frecuentes", "preguntas comunes", "dudas"],
            KnowledgeCategory.CONTACTOS: ["contactos", "contacto", "teléfonos", "correos"],
            KnowledgeCategory.RECURSOS_HUMANOS: ["recursos humanos", "rrhh", "personal", "empleados"],
            KnowledgeCategory.BASE_DATOS: ["base datos", "base de datos", "bd", "tablas", "tabla"],
        }

        for category, keywords in category_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        return None

    def search(
        self,
        query: str,
        top_k: int = 3,
        min_score: float = 0.1,
        category_filter: Optional[KnowledgeCategory] = None
    ) -> List[KnowledgeEntry]:
        query_lower = self._clean_text(query.lower())

        category_from_query = self._detect_category_in_query(query_lower)
        if category_from_query and not category_filter:
            logger.info(f"Detectada pregunta sobre categoría: {category_from_query.value}")
            return self.get_entries_by_category(category_from_query, top_k=top_k)

        scored_entries = []
        for entry in self.knowledge_base:
            score = self._calculate_score(query_lower, entry)
            if category_filter and entry.category == category_filter:
                score += 0.3
            if score >= min_score:
                scored_entries.append((score, entry))

        scored_entries.sort(reverse=True, key=lambda x: x[0])
        results = [entry for _, entry in scored_entries[:top_k]]

        logger.debug(f"Búsqueda: '{query_lower[:50]}' → {len(results)} resultados")
        return results

    def get_context_for_llm(self, query: str, top_k: int = 2, include_metadata: bool = True) -> str:
        relevant = self.search(query, top_k=top_k)
        if not relevant:
            return ""

        context = "📚 CONOCIMIENTO INSTITUCIONAL RELEVANTE:\n\n"
        for idx, entry in enumerate(relevant, 1):
            if include_metadata:
                category_name = KnowledgeCategory.get_display_name(entry.category)
                context += f"**{idx}. [{category_name}] {entry.question}**\n"
            else:
                context += f"**{idx}. {entry.question}**\n"
            context += f"{entry.answer}\n\n"
            if entry.related_commands:
                context += f"_Comandos relacionados: {', '.join(entry.related_commands)}_\n\n"

        context += "---\n\n"
        return context

    def get_entries_by_category(self, category: KnowledgeCategory, top_k: int = 5) -> List[KnowledgeEntry]:
        entries = [e for e in self.knowledge_base if e.category == category]
        entries.sort(key=lambda e: e.priority, reverse=True)
        return entries[:top_k]

    def get_all_categories(self) -> List[KnowledgeCategory]:
        return KnowledgeCategory.get_all()

    def find_by_keywords(self, keywords: List[str]) -> List[KnowledgeEntry]:
        matching = []
        for entry in self.knowledge_base:
            if any(kw.lower() in [k.lower() for k in entry.keywords] for kw in keywords):
                matching.append(entry)
        return matching

    def get_high_priority_entries(self) -> List[KnowledgeEntry]:
        return [e for e in self.knowledge_base if e.priority >= 2]

    def get_stats(self) -> Dict[str, Any]:
        stats: Dict[str, Any] = {
            'total_entries': len(self.knowledge_base),
            'categories': {},
            'priority_distribution': {1: 0, 2: 0, 3: 0}
        }
        for entry in self.knowledge_base:
            stats['categories'][entry.category.value] = stats['categories'].get(entry.category.value, 0) + 1
            stats['priority_distribution'][entry.priority] += 1
        return stats

    def get_source(self) -> str:
        return self.source

    def reload_from_database(self) -> bool:
        try:
            if self.repository.health_check():
                entries = self.repository.get_all_entries()
                if entries:
                    self.knowledge_base = entries
                    self.source = "database"
                    logger.info(f"✅ Conocimiento recargado desde BD: {len(entries)} entradas")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error al recargar desde BD: {e}")
            return False

    def __repr__(self) -> str:
        role_info = f", role={self.id_rol}" if self.id_rol is not None else ""
        return f"KnowledgeService(entries={len(self.knowledge_base)}, source='{self.source}'{role_info})"


# Alias para compatibilidad durante la transición
KnowledgeManager = KnowledgeService
