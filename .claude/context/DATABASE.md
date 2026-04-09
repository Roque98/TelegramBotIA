# Base de Datos

## Configuración

| Campo | Valor |
|-------|-------|
| **Motor** | SQL Server / MySQL |
| **Base de datos** | `abcmasplus` |
| **ORM** | SQLAlchemy 2.0 |
| **Pool** | 5 conexiones + 10 overflow |
| **Timeout** | 20 segundos |

---

## Tablas Principales

### Usuarios y Autenticación

#### Usuarios
```sql
CREATE TABLE Usuarios (
    idUsuario INT PRIMARY KEY,
    idEmpleado INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    rol INT NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    fechaCreacion DATETIME NOT NULL,
    fechaUltimoAcceso DATETIME NULL,
    activo BIT NOT NULL
);
```

#### UsuariosTelegram
```sql
-- Vincula usuarios con Telegram
telegram_id BIGINT UNIQUE,
idUsuario INT FK,
username VARCHAR(100),
verificado BIT,
codigo_verificacion VARCHAR(10)
```

---

### Knowledge Base

#### knowledge_categories
```sql
CREATE TABLE knowledge_categories (
    id INT PRIMARY KEY IDENTITY,
    name VARCHAR(50) UNIQUE NOT NULL,      -- 'PROCESOS', 'POLITICAS', etc.
    display_name NVARCHAR(100) NOT NULL,
    description NVARCHAR(500),
    icon NVARCHAR(10),                      -- Emoji
    active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE()
);
```

**Categorías predefinidas**:
| name | display_name | icon |
|------|--------------|------|
| PROCESOS | Procesos | ⚙️ |
| POLITICAS | Políticas | 📋 |
| FAQS | Preguntas frecuentes | ❓ |
| CONTACTOS | Contactos | 📞 |
| RECURSOS_HUMANOS | RRHH | 👥 |
| SISTEMAS | Sistemas | 💻 |
| BASE_DATOS | Base de datos | 🗄️ |

#### knowledge_entries
```sql
CREATE TABLE knowledge_entries (
    id INT PRIMARY KEY IDENTITY,
    category_id INT FK NOT NULL,
    question NVARCHAR(500) NOT NULL,
    answer NVARCHAR(MAX) NOT NULL,
    keywords NVARCHAR(MAX) NOT NULL,       -- JSON: ["palabra1", "palabra2"]
    related_commands NVARCHAR(500),        -- JSON: ["/help", "/ia"]
    priority INT DEFAULT 1,                -- 1=normal, 2=high, 3=critical
    active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE()
);
```

---

### Memoria de Usuario

#### UserMemoryProfiles
```sql
CREATE TABLE UserMemoryProfiles (
    idMemoryProfile INT PRIMARY KEY IDENTITY,
    idUsuario INT FK UNIQUE NOT NULL,
    resumenContextoLaboral NVARCHAR(MAX),   -- "Usuario del área de ventas..."
    resumenTemasRecientes NVARCHAR(MAX),    -- "Últimamente pregunta sobre..."
    resumenHistorialBreve NVARCHAR(MAX),    -- "Ha realizado 45 consultas..."
    numInteracciones INT DEFAULT 0,
    ultimaActualizacion DATETIME2 DEFAULT GETDATE(),
    fechaCreacion DATETIME2 DEFAULT GETDATE(),
    version INT DEFAULT 1
);
```

---

### Permisos y Roles

#### Roles
```sql
CREATE TABLE Roles (
    idRol INT PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    activo BIT NOT NULL
);
```

#### RolesCategoriesKnowledge
```sql
-- Controla qué roles pueden ver qué categorías de knowledge
CREATE TABLE RolesCategoriesKnowledge (
    idRolCategoria INT PRIMARY KEY,
    idRol INT FK NOT NULL,
    idCategoria INT FK NOT NULL,
    permitido BIT NOT NULL,
    activo BIT DEFAULT 1,
    UNIQUE (idRol, idCategoria)
);
```

#### ~~RolesOperaciones~~ *(legacy — pendiente DROP)*
```sql
-- Reemplazada por BotPermisos (SEC-01). Ver migration 21_DropLegacyPermisosTablas.sql
```

#### Operaciones
```sql
CREATE TABLE Operaciones (
    idOperacion INT PRIMARY KEY,
    idModulo INT FK NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(500),
    comando VARCHAR(100),              -- '/ia', '/stats', etc.
    requiereParametros BIT NOT NULL,
    nivelCriticidad INT NOT NULL,
    activo BIT NOT NULL
);
```

---

### Logs y Auditoría

#### LogOperaciones
```sql
CREATE TABLE LogOperaciones (
    idLog BIGINT PRIMARY KEY IDENTITY,
    idUsuario INT FK NOT NULL,
    idOperacion INT FK NOT NULL,
    telegramChatId BIGINT,
    telegramUsername VARCHAR(100),
    parametros TEXT,                   -- JSON con query del usuario
    resultado VARCHAR(50),             -- 'EXITOSO', 'ERROR', 'DENEGADO'
    mensajeError TEXT,
    duracionMs INT,
    ipOrigen VARCHAR(50),
    fechaEjecucion DATETIME NOT NULL
);
```

