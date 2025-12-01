# 📚 PLAN: Knowledge Base + RAG System

Plan para transformar el agente en un "empleado capacitado" con conocimiento institucional.

**Versión:** 1.0
**Fecha:** 2025-11-27
**Estado:** Planificación
**Objetivo:** Agente con memoria empresarial que responde inteligentemente sin siempre consultar BD

---

## 🎯 Visión General

**Problema Actual:**
- Agente solo puede responder si consulta la BD
- No tiene conocimiento de políticas, procesos, FAQs
- Cada pregunta requiere clasificación y posible query SQL

**Solución Propuesta:**
- Knowledge Base con información institucional
- RAG (Retrieval Augmented Generation) para búsqueda semántica
- Sistema híbrido que combina: Conocimiento + BD + LLM

**Valor Entregado:**
```
Usuario: "¿Cómo solicito vacaciones?"
Antes: ❌ No puede responder (no está en BD)
Ahora: ✅ "Para solicitar vacaciones debes llenar el formulario
          con 15 días de anticipación..."

Usuario: "¿Cuántos usuarios hay?"
Antes: ✅ Consulta BD → responde
Ahora: ✅ Consulta BD → responde (sin cambios)
```

---

## 📊 Estrategia de Implementación

### Enfoque Incremental (3 Fases):

```
Fase 1 → Knowledge Base Simple (1-2 días)
  ↓
Fase 2 → RAG System con Vectores (2-3 días)
  ↓
Fase 3 → Sistema Híbrido Completo (2-3 días)
```

**Cada fase es independiente y deployable**

---

## 🎯 FASE 1: Knowledge Base Simple (1-2 días)

**Objetivo:** Agregar conocimiento institucional al agente mediante archivos estructurados

### Valor Entregado:

```python
Usuario: "¿Cuál es el horario de atención?"
Sistema:
  1. Busca en knowledge_base.py
  2. Encuentra: "Horario: 8am-6pm"
  3. Responde directamente (sin consultar BD)
```

### Tareas:

**Día 1: Estructura de Knowledge Base**
- [ ] Crear `src/agent/knowledge/__init__.py`
- [ ] Crear `src/agent/knowledge/company_knowledge.py`
- [ ] Definir estructura de categorías (Procesos, Políticas, FAQs, Contactos)
- [ ] Agregar contenido inicial (10-15 entradas por categoría)
- [ ] Crear clase `KnowledgeManager` para acceder al conocimiento

**Día 2: Integración con Clasificador**
- [ ] Modificar `CLASSIFICATION_V3` para incluir conocimiento
- [ ] Actualizar `QueryClassifier` para usar KnowledgeManager
- [ ] Crear nuevo tipo de respuesta: "knowledge" (además de "database" y "general")
- [ ] Tests unitarios de KnowledgeManager
- [ ] Pruebas de integración

### Archivos a Crear:

```
src/agent/knowledge/
├── __init__.py
├── company_knowledge.py      # ~200 líneas - Datos estructurados
├── knowledge_manager.py      # ~150 líneas - Lógica de búsqueda simple
└── knowledge_categories.py   # ~80 líneas - Enum de categorías

tests/agent/knowledge/
└── test_knowledge_manager.py # ~120 líneas - Tests
```

### Ejemplo de Implementación:

```python
# src/agent/knowledge/company_knowledge.py
from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

class KnowledgeCategory(Enum):
    PROCESOS = "procesos"
    POLITICAS = "politicas"
    FAQS = "faqs"
    CONTACTOS = "contactos"
    SISTEMAS = "sistemas"

@dataclass
class KnowledgeEntry:
    """Entrada de conocimiento empresarial."""
    category: KnowledgeCategory
    question: str
    answer: str
    keywords: List[str]
    related_commands: List[str] = None

# Base de conocimiento
KNOWLEDGE_BASE = [
    KnowledgeEntry(
        category=KnowledgeCategory.PROCESOS,
        question="¿Cómo solicito vacaciones?",
        answer="Para solicitar vacaciones debes: 1) Ingresar al portal de empleados, "
               "2) Llenar el formulario de vacaciones con al menos 15 días de anticipación, "
               "3) Esperar aprobación de tu supervisor.",
        keywords=["vacaciones", "solicitar", "pedir", "días libres", "descanso"],
        related_commands=["/help"]
    ),
    KnowledgeEntry(
        category=KnowledgeCategory.POLITICAS,
        question="¿Cuál es el horario de trabajo?",
        answer="El horario laboral es de Lunes a Viernes de 8:00 AM a 6:00 PM, "
               "con 1 hora de almuerzo entre 12:00 PM y 2:00 PM.",
        keywords=["horario", "hora", "entrada", "salida", "jornada"],
        related_commands=[]
    ),
    KnowledgeEntry(
        category=KnowledgeCategory.FAQS,
        question="¿Qué hacer si olvido mi contraseña?",
        answer="Si olvidaste tu contraseña puedes: 1) Usar la opción 'Olvidé mi contraseña' "
               "en el portal, 2) Contactar al departamento de IT en la extensión 123, "
               "3) Enviar un ticket usando /crear_ticket.",
        keywords=["contraseña", "password", "olvidé", "resetear", "cambiar"],
        related_commands=["/crear_ticket"]
    ),
    KnowledgeEntry(
        category=KnowledgeCategory.CONTACTOS,
        question="¿Cómo contacto al departamento de IT?",
        answer="Puedes contactar a IT por: Extensión: 123, Email: it@empresa.com, "
               "O crear un ticket usando /crear_ticket",
        keywords=["it", "sistemas", "soporte", "técnico", "contacto"],
        related_commands=["/crear_ticket"]
    ),
    KnowledgeEntry(
        category=KnowledgeCategory.SISTEMAS,
        question="¿Qué comandos puedo usar en el bot?",
        answer="Comandos disponibles: /help (ayuda), /ia (consultas), "
               "/stats (estadísticas), /crear_ticket (soporte). "
               "Usa /help para ver la lista completa.",
        keywords=["comandos", "ayuda", "usar", "bot", "funciones"],
        related_commands=["/help"]
    ),
]
```

```python
# src/agent/knowledge/knowledge_manager.py
class KnowledgeManager:
    """Gestor de conocimiento empresarial."""

    def __init__(self):
        self.knowledge_base = KNOWLEDGE_BASE

    def search(self, query: str, top_k: int = 3) -> List[KnowledgeEntry]:
        """
        Buscar entradas relevantes por keywords.

        Args:
            query: Consulta del usuario
            top_k: Número de resultados

        Returns:
            Lista de entradas más relevantes
        """
        query_lower = query.lower()
        scored_entries = []

        for entry in self.knowledge_base:
            score = 0
            # Scoring simple por keywords
            for keyword in entry.keywords:
                if keyword in query_lower:
                    score += 1

            if score > 0:
                scored_entries.append((score, entry))

        # Ordenar por score y retornar top_k
        scored_entries.sort(reverse=True, key=lambda x: x[0])
        return [entry for _, entry in scored_entries[:top_k]]

    def get_context_for_llm(self, query: str) -> str:
        """Generar contexto para agregar al prompt del LLM."""
        relevant = self.search(query, top_k=3)

        if not relevant:
            return ""

        context = "CONOCIMIENTO INSTITUCIONAL RELEVANTE:\n\n"
        for entry in relevant:
            context += f"Q: {entry.question}\n"
            context += f"A: {entry.answer}\n\n"

        return context
```

### Criterios de Éxito:

- ✅ Knowledge base con 30+ entradas en 5 categorías
- ✅ KnowledgeManager encuentra entradas relevantes
- ✅ Clasificador diferencia entre "knowledge", "database" y "general"
- ✅ Respuestas instantáneas para preguntas de conocimiento
- ✅ Tests con 90%+ cobertura

---

## 🎯 FASE 2: RAG System con Vectores (2-3 días)

**Objetivo:** Búsqueda semántica usando embeddings (vectores)

### Valor Entregado:

```python
Usuario: "¿Cómo pido días libres?"  # Sinónimo de "vacaciones"
Antes (keyword search): ❌ No encuentra nada
Ahora (semantic search): ✅ Encuentra entrada de vacaciones
```

