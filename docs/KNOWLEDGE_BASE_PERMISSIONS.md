# Sistema de Permisos para Knowledge Base

## Descripción General

El sistema de **Knowledge Base con Control de Acceso por Rol** permite restringir qué categorías de conocimiento puede ver cada usuario basándose en su rol. Esto garantiza que los usuarios solo tengan acceso a la información relevante para su función.

---

## Arquitectura

### Tablas Involucradas

1. **knowledge_categories** - Categorías de conocimiento (PROCESOS, POLITICAS, FAQS, etc.)
2. **knowledge_entries** - Entradas de conocimiento individual
3. **Roles** - Roles del sistema
4. **RolesCategoriesKnowledge** - Tabla de relación que controla qué roles tienen acceso a qué categorías

### Tabla RolesCategoriesKnowledge

```sql
CREATE TABLE [dbo].[RolesCategoriesKnowledge] (
    idRolCategoria INT IDENTITY(1,1) PRIMARY KEY,
    idRol INT NOT NULL,
    idCategoria INT NOT NULL,
    permitido BIT NOT NULL DEFAULT 1,
    fechaAsignacion DATETIME DEFAULT GETDATE(),
    usuarioAsignacion INT NULL,
    activo BIT DEFAULT 1,
    CONSTRAINT FK_RolesCategoriesKnowledge_Roles
        FOREIGN KEY (idRol) REFERENCES Roles(idRol),
    CONSTRAINT FK_RolesCategoriesKnowledge_Categories
        FOREIGN KEY (idCategoria) REFERENCES knowledge_categories(id),
    CONSTRAINT UQ_RolCategoria UNIQUE(idRol, idCategoria)
);
```

---

## Flujo de Funcionamiento

### 1. Inicialización del Sistema

Cuando se crea un `KnowledgeManager` o `QueryClassifier`, se pasa el `id_rol` del usuario:

```python
# Ejemplo de uso con rol
knowledge_manager = KnowledgeManager(db_manager=db_manager, id_rol=5)

# El manager carga automáticamente solo las categorías permitidas para el rol 5
```

### 2. Carga de Entradas Filtradas

El `KnowledgeRepository` consulta automáticamente qué categorías están permitidas:

```python
# En KnowledgeRepository
allowed_categories = self.get_allowed_categories_by_role(id_rol=5)
# Retorna: [1, 2, 4]  (IDs de categorías permitidas)

# Luego filtra las entradas
entries = self.get_all_entries_by_role(id_rol=5)
# Solo retorna entradas de las categorías 1, 2 y 4
```

### 3. Búsqueda con Permisos

Cuando un usuario realiza una búsqueda, solo ve resultados de categorías permitidas:

```python
# El usuario pregunta algo
query = "¿Cómo solicito vacaciones?"

# El clasificador busca con filtro de rol
results = knowledge_manager.search(query, top_k=3)
# Solo retorna resultados de categorías permitidas para el rol del usuario
```

---

## Componentes Modificados

### 1. KnowledgeRepository

**Nuevos métodos:**

- `get_allowed_categories_by_role(id_rol: int) -> List[int]`
  - Obtiene IDs de categorías permitidas para un rol
  - Incluye cache para optimizar rendimiento

- `get_all_entries_by_role(id_rol: Optional[int]) -> List[KnowledgeEntry]`
  - Obtiene entradas filtradas por permisos de rol
  - Si `id_rol=None`, retorna todas las entradas

**Métodos modificados:**

- `search_entries(..., id_rol: Optional[int])`
  - Ahora filtra resultados por categorías permitidas

- `get_categories_info(id_rol: Optional[int])`
  - Retorna solo categorías permitidas para el rol

### 2. KnowledgeManager

**Modificaciones en `__init__`:**

```python
def __init__(
    self,
    db_manager: Optional[DatabaseManager] = None,
    id_rol: Optional[int] = None
):
    """
    Args:
        db_manager: Gestor de base de datos
        id_rol: ID del rol para filtrar conocimiento
    """
    # Carga automáticamente solo las entradas permitidas para el rol
```

### 3. QueryClassifier

**Modificaciones en `__init__`:**

```python
def __init__(
    self,
    llm_provider: LLMProvider,
    prompt_version: Optional[int] = None,
    knowledge_manager: Optional[KnowledgeManager] = None,
    id_rol: Optional[int] = None,
    db_manager: Optional[DatabaseManager] = None
):
    """
    Crea KnowledgeManager con filtro de rol automáticamente
    """
```

---

## Uso en el Flujo del Bot

### Ejemplo Completo