---

### Chat e IA

#### ChatConversaciones
```sql
CREATE TABLE ChatConversaciones (
    IdConversacion INT PRIMARY KEY,
    IdUsuario INT FK NOT NULL,
    Titulo VARCHAR(200),
    Modelo VARCHAR(100),               -- 'gpt-4', 'claude-3-sonnet'
    Temperatura DECIMAL(3,2),
    MaxTokens INT,
    MensajeSistema TEXT,
    TotalMensajes INT DEFAULT 0,
    TotalTokensUsados INT DEFAULT 0,
    CostoTotal DECIMAL(10,4) DEFAULT 0,
    Activa BIT DEFAULT 1,
    FechaCreacion DATETIME NOT NULL
);
```

#### ChatMensajes
```sql
CREATE TABLE ChatMensajes (
    IdMensaje INT PRIMARY KEY,
    IdConversacion INT FK NOT NULL,
    Rol VARCHAR(20) NOT NULL,          -- 'user', 'assistant'
    Contenido TEXT NOT NULL,
    TokensPrompt INT,
    TokensCompletion INT,
    TiempoRespuestaMs INT,
    Costo DECIMAL(10,6),
    Modelo VARCHAR(100),
    FechaCreacion DATETIME NOT NULL
);
```

---

## Stored Procedures

### sp_search_knowledge
```sql
EXEC sp_search_knowledge
    @query = 'política devoluciones',
    @category = NULL,              -- o 'POLITICAS'
    @top_k = 3,
    @min_priority = 1
```

**Retorna**: Entradas ordenadas por prioridad + relevancia

---

## Queries Comunes

### Buscar en Knowledge Base
```python
# KnowledgeRepository.search_entries()
query = """
SELECT e.*, c.name as category_name
FROM knowledge_entries e
JOIN knowledge_categories c ON e.category_id = c.id
WHERE e.active = 1 AND c.active = 1
  AND (e.question LIKE ? OR e.keywords LIKE ?)
ORDER BY e.priority DESC
"""
```

### Obtener perfil de memoria
```python
# MemoryRepository.get_user_memory_profile()
query = """
SELECT * FROM UserMemoryProfiles
WHERE idUsuario = :user_id
"""
```

### Guardar perfil de memoria
```python
# MemoryRepository.save_memory_profile()
# INSERT si no existe, UPDATE si existe
query = """
MERGE INTO UserMemoryProfiles AS target
USING (SELECT :user_id AS idUsuario) AS source
ON target.idUsuario = source.idUsuario
WHEN MATCHED THEN
    UPDATE SET resumenContextoLaboral = :contexto, ...
WHEN NOT MATCHED THEN
    INSERT (idUsuario, ...) VALUES (:user_id, ...)
"""
```

### Verificar permisos (SEC-01)
```python
# PermissionService.can() — nuevo sistema
permisos = await permission_service.get_all_for_user(
    user_id=10, role_id=2, gerencia_ids=[1], direccion_ids=[]
)
tiene_permiso = permisos.get("tool:database_query", False)

# Cache LRU TTL 60s por user_id
# Invalidar: permission_service.invalidate(user_id)
```

---

## Conexión

### DatabaseManager
```python
# src/database/connection.py

class DatabaseManager:
    async def get_session(self) -> AsyncSession
    async def execute_query(self, sql: str, params: list = None) -> list[dict]
    async def get_schema(self) -> dict  # Para SQLGenerator
    async def close(self)
```

### Configuración
```python
# src/config/settings.py

class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 1433
    db_name: str = "abcmasplus"
    db_user: str
    db_password: str
    db_type: str = "mssql"  # mssql, mysql, postgresql

    @property
    def database_url(self) -> str:
        # Construye URL según db_type
```

---

## Sistema de Permisos SEC-01

### Tablas nuevas (Migration 10–11)

#### BotTipoEntidad — catálogo de tipos de entidad
| nombre | prioridad | tipoResolucion | descripción |
|--------|-----------|----------------|-------------|
| usuario | 1 | definitivo | Override individual, pisa todo |
| autenticado | 2 | permisivo | Cualquier usuario autenticado (filtrable por rol) |
| gerencia | 3 | permisivo | Gerencia del usuario (filtrable por rol) |
| direccion | 4 | permisivo | Dirección del usuario (filtrable por rol) |

#### BotRecurso — catálogo de recursos controlables
| recurso | tipoRecurso | esPublico |
|---------|-------------|-----------|
| `tool:database_query` | tool | 0 |
| `tool:calculate` | tool | 0 |
| `cmd:/ia` | cmd | 0 |
| `cmd:/start` | cmd | 1 ← público |
| `cmd:/recargar_permisos` | cmd | 1 ← público |
| `tool:reload_permissions` | tool | 1 ← público |

#### BotPermisos — reglas de acceso
- `idTipoEntidad` → tipo de entidad (usuario/autenticado/gerencia/direccion)
- `idEntidad` → ID del usuario/gerencia/dirección (0 para autenticado)
- `idRecurso` → recurso a controlar
- `idRolRequerido` → NULL = cualquier rol, valor = rol específico
- `permitido` → 1=permitido, 0=denegado
- `fechaExpiracion` → NULL=permanente

