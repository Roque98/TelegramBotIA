# PLAN: Reemplazar stemmer manual por NLP real

> **Objetivo**: Mejorar la calidad de búsqueda en la knowledge base usando NLP real en lugar del stemmer manual
> **Rama**: `feature/cal-14-stemmer-nlp`
> **Prioridad**: 🟡 Media
> **Progreso**: 0% (0/6)

---

## Contexto

`src/knowledge/knowledge_service.py:67-92` implementa un stemmer manual con 29 sufijos hardcodeados:

```python
@staticmethod
def _stem_es(word: str) -> str:
    for suffix in ("aciones", "iciones", "amiento", ...):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word
```

Problemas:
- No es un stemmer lingüístico, es truncamiento por sufijos
- "comunicación" → "comunica" (pierde la raíz correcta "comunic")
- No maneja irregulares: "yendo", "fui", "hizo"
- 29 sufijos no cubren la morfología española completa

La alternativa más sencilla es `snowballstemmer` (incluido en `nltk`) o el stemmer de `spacy` con el modelo `es_core_news_sm`.

---

## Archivos involucrados

- `src/knowledge/knowledge_service.py` — reemplazar `_stem_es()`
- `requirements.txt` — agregar `nltk` o verificar si ya está
- `tests/test_knowledge_service.py` — tests de búsqueda con palabras irregulares

---

## Opciones

| Opción | Librería | Tamaño | Calidad |
|--------|----------|--------|---------|
| A | `nltk` (SnowballStemmer) | ~10MB | Buena |
| B | `spacy` (es_core_news_sm) | ~100MB | Excelente |
| C | Mantener actual + mejorar lista | 0MB | Regular |

**Recomendación**: Opción A (nltk SnowballStemmer) — buen balance entre calidad y peso.

---

## Tareas

- [ ] **14.1** Verificar si `nltk` ya está en `requirements.txt`; si no, agregarlo
- [ ] **14.2** Reemplazar método `_stem_es()` por `SnowballStemmer("spanish").stem(word)`
- [ ] **14.3** Agregar descarga automática del corpus necesario de nltk al primer uso (o en startup)
- [ ] **14.4** Eliminar la lista de 29 sufijos hardcodeados
- [ ] **14.5** Comparar resultados de búsqueda antes y después con un conjunto de 20 queries de prueba
- [ ] **14.6** Actualizar tests de `knowledge_service` con casos de palabras irregulares

---

## Criterios de aceptación

- La búsqueda de "vacaciones" encuentra entradas con "vacación", "vacacionar"
- La búsqueda de "reembolso" encuentra "reembolsar", "reembolsado"
- El código no tiene listas de sufijos hardcodeados
- Tiempo de búsqueda no aumenta más de 50ms respecto al actual
