# 🎯 Sistema de Prompts Modular

Sistema de gestión de prompts con versionado, A/B testing y plantillas reutilizables.

## 🚀 Inicio Rápido

### Uso Básico

```python
from src.agent.prompts import get_default_manager

# Obtener instancia del manager
manager = get_default_manager()

# Generar un prompt
prompt = manager.get_prompt(
    'classification',
    user_query="¿Cuántos usuarios hay en la base de datos?"
)
```

### Usar Versión Específica

```python
# Usar versión 2 del prompt de generación SQL
prompt = manager.get_prompt(
    'sql_generation',
    version=2,
    user_query="Lista todos los productos",
    database_schema=schema
)
```

### Configurar A/B Testing

```python
# 50% versión 1, 50% versión 2
manager.enable_ab_test(
    'classification',
    variants={1: 0.5, 2: 0.5},
    strategy='weighted'
)

# Ahora los prompts se distribuyen automáticamente
prompt = manager.get_prompt('classification', user_query="test")
```

### Establecer Versión por Defecto

```python
# Usar siempre versión 2
manager.set_default_version('sql_generation', version=2)
```

## 📁 Estructura del Módulo

```
src/agent/prompts/
├── __init__.py              # Exports públicos
├── prompt_templates.py      # Plantillas Jinja2 versionadas
├── prompt_manager.py        # Gestor de prompts y A/B testing
└── README.md               # Este archivo
```

## 📋 Prompts Disponibles

### 1. Classification (Clasificación de consultas)
- **V1**: Clasificador básico database/general
- **V2**: Clasificador mejorado con contexto adicional

```python
prompt = manager.get_prompt(
    'classification',
    user_query="¿Cuántos productos hay?"
)
```

### 2. SQL Generation (Generación de SQL)
- **V1**: Generador básico con reglas de seguridad
- **V2**: Generador mejorado para SQL Server
- **V3**: Generador optimizado con soporte para consultas complejas

```python
prompt = manager.get_prompt(
    'sql_generation',
    user_query="Lista los 10 productos más vendidos",
    database_schema=schema,
    max_results=10  # opcional
)
```

### 3. General Response (Respuestas generales)
- **V1**: Asistente amigable básico
- **V2**: Asistente profesional con contexto

```python
prompt = manager.get_prompt(
    'general_response',
    user_query="Hola, ¿cómo estás?",
    context="Usuario es administrador"  # opcional
)
```

## 🔧 Funciones Útiles

### Listar Prompts Disponibles

```python
prompts = manager.list_prompts()
print(prompts)
# {
#     'CLASSIFICATION': [1, 2],
#     'SQL_GENERATION': [1, 2, 3],
#     'GENERAL_RESPONSE': [1, 2]
# }
```

### Ver Métricas de Uso

```python
# Métricas de un prompt específico
metrics = manager.get_metrics('classification')

# Todas las métricas
all_metrics = manager.get_metrics()
```

### Ver Estadísticas de A/B Testing

```python
stats = manager.get_ab_test_stats('classification')
print(stats)
# {
#     'enabled': True,
#     'strategy': 'weighted',
#     'variants': {1: 0.5, 2: 0.5},
#     'usage': {1: 1247, 2: 1253}
# }
```

### Deshabilitar A/B Testing

```python
manager.disable_ab_test('classification')
```

## ➕ Agregar Nuevo Prompt

### 1. Agregar Template en `prompt_templates.py`

```python
class PromptTemplates:
    # ... templates existentes ...

    MI_NUEVO_PROMPT_V1 = Template("""
    Instrucciones claras aquí...

    Variable: {{ mi_variable }}

    Respuesta:
    """)
```

### 2. Usar en tu Código

```python
from src.agent.prompts import get_default_manager

manager = get_default_manager()
prompt = manager.get_prompt(
    'mi_nuevo_prompt',
    mi_variable="valor"
)
```

## 🧪 Integración con Componentes

### En QueryClassifier

```python
class QueryClassifier:
    def __init__(self, llm_provider: LLMProvider, prompt_version: Optional[int] = None):
        self.llm_provider = llm_provider
        self.prompt_manager = get_default_manager()
        self.prompt_version = prompt_version

    async def classify(self, user_query: str) -> QueryType:
        prompt = self.prompt_manager.get_prompt(
            'classification',
            version=self.prompt_version,
            user_query=user_query
        )
        # ... rest of logic
```

### En SQLGenerator

```python
class SQLGenerator:
    def __init__(self, llm_provider: LLMProvider, prompt_version: Optional[int] = None):
        self.llm_provider = llm_provider
        self.prompt_manager = get_default_manager()
        self.prompt_version = prompt_version

    async def generate_sql(self, user_query: str, database_schema: str) -> Optional[str]:
        prompt = self.prompt_manager.get_prompt(
            'sql_generation',
            version=self.prompt_version,
            user_query=user_query,
            database_schema=database_schema
        )
        # ... rest of logic
```

## 📊 Estrategias de A/B Testing

### Random / Weighted (por defecto)
Selección aleatoria ponderada según los pesos configurados.

```python
manager.enable_ab_test(
    'classification',
    variants={1: 0.3, 2: 0.7},  # 30% v1, 70% v2
    strategy='weighted'
)
```

### Round Robin
Rotación circular entre versiones (útil para testing uniforme).

```python
manager.enable_ab_test(
    'sql_generation',
    variants={1: 0.5, 2: 0.5},
    strategy='round_robin'
)
```

## ⚠️ Mejores Prácticas

1. **Versionado**: Siempre versionar prompts (`_V1`, `_V2`, etc.)
2. **No modificar versiones existentes**: Crear nueva versión para cambios
3. **A/B testing gradual**: Empezar con distribución 90/10 antes de 50/50
4. **Documentar cambios**: Usar metadata para documentar por qué se creó una versión
5. **Monitorear métricas**: Revisar regularmente las estadísticas de uso
6. **Defaults sensatos**: Usar valores por defecto en variables opcionales

## 📖 Documentación Completa

Ver [BEST_PRACTICES.md](../../../docs/prompts/BEST_PRACTICES.md) para guía completa sobre:
- Principios de diseño de prompts
- Optimización de tokens
- Ejemplos avanzados
- Troubleshooting

## 🔗 Referencias

- **Plantillas**: `src/agent/prompts/prompt_templates.py`
- **Manager**: `src/agent/prompts/prompt_manager.py`
- **Tests**: `tests/test_prompts.py` (TODO)
- **Docs**: `docs/prompts/BEST_PRACTICES.md`

---

**Versión**: 1.0
**Última actualización**: 2025-10-29