### Tareas:

**Día 1: Setup de Vector Store**
- [ ] Instalar ChromaDB (`pip install chromadb`)
- [ ] Crear `VectorKnowledgeManager`
- [ ] Convertir KNOWLEDGE_BASE a vectores
- [ ] Implementar búsqueda por similitud semántica

**Día 2: Integración con OpenAI Embeddings**
- [ ] Usar OpenAI embeddings (`text-embedding-ada-002`)
- [ ] Cachear vectores para no regenerar
- [ ] Benchmark: keyword vs semantic search

**Día 3: Optimización**
- [ ] Híbrido: semantic search + keyword fallback
- [ ] Configuración de thresholds de similitud
- [ ] Tests de performance
- [ ] Documentación

### Archivos a Crear:

```
src/agent/knowledge/
├── vector_knowledge_manager.py   # ~200 líneas
├── embeddings_cache.py           # ~100 líneas
└── vector_store.py               # ~150 líneas

tests/agent/knowledge/
└── test_vector_search.py         # ~150 líneas
```

### Ejemplo de Implementación:

```python
# src/agent/knowledge/vector_knowledge_manager.py
import chromadb
from chromadb.config import Settings

class VectorKnowledgeManager:
    """Gestor de conocimiento con búsqueda semántica."""

    def __init__(self):
        # Inicializar ChromaDB local
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=".chromadb"
        ))

        # Crear/obtener colección
        self.collection = self.client.get_or_create_collection(
            name="company_knowledge"
        )

        # Cargar knowledge base
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        """Cargar entradas de conocimiento como vectores."""
        # Obtener embeddings de OpenAI
        from openai import OpenAI
        client = OpenAI()

        for idx, entry in enumerate(KNOWLEDGE_BASE):
            # Crear documento combinando pregunta y respuesta
            document = f"{entry.question} {entry.answer}"

            # Obtener embedding
            response = client.embeddings.create(
                input=document,
                model="text-embedding-ada-002"
            )
            embedding = response.data[0].embedding

            # Agregar a ChromaDB
            self.collection.add(
                embeddings=[embedding],
                documents=[document],
                metadatas=[{
                    "category": entry.category.value,
                    "question": entry.question,
                    "answer": entry.answer
                }],
                ids=[f"entry_{idx}"]
            )

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Búsqueda semántica por similitud de vectores."""
        # Obtener embedding de la query
        from openai import OpenAI
        client = OpenAI()

        response = client.embeddings.create(
            input=query,
            model="text-embedding-ada-002"
        )
        query_embedding = response.data[0].embedding

        # Buscar en ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Formatear resultados
        formatted = []
        for metadata in results['metadatas'][0]:
            formatted.append({
                'question': metadata['question'],
                'answer': metadata['answer'],
                'category': metadata['category']
            })

        return formatted
```

### Criterios de Éxito:

- ✅ Vector store funcional con ChromaDB
- ✅ Búsqueda semántica con 85%+ accuracy
- ✅ Encuentra sinónimos y paráfrasis
- ✅ Tiempo de respuesta <500ms
- ✅ Cache de embeddings para eficiencia

---

## 🎯 FASE 3: Sistema Híbrido Completo (2-3 días)

**Objetivo:** Orquestar múltiples fuentes de conocimiento inteligentemente

### Valor Entregado:

```python
Usuario: "¿Cuántos días de vacaciones tengo disponibles?"

Sistema híbrido:
  1. Buscar en knowledge base → "Políticas de vacaciones: 15 días/año"
  2. Consultar BD → "Usuario123 ha usado 7 días"
  3. LLM combina ambas → "Tienes derecho a 15 días por año.
                          Has usado 7, te quedan 8 días disponibles."
```

### Tareas:

**Día 1: Knowledge Orchestrator**
- [ ] Crear `KnowledgeOrchestrator`
- [ ] Decidir qué fuentes consultar según la query
- [ ] Combinar resultados de múltiples fuentes
- [ ] Priorización de fuentes

