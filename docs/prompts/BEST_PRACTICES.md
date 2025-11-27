# 📝 Mejores Prácticas para Prompts

> **Última actualización:** 2025-10-29
> **Sistema de Prompts:** v1.0

---

## 📋 Tabla de Contenidos

1. [Principios Fundamentales](#principios-fundamentales)
2. [Estructura de Prompts](#estructura-de-prompts)
3. [Versionado de Prompts](#versionado-de-prompts)
4. [A/B Testing](#ab-testing)
5. [Variables en Templates](#variables-en-templates)
6. [Optimización de Prompts](#optimización-de-prompts)
7. [Troubleshooting](#troubleshooting)
8. [Ejemplos Prácticos](#ejemplos-prácticos)

---

## 🎯 Principios Fundamentales

### 1. Claridad sobre Brevedad
- **✓ HACER:** Ser explícito en las instrucciones
- **✗ EVITAR:** Instrucciones ambiguas o vagas

```python
# ❌ MAL
"Genera SQL para la pregunta"

# ✅ BIEN
"""Dado el esquema de base de datos, genera una consulta SQL segura.
SOLO usa SELECT, no modifiques datos. Responde únicamente con el SQL."""
```

### 2. Separación de Concerns
- Cada prompt debe tener **un solo propósito** claro
- No mezclar clasificación con generación
- Mantener prompts modulares y reutilizables

### 3. Versionado Desde el Inicio
- **SIEMPRE** empezar con `_V1`
- Nunca modificar una versión existente en producción
- Crear nueva versión para cambios significativos

### 4. Instrucciones Claras y Específicas
- Usar listas numeradas o con viñetas
- Especificar formato de salida esperado
- Incluir ejemplos cuando sea posible

---

## 🏗️ Estructura de Prompts

### Anatomía de un Prompt Efectivo

```
1. Contexto/Rol del sistema
2. Datos de entrada (esquema, pregunta, etc.)
3. Instrucciones específicas
4. Restricciones y reglas
5. Formato de salida esperado
```

### Ejemplo Completo

```python
PROMPT_TEMPLATE = Template("""
[1. ROL]
Eres un experto en SQL Server especializado en generar consultas seguras.

[2. DATOS]
Esquema de base de datos:
{{ database_schema }}

Pregunta del usuario:
"{{ user_query }}"

[3. INSTRUCCIONES]
Genera una consulta SQL que:
1. Responda exactamente a la pregunta del usuario
2. Use solo tablas y columnas del esquema proporcionado
3. Sea eficiente y optimizada

[4. RESTRICCIONES]
- SOLO consultas SELECT (prohibido: INSERT, UPDATE, DELETE, DROP)
- Usar TOP {{ max_results|default(100) }} para limitar resultados
- No ejecutar procedimientos almacenados

[5. FORMATO]
Responde ÚNICAMENTE con el código SQL, sin markdown ni explicaciones.

SQL:
""")
```

---

## 🔄 Versionado de Prompts

### Cuándo Crear una Nueva Versión

| Situación | Acción | Ejemplo |
|-----------|--------|---------|
| Fix de typo menor | Actualizar en v1 | "databse" → "database" |
| Cambio de instrucción | Nueva versión (v2) | Agregar nueva regla de seguridad |
| Reformulación completa | Nueva versión (v3) | Cambiar estructura del prompt |
| Experimentación | Nueva versión para A/B testing | Probar tono más formal vs casual |

### Nomenclatura de Versiones

```python
# Correcto ✅
CLASSIFICATION_V1 = Template(...)
CLASSIFICATION_V2 = Template(...)
SQL_GENERATION_V1 = Template(...)
SQL_GENERATION_V2 = Template(...)

# Incorrecto ❌
classification_prompt = Template(...)  # Sin versión
CLASSIFICATION_FINAL = Template(...)  # Nombre ambiguo
```

### Metadata Recomendada

```python
METADATA_V2 = {
    'created_at': '2025-10-29',
    'author': 'equipo-ia',
    'changes': 'Mejorar instrucciones de seguridad SQL',
    'tested': True,
    'performance': {
        'accuracy': 0.95,
        'avg_tokens': 450
    }
}
```

---

## 🧪 A/B Testing

### Configuración de A/B Testing

```python
from src.agent.prompts import get_default_manager

manager = get_default_manager()

# Ejemplo 1: 50/50 split
manager.enable_ab_test(
    'classification',
    variants={1: 0.5, 2: 0.5},
    strategy='weighted'
)

# Ejemplo 2: Gradual rollout
manager.enable_ab_test(
    'sql_generation',
    variants={1: 0.8, 2: 0.2},  # 80% v1, 20% v2
    strategy='weighted'
)

# Ejemplo 3: Round robin (testing)
manager.enable_ab_test(
    'general_response',
    variants={1: 0.33, 2: 0.33, 3: 0.34},
    strategy='round_robin'
)
```

### Métricas a Trackear

```python
# Obtener estadísticas
stats = manager.get_ab_test_stats('classification')
print(stats)
# {
#     'enabled': True,
#     'strategy': 'weighted',
#     'variants': {1: 0.5, 2: 0.5},
#     'usage': {1: 1247, 2: 1253}
# }

# Análisis completo
metrics = manager.get_metrics('classification')
```

### Proceso de A/B Testing

1. **Preparación**
   - Definir hipótesis clara
   - Crear nueva versión del prompt
   - Configurar distribución inicial (ej: 90/10)

2. **Ejecución**
   - Recolectar datos durante período definido
   - Monitorear métricas clave (accuracy, latencia, costo)
   - Registrar feedback de usuarios

3. **Análisis**
   - Comparar métricas entre versiones
   - Validar significancia estadística
   - Decidir versión ganadora

4. **Rollout**
   - Incrementar gradualmente tráfico a versión ganadora
   - Monitorear por regresiones
   - Establecer como default

---

## 🎨 Variables en Templates

### Variables Básicas

```python
# Sintaxis Jinja2
prompt = manager.get_prompt(
    'sql_generation',
    user_query="¿Cuántos usuarios hay?",
    database_schema=schema_text
)
```

### Variables con Valores por Defecto

```python
PROMPT_WITH_DEFAULTS = Template("""
Genera SQL con máximo {{ max_results|default(100) }} resultados.
Nivel de detalle: {{ detail_level|default('normal') }}
""")

# Uso
prompt = manager.get_prompt(
    'custom',
    user_query="test"
    # max_results usará default: 100
    # detail_level usará default: 'normal'
)
```

### Condicionales

```python
CONDITIONAL_PROMPT = Template("""
Pregunta: {{ user_query }}

{% if context %}
Contexto adicional: {{ context }}
{% endif %}

{% if priority == 'high' %}
⚠️ URGENTE: Priorizar precisión sobre velocidad
{% else %}
Optimizar para velocidad de respuesta
{% endif %}
""")
```

### Loops

```python
MULTI_TABLE_PROMPT = Template("""
Tablas disponibles:
{% for table in tables %}
- {{ table.name }}: {{ table.description }}
  Columnas: {{ table.columns|join(', ') }}
{% endfor %}
""")
```

---

## ⚡ Optimización de Prompts

### 1. Reducir Tokens

```python
# ❌ Verboso (muchos tokens)
"""
Por favor, necesito que generes una consulta SQL que sea muy segura
y que no modifique ningún dato de la base de datos. Es muy importante
que uses solamente SELECT y que no uses ningún comando peligroso como
DELETE o DROP TABLE porque eso sería muy malo...
"""

# ✅ Conciso y claro
"""
Genera consulta SQL de solo lectura.
SOLO SELECT - prohibido: INSERT, UPDATE, DELETE, DROP, ALTER.
"""
```

### 2. Estructura Clara

```python
# ❌ Sin estructura
"""
Dada esta base de datos genera SQL para la pregunta del usuario pero
recuerda que debe ser seguro y usar el esquema correcto además de
responder solo con SQL sin markdown...
"""

# ✅ Con estructura
"""
ESQUEMA: {{ schema }}
PREGUNTA: "{{ query }}"

REGLAS:
1. Solo SELECT
2. Usar nombres exactos del esquema
3. Sin markdown en respuesta

SQL:
"""
```

### 3. Pocos-Shot Learning (Ejemplos)

```python
FEW_SHOT_PROMPT = Template("""
Genera SQL basado en estos ejemplos:

Ejemplo 1:
Pregunta: "¿Cuántos usuarios hay?"
SQL: SELECT COUNT(*) as total FROM usuarios

Ejemplo 2:
Pregunta: "Lista los 5 productos más caros"
SQL: SELECT TOP 5 nombre, precio FROM productos ORDER BY precio DESC

Ahora tu turno:
Pregunta: "{{ user_query }}"
SQL:
""")
```

### 4. Chain of Thought (para tareas complejas)

```python
COT_PROMPT = Template("""
Analiza paso a paso:

1. ¿Qué información necesita el usuario?
2. ¿Qué tablas contienen esa información?
3. ¿Se necesitan JOINs? ¿Cuáles?
4. ¿Hay filtros o condiciones?
5. ¿Se necesita agregación?

Pregunta: "{{ user_query }}"
Esquema: {{ schema }}

Razonamiento:
[Piensa aquí]

SQL Final:
""")
```

---

## 🐛 Troubleshooting

### Problema: Prompts no se cargan

```python
# Error
ValueError: No hay versiones disponibles para prompt tipo: clasificacion

# Solución
# 1. Verificar que el nombre esté correcto (minúsculas, sin acentos)
manager.get_prompt('classification', ...)  # ✅

# 2. Listar prompts disponibles
available = manager.list_prompts()
print(available)
```

### Problema: A/B testing no funciona

```python
# Verificar configuración
stats = manager.get_ab_test_stats('classification')
print(stats)

# Verificar que suma de pesos = 1.0
variants = {1: 0.3, 2: 0.3, 3: 0.3}  # ❌ Suma = 0.9
variants = {1: 0.33, 2: 0.33, 3: 0.34}  # ✅ Suma = 1.0
```

### Problema: Variables no se reemplazan

```python
# ❌ Variable no definida en template
PROMPT = Template("Pregunta: {{ question }}")
manager.get_prompt('test', user_query="test")  # Error: 'question' undefined

# ✅ Usar nombres consistentes
PROMPT = Template("Pregunta: {{ user_query }}")
manager.get_prompt('test', user_query="test")  # ✅
```

---

## 💡 Ejemplos Prácticos

### Ejemplo 1: Crear Nuevo Prompt

```python
# 1. Agregar a prompt_templates.py
class PromptTemplates:

    DATA_VALIDATION_V1 = Template("""
Valida si los siguientes datos son correctos:

Datos: {{ data }}

Reglas de validación:
{% for rule in validation_rules %}
- {{ rule }}
{% endfor %}

Responde con JSON:
{
  "is_valid": true/false,
  "errors": ["lista de errores"],
  "warnings": ["lista de advertencias"]
}
""")

# 2. Usar en código
from src.agent.prompts import get_default_manager

manager = get_default_manager()
result = manager.get_prompt(
    'data_validation',
    data='{"email": "user@example"}',
    validation_rules=['Email debe tener @', 'Email debe tener dominio']
)
```

### Ejemplo 2: Migrar Prompt Hardcoded

```python
# ❌ ANTES (hardcoded)
def classify_urgency(message: str) -> str:
    prompt = f"""
    ¿Este mensaje es urgente?
    Mensaje: {message}
    Responde: urgente/normal/bajo
    """
    return llm.generate(prompt)

# ✅ DESPUÉS (usando sistema de prompts)
# 1. Agregar template
URGENCY_CLASSIFICATION_V1 = Template("""
Clasifica la urgencia del siguiente mensaje.

Mensaje: "{{ message }}"

Responde con UNA palabra:
- urgente: requiere atención inmediata
- normal: atención regular
- bajo: puede esperar

Clasificación:
""")

# 2. Refactorizar código
def classify_urgency(message: str) -> str:
    from src.agent.prompts import get_default_manager

    manager = get_default_manager()
    prompt = manager.get_prompt(
        'urgency_classification',
        message=message
    )
    return llm.generate(prompt)
```

### Ejemplo 3: Configurar Diferentes Versiones por Entorno

```python
# config/prompt_config.py
from src.agent.prompts import get_default_manager

def configure_prompts_for_environment(env: str):
    manager = get_default_manager()

    if env == "production":
        # Versiones estables en producción
        manager.set_default_version('classification', 2)
        manager.set_default_version('sql_generation', 3)
        manager.set_default_version('general_response', 1)

    elif env == "staging":
        # A/B testing en staging
        manager.enable_ab_test('classification', {2: 0.7, 3: 0.3})
        manager.enable_ab_test('sql_generation', {3: 0.5, 4: 0.5})

    elif env == "development":
        # Siempre usar últimas versiones en dev
        # (comportamiento por defecto)
        pass

# main.py
from src.config.settings import settings
configure_prompts_for_environment(settings.environment)
```

---

## 📊 Checklist de Calidad de Prompts

Antes de crear una nueva versión de prompt, verificar:

- [ ] **Claridad**: ¿Las instrucciones son claras e inequívocas?
- [ ] **Completitud**: ¿Incluye todos los casos edge?
- [ ] **Seguridad**: ¿Previene comportamientos no deseados?
- [ ] **Eficiencia**: ¿Usa la mínima cantidad de tokens necesaria?
- [ ] **Testeable**: ¿Tiene casos de prueba definidos?
- [ ] **Versionado**: ¿Sigue la convención NOMBRE_VN?
- [ ] **Documentación**: ¿Está documentado el cambio vs versión anterior?
- [ ] **Variables**: ¿Todas las variables tienen defaults o son requeridas?

---

## 🔗 Referencias

- [Documentación Jinja2](https://jinja.palletsprojects.com/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [OpenAI Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Library](https://docs.anthropic.com/claude/prompt-library)

---

**Última revisión:** 2025-10-29
**Mantenido por:** Equipo de IA
**Versión del documento:** 1.0
