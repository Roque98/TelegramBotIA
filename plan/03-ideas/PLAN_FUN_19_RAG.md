# PLAN: RAG con búsqueda vectorial para Knowledge Base

> **Objetivo**: Reemplazar la búsqueda por keywords con búsqueda semántica usando embeddings vectoriales
> **Rama**: `feature/fun-19-rag-vectorial`
> **Prioridad**: 🟢 Funcional
> **Progreso**: 0% (0/9)

---

## Contexto

La búsqueda actual en `knowledge_service.py` usa keywords + stemming manual. Esto falla en casos como:

- Usuario pregunta "¿cómo pido días libres?" → no encuentra "vacaciones" (palabras distintas, mismo significado)
- Usuario pregunta "procedimiento para pago de gastos" → no encuentra "reembolso de viáticos"

RAG (Retrieval-Augmented Generation) con embeddings resuelve esto: convierte preguntas y respuestas en vectores numéricos que capturan el **significado semántico**, no solo las palabras exactas.

---

## Arquitectura propuesta

```
Usuario pregunta
       ↓
Generar embedding de la pregunta (OpenAI text-embedding-3-small)
       ↓
Buscar los K vectores más similares en la BD vectorial
       ↓
Pasar los K resultados como contexto al LLM
       ↓
LLM genera respuesta con contexto relevante
```

---

## Opciones de almacenamiento vectorial

| Opción | Ventaja | Desventaja |
|--------|---------|------------|
| pgvector (PostgreSQL) | Ya tienes BD | Requiere migrar de SQL Server |
| ChromaDB | Simple, local | Otro proceso a mantener |
| SQL Server + cálculo manual | Sin nueva infra | Lento para miles de entradas |
| OpenAI embeddings en BD actual | Sin nueva infra | Calcular similitud en Python |

**Recomendación**: Guardar embeddings como columna en `knowledge_entries` de SQL Server y calcular similitud coseno en Python. Sin nueva infraestructura.

---

## Archivos involucrados

- `src/knowledge/knowledge_entity.py` — agregar campo `embedding`
- `src/knowledge/knowledge_repository.py` — guardar/leer embeddings
- `src/knowledge/knowledge_service.py` — nuevo método `search_semantic()`
- `src/agents/providers/openai_provider.py` — agregar método `get_embedding()`
- BD: columna `embedding` en `knowledge_entries`

---

## Tareas

- [ ] **19.1** Agregar método `get_embedding(text)` en `openai_provider.py` usando `text-embedding-3-small`
- [ ] **19.2** Agregar columna `embedding` (tipo `nvarchar(max)` para JSON) en `knowledge_entries`
- [ ] **19.3** Crear script de migración para generar embeddings de todas las entradas existentes
- [ ] **19.4** Actualizar `knowledge_repository.py` para guardar y leer embeddings
- [ ] **19.5** Implementar `cosine_similarity(v1, v2)` en `knowledge_service.py`
- [ ] **19.6** Implementar `search_semantic(query, top_k)` que use embeddings
- [ ] **19.7** Hacer que `search()` use semántica como primera opción y keywords como fallback
- [ ] **19.8** Actualizar embeddings automáticamente cuando se modifica una entrada en BD
- [ ] **19.9** Comparar calidad de resultados: buscar 20 preguntas con ambos métodos y documentar

---

## Criterios de aceptación

- "días libres" encuentra entradas sobre "vacaciones"
- "pago de gastos" encuentra entradas sobre "reembolso"
- El fallback a keywords funciona si no hay embeddings disponibles
- El costo de embeddings está dentro de lo razonable (estimado: <$1/mes para 500 entradas)