### Jerarquía de resolución

```
1. esPublico=1 en BotRecurso → PERMITIDO inmediatamente
2. Entrada 'definitivo' (usuario) → respuesta final
3. Entre 'permisivo' → si ALGUNA permite, PERMITIDO
4. Sin filas → DENEGADO (default deny)
```

### Cómo agregar un nuevo permiso

```sql
-- Permitir tool:nueva_tool para rol Gerente (idRol=2)
INSERT INTO abcmasplus..BotRecurso (recurso, tipoRecurso, descripcion)
VALUES ('tool:nueva_tool', 'tool', 'Descripción de la nueva tool');

DECLARE @idRecurso INT = SCOPE_IDENTITY();
DECLARE @idAutenticado INT = (SELECT idTipoEntidad FROM BotTipoEntidad WHERE nombre='autenticado');

INSERT INTO abcmasplus..BotPermisos (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido)
VALUES (@idAutenticado, 0, @idRecurso, 2, 1);
```

### Cómo denegar un recurso a un usuario específico

```sql
-- Denegar tool:database_query al usuario idUsuario=15 (override definitivo)
DECLARE @idUsuario INT = (SELECT idTipoEntidad FROM BotTipoEntidad WHERE nombre='usuario');
DECLARE @idRecurso INT = (SELECT idRecurso FROM BotRecurso WHERE recurso='tool:database_query');

INSERT INTO abcmasplus..BotPermisos (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido)
VALUES (@idUsuario, 15, @idRecurso, NULL, 0);
-- El deny definitivo pisa cualquier allow de rol/gerencia
```

---

## Migraciones

```
database/migrations/
├── 09_PreMigracionCheck.sql          -- Verificación pre-migración
├── 10_BotPermisos.sql                -- Crear BotTipoEntidad, BotRecurso, BotPermisos, BotPermisosAudit
├── 11_BotPermisos_DatosIniciales.sql -- Datos iniciales por rol (1–8)
├── 20_DropLegacyPermisosSPs.sql      -- DROP sp_VerificarPermisoOperacion, sp_ObtenerOperacionesUsuario
└── 21_DropLegacyPermisosTablas.sql   -- DROP RolesOperaciones, RolesIA, GerenciasRolesIA
```

---

## Seguridad

### SQLValidator
- Solo permite `SELECT`, `EXEC`, `WITH`
- Rechaza `INSERT`, `UPDATE`, `DELETE`, `DROP`
- Rechaza comentarios `--`, `/*`, `*/`
- Rechaza múltiples statements (`;`)

### Queries parametrizadas
```python
# ✅ Correcto
db.execute_query("SELECT * FROM users WHERE id = ?", [user_id])

# ❌ Incorrecto (SQL injection)
db.execute_query(f"SELECT * FROM users WHERE id = {user_id}")
```

---

## Tablas ARQ-35: Agentes Dinámicos

### BotIAv2_AgenteDef
```sql
idAgente           INT PK IDENTITY
nombre             VARCHAR(100) UNIQUE   -- 'datos', 'conocimiento', 'casual', 'generalista'
descripcion        VARCHAR(500)          -- usada por IntentClassifier para rutear
systemPrompt       NVARCHAR(MAX)         -- debe contener {tools_description} y {usage_hints}
temperatura        DECIMAL(3,2)          -- temperatura del LLM
maxIteraciones     INT                   -- max_iterations del ReActAgent
modeloOverride     VARCHAR(100) NULL     -- NULL = usa openai_loop_model del sistema
esGeneralista      BIT                   -- 1 = ignora tool_scope, usa permisos directos del usuario
activo             BIT
version            INT                   -- incrementado automáticamente por trigger al cambiar prompt
fechaActualizacion DATETIME2
```

### BotIAv2_AgenteTools
```sql
idAgenteTools  INT PK IDENTITY
idAgente       INT FK → BotIAv2_AgenteDef
nombreTool     VARCHAR(100)   -- 'database_query', 'knowledge_search', etc.
activo         BIT
UNIQUE(idAgente, nombreTool)
```

### BotIAv2_AgentePromptHistorial (append-only)
```sql
idHistorial   INT PK IDENTITY
idAgente      INT FK → BotIAv2_AgenteDef
systemPrompt  NVARCHAR(MAX)   -- versión anterior del prompt
version       INT             -- versión guardada
razonCambio   VARCHAR(500)
modificadoPor VARCHAR(100)
fechaCreacion DATETIME2
```

### Trigger TR_AgenteDef_VersionHistorial
- Se dispara en `UPDATE` de `systemPrompt` en `BotIAv2_AgenteDef`
- Inserta la versión anterior en `BotIAv2_AgentePromptHistorial`
- Incrementa `version` en la fila actualizada
- Permite cache de instancias keyed por `(idAgente, version)` en `AgentBuilder`

### BotIAv2_InteractionLogs (columna agregada)
```sql
agenteNombre   VARCHAR(100) NULL   -- ARQ-35: nombre del agente que respondió
```
```
