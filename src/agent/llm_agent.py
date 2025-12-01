"""
Agente LLM para procesar consultas y generar SQL.

Refactorizado para actuar como orquestador de componentes especializados.
"""
import asyncio
import logging
from typing import Optional
from src.config.settings import settings
from src.database.connection import DatabaseManager
from .providers.base_provider import LLMProvider
from .providers.openai_provider import OpenAIProvider
from .providers.anthropic_provider import AnthropicProvider
from .classifiers.query_classifier import QueryClassifier, QueryType
from .sql.sql_generator import SQLGenerator
from .sql.sql_validator import SQLValidator
from .formatters.response_formatter import ResponseFormatter
from .prompts import get_default_manager

logger = logging.getLogger(__name__)


class LLMAgent:
    """Agente que procesa consultas en lenguaje natural y las convierte a SQL."""

    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        llm_provider: Optional[LLMProvider] = None
    ):
        """
        Inicializar el agente.

        Args:
            db_manager: Gestor de base de datos (opcional, se crea si no se proporciona)
            llm_provider: Proveedor de LLM (opcional, se crea si no se proporciona)
        """
        # Inicializar base de datos
        self.db_manager = db_manager or DatabaseManager()

        # Inicializar proveedor LLM
        self.llm_provider = llm_provider or self._initialize_llm_provider()

        # Inicializar gestor de prompts
        self.prompt_manager = get_default_manager()

        # Inicializar componentes especializados
        self.query_classifier = QueryClassifier(self.llm_provider)
        self.sql_generator = SQLGenerator(self.llm_provider)
        self.sql_validator = SQLValidator()
        self.response_formatter = ResponseFormatter(
            max_results_display=10,
            llm_provider=self.llm_provider,
            use_natural_language=True
        )

        logger.info(
            f"Agente LLM inicializado con proveedor: {self.llm_provider.get_provider_name()}, "
            f"modelo: {self.llm_provider.get_model_name()}"
        )

    def _initialize_llm_provider(self) -> LLMProvider:
        """
        Inicializar el proveedor de LLM según la configuración.

        Returns:
            Instancia del proveedor de LLM

        Raises:
            ValueError: Si no se encuentra ninguna API key configurada
        """
        if settings.openai_api_key:
            # Mostrar token parcialmente ocultado para seguridad
            masked_token = self._mask_token(settings.openai_api_key)
            logger.info(f"Usando proveedor OpenAI - Token: {masked_token}")
            return OpenAIProvider(
                api_key=settings.openai_api_key,
                model=settings.openai_model
            )
        elif settings.anthropic_api_key:
            # Mostrar token parcialmente ocultado para seguridad
            masked_token = self._mask_token(settings.anthropic_api_key)
            logger.info(f"Usando proveedor Anthropic - Token: {masked_token}")
            return AnthropicProvider(
                api_key=settings.anthropic_api_key
            )
        else:
            raise ValueError("No se encontró ninguna API key de LLM configurada")

    @staticmethod
    def _mask_token(token: str) -> str:
        """
        Ocultar parcialmente el token para seguridad.

        Args:
            token: Token completo

        Returns:
            Token con caracteres del medio ocultados
        """
        if len(token) <= 8:
            return "***"
        return f"{token[:4]}...{token[-4:]}"

    async def process_query(self, user_query: str) -> str:
        """
        Procesar una consulta del usuario.

        Este método orquesta todo el flujo:
        1. Clasificar la consulta
        2. Si es general, responder con el LLM
        3. Si es conocimiento institucional, responder con knowledge base
        4. Si requiere BD, generar SQL, validar, ejecutar y formatear

        Args:
            user_query: Consulta en lenguaje natural del usuario

        Returns:
            Respuesta formateada para el usuario
        """
        try:
            # 1. Clasificar la consulta
            query_type = await self.query_classifier.classify(user_query)

            # 2. Si es una consulta general, responder directamente
            if query_type == QueryType.GENERAL:
                return await self._process_general_query(user_query)

            # 3. Si es conocimiento institucional, responder con knowledge base
            if query_type == QueryType.KNOWLEDGE:
                return await self._process_knowledge_query(user_query)

            # 4. Si requiere base de datos, seguir el flujo completo
            return await self._process_database_query(user_query)

        except Exception as e:
            logger.error(f"Error en process_query: {e}", exc_info=True)
            return self.response_formatter.format_error(str(e), user_friendly=True)

    async def _process_general_query(self, user_query: str) -> str:
        """
        Procesar una consulta general que no requiere base de datos.

        Responde con la personalidad de Amber, recordando al usuario
        sobre sus capacidades de información empresarial y consultas de BD.
        El mensaje se genera dinámicamente desde la base de datos.

        Args:
            user_query: Consulta del usuario

        Returns:
            Respuesta de Amber sobre sus capacidades
        """
        logger.info("Consulta general detectada - Amber responde sobre sus capacidades")

        # Detectar saludos para personalizar la respuesta
        saludos = ["hola", "hello", "hi", "buenos días", "buenas tardes", "buenas noches", "hey"]
        es_saludo = any(saludo in user_query.lower() for saludo in saludos)

        if es_saludo:
            # Generar mensaje dinámico desde BD
            greeting_message = self._generate_greeting_from_db()
            return greeting_message
        else:
            # Generar respuesta general con categorías desde BD
            general_response = self._generate_general_response_from_db()
            return general_response

    def _generate_greeting_from_db(self) -> str:
        """
        Generar mensaje de saludo dinámicamente desde la BD.

        Returns:
            Mensaje de saludo con categorías y ejemplos desde BD
        """
        try:
            from src.agent.knowledge import KnowledgeRepository

            # Usar el mismo db_manager que el agente
            repository = KnowledgeRepository(self.db_manager)

            # Verificar health check primero
            if not repository.health_check():
                logger.warning("BD no disponible para generar saludo, usando fallback")
                raise ConnectionError("BD no responde al health check")

            # Obtener categorías con conteo
            categories = repository.get_categories_info()
            logger.debug(f"Categorías obtenidas: {len(categories)}")

            # Construir texto de categorías
            categories_text = ""
            for cat in categories:
                if cat.get('entry_count', 0) > 0:
                    categories_text += f"• {cat['icon']} {cat['display_name']}\n"

            # Obtener ejemplos de preguntas
            examples = repository.get_example_questions(limit=3)
            logger.debug(f"Ejemplos obtenidos: {len(examples)}")
            examples_text = "\n".join([f"• `{q}`" for q in examples])

            logger.info("✅ Saludo generado dinámicamente desde BD")
            return (
                "👋 ¡Hola! Soy **Amber**, analista del Centro de Operaciones ✨\n\n"
                "Estoy aquí para ayudarte con información sobre:\n\n"
                f"{categories_text}\n"
                "💡 **Ejemplos de preguntas:**\n"
                f"{examples_text}\n\n"
                "¿En qué puedo ayudarte hoy? 🎯"
            )

        except Exception as e:
            logger.error(f"❌ Error generando saludo desde BD: {e}", exc_info=True)
            # Fallback básico si falla la BD
            return (
                "👋 ¡Hola! Soy **Amber**, analista del Centro de Operaciones ✨\n\n"
                "Estoy aquí para ayudarte con:\n\n"
                "📋 Información Institucional\n"
                "📊 Consultas de Datos\n"
                "💡 Preguntas y soporte\n\n"
                "¿En qué puedo ayudarte hoy? 🎯"
            )

    def _generate_general_response_from_db(self) -> str:
        """
        Generar respuesta general dinámicamente desde la BD.

        Returns:
            Mensaje con especialidades basadas en categorías de BD
        """
        try:
            from src.agent.knowledge import KnowledgeRepository

            # Usar el mismo db_manager que el agente
            repository = KnowledgeRepository(self.db_manager)

            # Verificar health check primero
            if not repository.health_check():
                logger.warning("BD no disponible para generar respuesta general, usando fallback")
                raise ConnectionError("BD no responde al health check")

            # Obtener categorías con conteo
            categories = repository.get_categories_info()
            logger.debug(f"Categorías obtenidas para respuesta general: {len(categories)}")

            # Construir texto de especialidades (solo categorías con contenido)
            specialties_text = ""
            for cat in categories:
                if cat.get('entry_count', 0) > 0:
                    specialties_text += f"{cat['icon']} {cat['display_name']}\n"

            logger.info("✅ Respuesta general generada dinámicamente desde BD")
            return (
                "💭 Hmm, esa es una pregunta interesante, pero estoy especializada en información empresarial y consultas de datos.\n\n"
                "🎯 **Mis especialidades:**\n\n"
                f"{specialties_text}\n"
                "¿Hay algo relacionado con estos temas en lo que pueda ayudarte? ✨\n\n"
                "_Amber, siempre dispuesta a ayudar_ 💪"
            )

        except Exception as e:
            logger.error(f"❌ Error generando respuesta general desde BD: {e}", exc_info=True)
            # Fallback básico si falla la BD
            return (
                "💭 Hmm, esa es una pregunta interesante, pero estoy especializada en información empresarial y consultas de datos.\n\n"
                "🎯 **Mis especialidades:**\n\n"
                "📋 Políticas y procesos\n"
                "📊 Consultas de datos\n"
                "💡 Información de sistemas\n\n"
                "¿Hay algo relacionado con estos temas en lo que pueda ayudarte? ✨\n\n"
                "_Amber, siempre dispuesta a ayudar_ 💪"
            )

    async def _process_knowledge_query(self, user_query: str) -> str:
        """
        Procesar una consulta de conocimiento institucional.

        Args:
            user_query: Consulta del usuario

        Returns:
            Respuesta con conocimiento institucional
        """
        logger.info("Procesando consulta de conocimiento institucional")

        # Obtener contexto de conocimiento
        knowledge_context = self.query_classifier.get_knowledge_context(user_query, top_k=3)

        if not knowledge_context:
            # Si por alguna razón no hay contexto, responder con LLM general
            return await self._process_general_query(user_query)

        # Usar el sistema de prompts con contexto de conocimiento
        prompt = self.prompt_manager.get_prompt(
            'general_response',
            version=2,
            user_query=user_query,
            context=knowledge_context
        )

        try:
            response = await self.llm_provider.generate(prompt, max_tokens=1024)
            return self.response_formatter.format_general_response(response)

        except Exception as e:
            logger.error(f"Error procesando consulta de conocimiento: {e}")
            return (
                "❌ Oh, tuve un problema procesando esa pregunta.\n\n"
                "¿Podrías intentarlo de nuevo o reformularla?\n\n"
                "_Amber está aquí para ayudarte_ ✨"
            )

    async def _process_database_query(self, user_query: str) -> str:
        """
        Procesar una consulta que requiere acceso a base de datos.

        Args:
            user_query: Consulta del usuario

        Returns:
            Respuesta formateada con resultados
        """
        logger.info("Procesando consulta de base de datos")

        # 1. Obtener esquema de la base de datos
        schema = await asyncio.to_thread(self.db_manager.get_schema)

        # 2. Generar SQL
        sql_query = await self.sql_generator.generate_sql(user_query, schema)

        if not sql_query:
            return (
                "🤔 Hmm, tuve dificultades generando la consulta para eso.\n\n"
                "¿Podrías reformular tu pregunta de otra manera?\n\n"
                "_Amber intentando ayudarte_ 💪"
            )

        # 3. Validar SQL
        is_valid, error_message = self.sql_validator.validate(sql_query)

        if not is_valid:
            logger.warning(f"SQL no válido: {error_message}")
            return (
                "🔒 Esa consulta no pasó las validaciones de seguridad.\n\n"
                "Por tu seguridad, solo puedo ejecutar consultas de lectura.\n\n"
                "¿Necesitas algo más? _Amber aquí para ayudarte_ ✨"
            )

        # 4. Ejecutar la consulta
        try:
            results = await asyncio.to_thread(self.db_manager.execute_query, sql_query)
        except Exception as e:
            logger.error(f"Error ejecutando consulta: {e}")
            return (
                "❌ Ups, tuve un problema ejecutando la consulta en la base de datos.\n\n"
                "Esto puede ser temporal. ¿Intentamos de nuevo?\n\n"
                "_Amber aquí para ayudarte_ 💪"
            )

        # 5. Formatear respuesta
        return await self.response_formatter.format_query_results(
            user_query=user_query,
            sql_query=sql_query,
            results=results,
            include_sql=False  # Cambiar a True para debugging
        )