**Día 2: Integración Completa**
- [ ] Modificar `LLMAgent` para usar orchestrator
- [ ] Prompt engineering con múltiples contextos
- [ ] Caching inteligente de resultados
- [ ] Metrics y analytics

**Día 3: Optimización y Pruebas**
- [ ] A/B testing de diferentes estrategias
- [ ] Optimización de costos (embeddings, tokens)
- [ ] Tests end-to-end
- [ ] Documentación completa

### Archivos a Crear:

```
src/agent/orchestrator/
├── __init__.py
├── knowledge_orchestrator.py     # ~300 líneas
├── source_selector.py            # ~150 líneas
└── response_combiner.py          # ~200 líneas

tests/agent/orchestrator/
└── test_knowledge_orchestrator.py # ~200 líneas
```

### Ejemplo de Implementación:

```python
# src/agent/orchestrator/knowledge_orchestrator.py
class KnowledgeOrchestrator:
    """Orquestador de múltiples fuentes de conocimiento."""

    def __init__(
        self,
        vector_knowledge: VectorKnowledgeManager,
        db_manager: DatabaseManager,
        llm_provider: LLMProvider
    ):
        self.vector_knowledge = vector_knowledge
        self.db_manager = db_manager
        self.llm_provider = llm_provider

    async def answer_query(self, user_query: str, user_id: int) -> str:
        """
        Responder query usando múltiples fuentes.

        Estrategia:
        1. Clasificar tipo de query
        2. Decidir qué fuentes consultar
        3. Obtener información de cada fuente
        4. Combinar y generar respuesta coherente
        """
        # 1. Clasificar query
        query_type = await self._classify_query(user_query)

        # 2. Obtener información según el tipo
        sources_data = {}

        if query_type in ["knowledge", "hybrid"]:
            # Buscar en knowledge base
            knowledge_results = self.vector_knowledge.search(user_query, top_k=2)
            sources_data['knowledge'] = knowledge_results

        if query_type in ["database", "hybrid"]:
            # Consultar base de datos
            db_results = await self._query_database(user_query)
            sources_data['database'] = db_results

        # 3. Combinar y generar respuesta
        response = await self._combine_sources(
            user_query=user_query,
            sources_data=sources_data,
            query_type=query_type
        )

        return response

    async def _classify_query(self, query: str) -> str:
        """
        Clasificar query en: knowledge, database, hybrid, general.

        hybrid = necesita tanto knowledge como database
        """
        prompt = f"""
        Clasifica esta consulta:

        "{query}"

        Tipos:
        - "knowledge": Pregunta sobre políticas/procesos/información institucional
        - "database": Requiere datos específicos de BD (conteos, registros)
        - "hybrid": Requiere AMBOS (conocimiento + datos)
        - "general": Conversación general

        Responde con UNA palabra.
        """

        classification = await self.llm_provider.generate(prompt, max_tokens=10)
        return classification.strip().lower()

    async def _combine_sources(
        self,
        user_query: str,
        sources_data: Dict,
        query_type: str
    ) -> str:
        """Combinar información de múltiples fuentes en respuesta coherente."""

        # Construir contexto combinado
        context_parts = []

        if 'knowledge' in sources_data:
            knowledge_context = "\n".join([
                f"- {entry['answer']}"
                for entry in sources_data['knowledge']
            ])
            context_parts.append(f"CONOCIMIENTO INSTITUCIONAL:\n{knowledge_context}")

        if 'database' in sources_data:
            db_context = sources_data['database']
            context_parts.append(f"DATOS DE LA BASE DE DATOS:\n{db_context}")

        full_context = "\n\n".join(context_parts)

        # Generar respuesta combinada
        prompt = f"""
        Eres un asistente de empresa. Responde la consulta del usuario usando
        la información proporcionada.

        {full_context}

        Consulta del usuario: "{user_query}"

        Instrucciones:
        - Combina la información de todas las fuentes de manera natural
        - Si hay datos de BD, úsalos como información actualizada
        - Si hay conocimiento institucional, úsalo como contexto
        - Sé conciso pero completo

        Respuesta:
        """

        response = await self.llm_provider.generate(prompt, max_tokens=500)
        return response
```

### Criterios de Éxito:

- ✅ Orchestrator decide inteligentemente qué fuentes usar
- ✅ Combina conocimiento + BD coherentemente
- ✅ Respuestas 30% más completas que solo BD
- ✅ Costo optimizado (solo consulta lo necesario)
- ✅ Analytics de uso de cada fuente

---

## 📈 Métricas de Éxito

### Por Fase:

**FASE 1:**
- Knowledge base con 30+ entradas
- 50% de queries simples NO requieren BD
- Tiempo de respuesta <200ms para knowledge queries

**FASE 2:**
- 85%+ accuracy en búsqueda semántica
- Encuentra sinónimos/paráfrasis correctamente
- <500ms tiempo de búsqueda vectorial

**FASE 3:**
- 80% de queries clasificadas correctamente
- Combina sources en 90%+ de casos híbridos
- Reducción de 40% en queries a BD innecesarias

---

## 🛠️ Stack Tecnológico

### Librerías Necesarias:

```bash
# FASE 1 - No requiere librerías adicionales
# (usa estructura de datos Python nativa)

# FASE 2 - Vector Store
pip install chromadb==0.4.22
pip install openai  # Para embeddings

# FASE 3 - Opcional
pip install langchain  # Helpers para RAG
pip install tiktoken   # Token counting
```

### Costos Estimados:

**Embeddings (OpenAI):**
- `text-embedding-ada-002`: $0.0001 per 1K tokens
- 100 entradas de knowledge (~50K tokens): $0.005
- Queries diarias (1000): ~$0.10/día

**Total estimado:** ~$3-5/mes (muy bajo)

---

## 📚 Recursos de Aprendizaje

### Documentación:
- [ChromaDB Docs](https://docs.trychroma.com/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [LangChain RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)

### Ejemplos:
- [RAG from Scratch](https://github.com/langchain-ai/rag-from-scratch)
- [Building RAG Apps](https://www.pinecone.io/learn/retrieval-augmented-generation/)

---

## 🔄 Mantenimiento

### Actualización de Knowledge Base:

```python
# Agregar nueva entrada
new_entry = KnowledgeEntry(
    category=KnowledgeCategory.POLITICAS,
    question="Nueva política de home office",
    answer="...",
    keywords=[...]
)

# Re-generar vectores (FASE 2)
vector_manager.add_entry(new_entry)
```

### Monitoring:

- Dashboard de queries por tipo (knowledge/database/hybrid)
- Analytics de entradas de knowledge más usadas
- A/B testing de diferentes estrategias de búsqueda

---

## 🚀 Roadmap Extendido

### Post-FASE 3 (Futuro):

1. **Memory Conversacional**
   - Recordar contexto de conversaciones previas
   - Personalización por usuario

2. **Auto-learning**
   - Detectar preguntas sin respuesta
   - Sugerir nuevas entradas de knowledge

3. **Multi-modal Knowledge**
   - PDFs, imágenes, videos
   - Knowledge externo (web scraping)

4. **Knowledge Graphs**
   - Relaciones entre entidades
   - Inferencia avanzada

---

## ✅ Checklist de Inicio

Antes de empezar FASE 1:

- [ ] Recopilar documentación existente (manuales, políticas, FAQs)
- [ ] Identificar 5 categorías principales de conocimiento
- [ ] Crear lista de 30-50 preguntas frecuentes
- [ ] Definir estructura de respuestas (formato, tono)
- [ ] Setup de branch GitFlow

---

## 📝 Notas Finales

**Filosofía de Diseño:**
- Empezar simple, iterar basado en feedback
- Cada fase es deployable independientemente
- Priorizar calidad sobre cantidad de entradas
- Medir, analizar, optimizar continuamente

**Riesgos y Mitigaciones:**
- **Riesgo:** Knowledge base desactualizado → **Mitigación:** Proceso de revisión mensual
- **Riesgo:** Costos de embeddings → **Mitigación:** Caching agresivo
- **Riesgo:** Hallucinations del LLM → **Mitigación:** Validación de fuentes

---

**¿Listo para empezar?** 🚀

Siguiente paso: FASE 1 - Crear estructura de Knowledge Base