```python
from src.agent.llm_agent import LLMAgent
from src.database.connection import DatabaseManager

# 1. Usuario se autentica
user = get_authenticated_user(telegram_chat_id)
id_rol = user.rol  # Ej: 5 (Analista)

# 2. Crear agente con rol del usuario
db_manager = DatabaseManager()
agent = LLMAgent(db_manager=db_manager)

# 3. El agente usa QueryClassifier con rol
# Internamente, QueryClassifier pasa el id_rol al KnowledgeManager
query_classifier = QueryClassifier(
    llm_provider=agent.llm_provider,
    id_rol=id_rol,
    db_manager=db_manager
)

# 4. Usuario hace pregunta
response = await agent.process_query("¿Cómo solicito vacaciones?")

# El sistema automáticamente:
# - Busca solo en categorías permitidas para rol 5
# - Clasifica la consulta
# - Retorna respuesta con conocimiento filtrado
```

---

## Configuración de Permisos

### Asignar Categoría a Rol

```sql
-- Permitir al rol 5 (Analista) acceso a PROCESOS
INSERT INTO RolesCategoriesKnowledge
    (idRol, idCategoria, permitido, activo, usuarioAsignacion)
VALUES
    (5, 1, 1, 1, 1);  -- 1 = PROCESOS

-- Permitir múltiples categorías
INSERT INTO RolesCategoriesKnowledge
    (idRol, idCategoria, permitido, activo)
VALUES
    (5, 2, 1, 1),  -- POLITICAS
    (5, 3, 1, 1),  -- FAQS
    (5, 4, 1, 1);  -- CONTACTOS
```

### Revocar Acceso

```sql
-- Revocar acceso del rol 5 a POLITICAS
UPDATE RolesCategoriesKnowledge
SET activo = 0
WHERE idRol = 5 AND idCategoria = 2;
```

### Ver Permisos de un Rol

```sql
-- Ver categorías permitidas para rol 5
SELECT
    c.id,
    c.name,
    c.display_name,
    rc.fechaAsignacion
FROM RolesCategoriesKnowledge rc
INNER JOIN knowledge_categories c ON rc.idCategoria = c.id
WHERE rc.idRol = 5
    AND rc.permitido = 1
    AND rc.activo = 1;
```

---

## Ventajas del Sistema

### 1. **Seguridad**
- Control granular sobre qué información ve cada rol
- Previene acceso a información sensible

### 2. **Escalabilidad**
- Fácil de agregar nuevas categorías
- Fácil de modificar permisos sin cambiar código

### 3. **Performance**
- Cache de permisos por rol
- Filtrado a nivel de base de datos
- Solo carga datos necesarios

### 4. **Trazabilidad**
- Registro de quién asignó permisos
- Fecha de asignación
- Auditoría completa

---

## Ejemplos de Configuración

### Caso 1: Rol de Administrador

```sql
-- Administrador (rol 1) tiene acceso a TODAS las categorías
INSERT INTO RolesCategoriesKnowledge (idRol, idCategoria, permitido, activo)
SELECT 1, id, 1, 1
FROM knowledge_categories
WHERE active = 1;
```

### Caso 2: Rol de Usuario Básico

```sql
-- Usuario básico (rol 3) solo ve FAQs y CONTACTOS
INSERT INTO RolesCategoriesKnowledge (idRol, idCategoria, permitido, activo)
SELECT 3, id, 1, 1
FROM knowledge_categories
WHERE name IN ('FAQS', 'CONTACTOS');
```

### Caso 3: Rol de Analista

```sql
-- Analista (rol 5) ve PROCESOS, POLITICAS y DATOS
INSERT INTO RolesCategoriesKnowledge (idRol, idCategoria, permitido, activo)
SELECT 5, id, 1, 1
FROM knowledge_categories
WHERE name IN ('PROCESOS', 'POLITICAS', 'DATOS');
```

---

## Logs y Debugging

El sistema registra logs detallados:

```python
# KnowledgeRepository
logger.info("Rol 5 tiene acceso a 3 categorías: [1, 2, 4]")

# KnowledgeManager
logger.info("✅ KnowledgeManager inicializado desde BD para rol 5 con 15 entradas")

# QueryClassifier
logger.info("Inicializado clasificador con knowledge_base: 15 entradas, rol: 5")

# Búsqueda
logger.debug("Búsqueda con permisos: 10 resultados totales, 3 permitidos para rol 5")
```

---

## Manejo de Errores

### Sin Permisos

Si un rol no tiene acceso a ninguna categoría:

```python
# El sistema retorna lista vacía
entries = repository.get_all_entries_by_role(id_rol=999)
# entries = []

logger.warning("Rol 999 no tiene acceso a ninguna categoría de conocimiento")
```

### Base de Datos No Disponible

