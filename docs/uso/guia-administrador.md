# Guía de administrador

Esta guía cubre las tareas de administración del bot: gestión de usuarios, permisos,
base de conocimiento y monitoreo.

Todas las operaciones se realizan directamente sobre la base de datos `abcmasplus`.

---

## Gestión de usuarios

### Registrar un usuario nuevo

Los usuarios se registran ellos mismos vía Telegram (`/register` + `/verify`). El sistema
crea automáticamente el registro en `BotIAv2_UsuariosTelegram` una vez verificado.

Para que un usuario pueda registrarse, debe existir previamente en la tabla `Usuarios`
con el campo `activo = 1`.

### Activar / desactivar un usuario

```sql
-- Desactivar usuario (ya no puede usar el bot)
UPDATE abcmasplus..BotIAv2_UsuariosTelegram
SET activo = 0
WHERE telegramChatId = <chat_id>;

-- Reactivar usuario
UPDATE abcmasplus..BotIAv2_UsuariosTelegram
SET activo = 1
WHERE telegramChatId = <chat_id>;
```

### Consultar usuarios registrados

```sql
SELECT
    ut.telegramChatId,
    ut.telegramUsername,
    u.nombre + ' ' + u.apellido AS nombre_completo,
    u.idEmpleado,
    ut.activo,
    ut.fechaRegistro
FROM abcmasplus..BotIAv2_UsuariosTelegram ut
INNER JOIN abcmasplus..Usuarios u ON ut.idUsuario = u.idUsuario
ORDER BY ut.fechaRegistro DESC;
```

---

## Gestión de permisos

El sistema de permisos (SEC-01) controla qué herramientas y comandos puede usar cada usuario.
La jerarquía es:

```
esPublico=1 en BotIAv2_Recurso  →  acceso universal (sin verificar)
      ↓
tipo 'usuario' (definitivo)      →  override individual, pisa todo lo demás
      ↓
tipo 'autenticado'/'gerencia'/'direccion' (permisivos)  →  si alguno permite, se permite
      ↓
sin filas                        →  denegado por defecto
```

### Ver recursos disponibles

```sql
SELECT recurso, tipoRecurso, descripcion, esPublico
FROM abcmasplus..BotIAv2_Recurso
ORDER BY tipoRecurso, recurso;
```

Recursos típicos:

| recurso | tipo |
|---------|------|
| `tool:database_query` | tool |
| `tool:knowledge_search` | tool |
| `tool:calculate` | tool |
| `tool:save_preference` | tool |
| `cmd:/ia` | cmd |
| `cmd:/start` | cmd (público) |

### Permitir una tool a un rol

```sql
-- Ejemplo: permitir tool:database_query para rol Gerente (idRol=2)
DECLARE @idRecurso INT = (SELECT idRecurso FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:database_query');
DECLARE @idAutenticado INT = (SELECT idTipoEntidad FROM abcmasplus..BotIAv2_TipoEntidad WHERE nombre = 'autenticado');

INSERT INTO abcmasplus..BotIAv2_Permisos (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido)
VALUES (@idAutenticado, 0, @idRecurso, 2, 1);
```

### Denegar una tool a un usuario específico

```sql
-- Override individual que pisa cualquier permiso de rol
DECLARE @idUsuario_tipo INT = (SELECT idTipoEntidad FROM abcmasplus..BotIAv2_TipoEntidad WHERE nombre = 'usuario');
DECLARE @idRecurso INT = (SELECT idRecurso FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:database_query');

INSERT INTO abcmasplus..BotIAv2_Permisos (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido)
VALUES (@idUsuario_tipo, <idUsuario>, @idRecurso, NULL, 0);
```

### Recargar permisos en caliente

Los permisos se cachean por 5 minutos. Para forzar recarga inmediata sin reiniciar el bot:

El usuario puede enviar al bot:
```
/recargar_permisos
```

O bien esperar que el TTL expire automáticamente.

---

## Base de conocimiento

La base de conocimiento son artículos que Amber puede recuperar cuando el usuario pregunta
sobre políticas, procedimientos o información interna.

### Estructura

Cada artículo pertenece a una **categoría** y tiene:
- `question`: la pregunta o título del artículo
- `answer`: la respuesta completa en texto
- `keywords`: lista JSON de palabras clave para la búsqueda
- `priority`: 1 (normal), 2 (alta), 3 (crítica)

### Categorías disponibles

| nombre | descripción |
|--------|-------------|
| `PROCESOS` | Procedimientos operativos |
| `POLITICAS` | Políticas de la empresa |
| `FAQS` | Preguntas frecuentes |
| `CONTACTOS` | Directorio de contactos |
| `RECURSOS_HUMANOS` | Temas de RRHH |
| `SISTEMAS` | Guías de sistemas internos |
| `BASE_DATOS` | Documentación de datos |

### Agregar un artículo

```sql
-- 1. Obtener el id de la categoría
SELECT id, name FROM abcmasplus..knowledge_categories WHERE active = 1;

-- 2. Insertar el artículo
INSERT INTO abcmasplus..knowledge_entries
    (category_id, question, answer, keywords, priority, active)
VALUES (
    2,   -- id de categoría POLITICAS
    'Política de devoluciones',
    'Los productos pueden devolverse dentro de los 30 días de la compra...',
    '["devolución", "devolver", "cambio", "reintegro"]',
    2,   -- prioridad alta
    1
);
```

### Desactivar un artículo

```sql
UPDATE abcmasplus..knowledge_entries
SET active = 0
WHERE id = <id_articulo>;
```

### Controlar acceso por rol a una categoría

```sql
-- Permitir que el rol 3 vea la categoría RRHH
INSERT INTO abcmasplus..RolesCategoriesKnowledge (idRol, idCategoria, permitido)
VALUES (3, (SELECT id FROM knowledge_categories WHERE name = 'RECURSOS_HUMANOS'), 1);
```

---

## Monitoreo

### Ver las últimas interacciones

```sql
SELECT TOP 50
    il.correlationId,
    il.telegramChatId,
    il.mensajeUsuario,
    il.respuestaBot,
    il.exitoso,
    il.duracionMs,
    il.fechaInteraccion
FROM abcmasplus..BotIAv2_InteractionLogs il
ORDER BY il.fechaInteraccion DESC;
```

### Ver errores recientes

```sql
SELECT TOP 20
    al.nivel,
    al.mensaje,
    al.excepcion,
    al.correlationId,
    al.timestamp
FROM abcmasplus..BotIAv2_ApplicationLogs al
WHERE al.nivel IN ('ERROR', 'CRITICAL')
ORDER BY al.timestamp DESC;
```

### Ver costos de uso del LLM

```sql
SELECT
    CAST(cs.fechaCreacion AS DATE) AS fecha,
    COUNT(*) AS sesiones,
    SUM(cs.llamadasLLM) AS total_llamadas,
    SUM(cs.costoUSD) AS costo_total_usd
FROM abcmasplus..BotIAv2_CostSesiones cs
GROUP BY CAST(cs.fechaCreacion AS DATE)
ORDER BY fecha DESC;
```