```python
# Si la tabla RolesCategoriesKnowledge no existe
# O hay error de conexión
try:
    categories = repository.get_allowed_categories_by_role(5)
except Exception as e:
    logger.error(f"Error al obtener categorías: {e}")
    # Retorna lista vacía (acceso denegado por defecto)
    categories = []
```

---

## Migración y Compatibilidad

### Sin Rol Especificado

El sistema es compatible con código que no usa roles:

```python
# Sin id_rol = Sin filtro (backward compatible)
manager = KnowledgeManager(db_manager=db_manager)  # id_rol=None
# Carga TODAS las entradas

classifier = QueryClassifier(llm_provider=provider)  # id_rol=None
# Sin filtrado de permisos
```

### Migración Gradual

1. Ejecutar script de creación de tabla `RolesCategoriesKnowledge`
2. Asignar permisos a roles existentes
3. Actualizar código para pasar `id_rol` cuando esté disponible
4. El sistema funciona con o sin filtrado

---

## Testing

### Test de Permisos

```python
def test_role_permissions():
    repo = KnowledgeRepository()

    # Test: Rol con permisos
    allowed = repo.get_allowed_categories_by_role(5)
    assert len(allowed) > 0

    # Test: Rol sin permisos
    not_allowed = repo.get_allowed_categories_by_role(999)
    assert len(not_allowed) == 0

    # Test: Filtrado de entradas
    entries_rol_5 = repo.get_all_entries_by_role(5)
    entries_all = repo.get_all_entries()
    assert len(entries_rol_5) <= len(entries_all)
```

---

## Saludo y Categorías Filtradas por Rol

### Mensajes de Bienvenida Personalizados

El bot IRIS ahora personaliza su saludo inicial y la lista de categorías según el rol del usuario:

#### Comandos Afectados

1. **`/start`** - Mensaje de bienvenida
2. **`/help`** - Guía de uso
3. **Saludos conversacionales** - "Hola", "Buenos días", etc.

#### Cómo Funciona

```python
# Cuando un usuario ejecuta /start
async def start_command(update, context):
    # 1. Obtener rol del usuario
    user = update.effective_user
    telegram_user = user_manager.get_user_by_telegram_chat_id(user.id)
    id_rol = telegram_user.usuario.rol  # Ej: 5 (Analista)

    # 2. Obtener solo categorías permitidas para ese rol
    categories = get_categories_from_db(id_rol=id_rol)
    # Solo retorna categorías que el rol 5 puede ver

    # 3. Mostrar mensaje personalizado
    # "Puedo ayudarte con información sobre:"
    # • ⚙️ Procesos
    # • 📋 Políticas
    # (Solo las categorías permitidas para el rol)
```

### Ejemplo Práctico

**Usuario con Rol "Administrador" (id_rol=1):**
```
¡Hola Juan! 👋 Soy IRIS

Puedo ayudarte con información sobre:
⚙️ Procesos
📋 Políticas
❓ Preguntas Frecuentes
📊 Datos
👥 Contactos
📚 Documentación
💼 Recursos Humanos

¿En qué puedo ayudarte hoy? 🎯
```

**Usuario con Rol "Analista" (id_rol=5):**
```
¡Hola María! 👋 Soy IRIS

Puedo ayudarte con información sobre:
⚙️ Procesos
📋 Políticas
❓ Preguntas Frecuentes

¿En qué puedo ayudarte hoy? 🎯
```

El usuario "Analista" solo ve las 3 categorías permitidas para su rol, mientras que el "Administrador" ve todas.

### Flujo Completo

```
Usuario envía: /start
    ↓
Bot obtiene telegram_chat_id
    ↓
Consulta BD: ¿Qué usuario es?
    ↓
Obtiene id_rol del usuario
    ↓
Consulta RolesCategoriesKnowledge
    ↓
Filtra categorías permitidas
    ↓
Genera saludo personalizado
    ↓
Usuario solo ve categorías autorizadas
```

### Beneficios

1. **Experiencia Personalizada** - Cada usuario ve solo lo relevante para su función
2. **Seguridad** - No se menciona ni muestra información de categorías no autorizadas
3. **Claridad** - El usuario sabe exactamente qué puede consultar
4. **Consistencia** - Mismo filtrado en todo el sistema (saludo, búsquedas, respuestas)

---

## Resumen

El sistema de permisos de Knowledge Base proporciona:

✅ **Control de acceso granular** por rol y categoría
✅ **Filtrado automático** en búsquedas y clasificación
✅ **Saludo personalizado** según permisos del usuario
✅ **Cache de permisos** para mejor rendimiento
✅ **Backward compatible** con código existente
✅ **Logs completos** para debugging
✅ **Fácil configuración** vía SQL

El usuario solo ve el conocimiento relevante para su rol, mejorando la seguridad y relevancia de las respuestas del bot IRIS.
