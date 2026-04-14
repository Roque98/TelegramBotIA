[Docs](../index.md) › [Código](README.md) › [Tools](tools.md) › Tools de Alertas

# Tools de Alertas — Documentación Técnica

Sistema de monitoreo PRTG integrado en el bot. Compuesto por **7 tools de datos**
(sin LLM interno) más **1 tool de análisis** (con LLM). Todas usan `AlertRepository`
como capa de acceso a datos con fallback automático BAZ_CDMX → EKT.

---

## Arquitectura general

```
Consulta del usuario
        │
        ▼
    ReActAgent
        │
        ├─► get_active_alerts       ── listado rápido (sin LLM)
        ├─► alert_analysis          ── diagnóstico completo (con LLM)
        ├─► get_alert_detail        ── detalle por IP (sin LLM)
        ├─► get_historical_tickets  ── historial de tickets (sin LLM)
        ├─► get_escalation_matrix   ── escalamiento + contactos (sin LLM)
        ├─► get_inventory_by_ip     ── inventario (sin LLM)
        ├─► get_template_by_id      ── ficha de aplicación (sin LLM)
        └─► get_contacto_gerencia   ── correo/ext de área (sin LLM)
                │
                ▼
        AlertRepository
                │
         ┌──────┴──────┐
         ▼             ▼
     BAZ_CDMX   →   EKT (fallback)
     Monitoreos      OPENDATASOURCE
     ABCMASplus       ABCMASplus_EKT
```

---

## Modelos del dominio (`src/domain/alerts/alert_entity.py`)

### AlertEvent
Evento activo de PRTG (una fila de `PrtgObtenerEventosEnriquecidos`).

| Campo | Alias BD | Tipo | Descripción |
|---|---|---|---|
| `equipo` | `Equipo` | str | Nombre del equipo |
| `ip` | `IP` | str | Dirección IP |
| `sensor` | `Sensor` | str | Nombre del sensor que generó la alerta |
| `status` | `Status` | str | Estado: `down`, `warning`, etc. |
| `mensaje` | `Mensaje` | str | Mensaje de la alerta PRTG |
| `prioridad` | `Prioridad` | int | 0-5, mayor es más crítico |
| `id_area_atendedora` | `idAreaAtendedora` | int? | ID de gerencia atendedora |
| `id_area_administradora` | `idAreaAdministradora` | int? | ID de gerencia administradora |
| `area_atendedora` | `AreaAtendedora` | str | Nombre del área atendedora |
| `responsable_atendedor` | `ResponsableAtendedor` | str | Nombre del responsable |
| `area_administradora` | `AreaAdministradora` | str | Nombre del área administradora |
| `responsable_administrador` | `ResponsableAdministrador` | str | Nombre del responsable |
| `origen` | `_origen` | str | `"BAZ_CDMX"` o `"EKT"` (campo interno) |

**Propiedades calculadas:**
- `es_ekt` → `True` si el evento viene de la instancia EKT/COMERCIO
- `es_url_sensor` → `True` si el sensor es una URL (empieza con `http`)

---

### HistoricalTicket
Ticket histórico de un incidente similar al activo.

| Campo | Alias BD | Tipo | Descripción |
|---|---|---|---|
| `ticket` | `Ticket` | str? | ID del ticket (llega como int, se convierte a str) |
| `alerta` | `alerta` | str | Descripción de la alerta del ticket |
| `detalle` | `detalle` | str | Detalle técnico del incidente |
| `accion_correctiva` | `accionCorrectiva` | str | Acción correctiva aplicada (cruda) |

**Propiedad calculada:**
- `accion_formateada` → reemplaza `[Salto]` de la BD por saltos de línea reales `\n`

---

### Template
Template de la aplicación asociada al equipo.

| Campo | Alias BD | Tipo | Descripción |
|---|---|---|---|
| `id_template` | `idTemplate` | int? | ID del template |
| `aplicacion` | `Aplicacion` | str | Nombre de la aplicación |
| `gerencia_desarrollo` | `GerenciaDesarrollo` | str | Gerencia dueña del desarrollo |
| `instancia` | — | str | `"BAZ"`, `"COMERCIO"` o vacío |
| `atendedor_id_gerencia` | `Atendedor_idGerencia` | int? | ID de la gerencia atendedora en el template |
| `gerencia_atendedora` | `GerenciaAtendedora` | str | Nombre de la gerencia atendedora |
| `ambiente` | `ambiente` | str | Ambiente: producción, QA, etc. |
| `negocio` | `Negocio` | str | Línea de negocio |
| `tipo_template` | `TipoTemplate` | str | Tipo de template |
| `es_aws` | `esAws` | bool | Si el equipo está en AWS |
| `es_vertical` | `esVertical` | bool | Si es una aplicación vertical |

**Propiedades calculadas:**
- `etiqueta` → `"ABCEKT"` si `instancia == "COMERCIO"`, sino `"ABCMASplus"`
- `es_ekt` → `True` si `instancia == "COMERCIO"`

---

### EscalationLevel
Un nivel de la matriz de escalamiento del template.

| Campo | Alias BD | Tipo | Descripción |
|---|---|---|---|
| `nivel` | `nivel` | int | Número de nivel (1 = primer escalamiento) |
| `nombre` | `Nombre` | str | Nombre del contacto |
| `puesto` | `puesto` | str | Puesto dentro de la empresa |
| `extension` | `Extension` | str | Extensión telefónica |
| `celular` | `celular` | str | Número de celular |
| `correo` | `correo` | str | Correo electrónico |
| `tiempo_escalacion` | `TiempoEscalacion` | str | Minutos antes de escalar (llega como int, se convierte) |

---

### AreaContacto
Datos de contacto de una gerencia.

| Campo | Alias BD | Tipo | Descripción |
|---|---|---|---|
| `gerencia` | `Gerencia` | str | Nombre de la gerencia |
| `correos` | `direccion_correo` | str | Correo(s) del área |
| `extensiones` | `extensiones` | str | Extensiones telefónicas |
| `responsable` | `RESPONSABLE` | str | Nombre del responsable del área |

---

### InventoryItem
Equipo del inventario (unifica `EquiposFisicos` y `MaquinasVirtuales`).

| Campo | Tipo | Descripción |
|---|---|---|
| `ip` | str | IP del equipo |
| `hostname` | str | Nombre del host |
| `id_area_atendedora` | int? | ID del área atendedora (para `get_contacto_gerencia`) |
| `id_area_administradora` | int? | ID del área administradora |
| `area_atendedora` | str | Nombre del área atendedora |
| `area_administradora` | str | Nombre del área administradora |
| `fuente` | str | `"Fisico"` o `"Virtual"` |
| `tipo_equipo` | str | Tipo de equipo físico (solo para físicos) |
| `version_os` | str | Sistema operativo |
| `status` | str | Estado del equipo en inventario |
| `capa` | str | Capa de infraestructura |
| `ambiente` | str | Producción, QA, desarrollo, etc. |
| `impacto` | str | Impacto del equipo (Alto / Medio / Bajo) |
| `urgencia` | str | Urgencia de atención |
| `prioridad` | str | Prioridad combinada |
| `negocio` | str | Línea de negocio (solo físicos) |

---

### AlertContext
Agregado completo que se pasa al `AlertPromptBuilder`.

```python
class AlertContext(BaseModel):
    evento: AlertEvent
    tickets: list[HistoricalTicket] = []
    template: Optional[Template] = None
    matriz: list[EscalationLevel] = []
    contacto_atendedora: Optional[AreaContacto] = None
    contacto_administradora: Optional[AreaContacto] = None
    query_usuario: str = ""
```

---

## AlertRepository (`src/domain/alerts/alert_repository.py`)

Única capa de acceso a datos para todo el dominio de alertas.
Nunca lanza excepciones al llamador — retorna `[]` o `None` en caso de error.

### Estrategia de fallback BAZ_CDMX → EKT

```
_run_sp_with_fallback(sp_baz, sp_ekt, params)
    └─► Ejecuta sp_baz
            ├─► Si retorna filas → devuelve (filas, "BAZ_CDMX")
            └─► Si vacío o excepción → ejecuta sp_ekt
                    ├─► Si retorna filas → devuelve (filas, "EKT")
                    └─► Si vacío → devuelve ([], "BAZ_CDMX")

_run_sps_with_fallback(sps_baz[], sps_ekt[])
    └─► Ejecuta todos los SPs de sps_baz y combina resultados
            ├─► Si hay filas → devuelve (filas_combinadas, "BAZ_CDMX")
            └─► Si vacío → ejecuta todos los SPs de sps_ekt
                    ├─► Si hay filas → devuelve (filas_combinadas, "EKT")
                    └─► Si todos fallaron con excepción → lanza ConnectionError
```

Los SPs con sufijo `_EKT` usan `OPENDATASOURCE` internamente para conectar
a la instancia EKT (`10.81.48.139,1533`).

### Métodos públicos

| Método | Retorna | SPs involucrados |
|---|---|---|
| `get_active_events(ip, equipo, solo_down)` | `list[AlertEvent]` | `PrtgObtenerEventosEnriquecidos` + `...Performance` (× 2 instancias) |
| `get_historical_tickets(ip, sensor)` | `list[HistoricalTicket]` | `IABOT_ObtenerTicketsByAlerta` |
| `get_last_historical_event(ip)` | `HistoricalAlertEvent?` | `EventosPRTG_Historico` (SELECT directo) |
| `get_recent_sensors_by_ip(ip, limit)` | `list[dict]` | `EventosPRTG_Historico` (SELECT GROUP BY) |
| `get_template_id(ip, url)` | `dict?` | `IDTemplateByIp` / `IDTemplateByUrl` |
| `get_template_info(template_id)` | `Template?` | `Template_GetById` |
| `get_template_by_id(template_id)` | `Template?` | `Template_GetById` |
| `get_escalation_matrix(template_id)` | `list[EscalationLevel]` | `ObtenerMatriz` |
| `get_contacto_gerencia(id_gerencia)` | `AreaContacto?` | `Contacto_GetByIdGerencia` |
| `get_inventory_by_ip(ip)` | `InventoryItem?` | `EquiposFisicos_GetByIp` → `MaquinasVirtuales_GetByIp` → `..._Ekt` (× 4) |

**Detalle de `get_historical_tickets`** — Lógica de resolución de sensor:
```
1. Intenta con sensor exacto recibido
2. Si no hay tickets → consulta EventosPRTG_Historico para obtener
   los últimos 5 sensores distintos del equipo
3. Prueba cada sensor histórico hasta encontrar tickets
4. Si ninguno tiene tickets → retorna []
```

**Detalle de `get_inventory_by_ip`** — Orden de búsqueda:
```
1. EquiposFisicos_GetByIp      (BAZ, equipos físicos)
2. MaquinasVirtuales_GetByIp   (BAZ, VMs)
3. EquiposFisicos_GetByIp_Ekt  (EKT, equipos físicos)
4. MaquinasVirtuales_GetByIp_Ekt (EKT, VMs)
```
Retorna el primer resultado encontrado. Las columnas se normalizan
a `InventoryItem` porque `EquiposFisicos` y `MaquinasVirtuales` usan
nombres distintos (`AreaAtiende` vs `AreaAtendedora`, etc.).

---

## Las 8 tools de alertas

### 1. `get_active_alerts`

**Clase**: `GetActiveAlertsTool` | **Archivo**: `get_active_alerts_tool.py`

Lista alertas activas con filtros opcionales. Sin LLM interno — el agente formatea.

**Parámetros:**

| Parámetro | Tipo | Requerido | Default | Descripción |
|---|---|---|---|---|
| `ip` | string | No | `None` | IP exacta del equipo |
| `equipo` | string | No | `None` | Nombre parcial (case-insensitive) |
| `solo_down` | boolean | No | `false` | Solo equipos con status `down` |

**Flujo:**
```
execute()
  └─► AlertRepository.get_active_events(ip, equipo, solo_down)
          └─► Formatea cada AlertEvent como texto línea a línea
                  └─► ToolResult.success_result(data=texto)
```

**Retorna:** Texto con cada alerta numerada. Ejemplo:
```
3 alerta(s) activa(s):

[1] equipo: SWITCH-CORE | ip: 10.1.2.3 | sensor: Ping
    status: down | prioridad: 5
    mensaje: No se puede contactar el equipo
    área atendedora: Redes
    responsable atendedor: Juan Pérez
```

**Manejo de errores:** Si `get_active_events` lanza `ConnectionError`,
retorna `ToolResult.error_result` con mensaje descriptivo sobre la instancia.

---

### 2. `alert_analysis`

**Clase**: `AlertAnalysisTool` | **Archivo**: `alert_analysis_tool.py`

La única tool del grupo que invoca un LLM interno (`data_llm`).
Genera un diagnóstico estructurado en Markdown con acciones recomendadas.

**Parámetros:**

| Parámetro | Tipo | Requerido | Default | Descripción |
|---|---|---|---|---|
| `query` | string | Sí | — | Consulta del operador |
| `ip` | string | No | `None` | Filtrar por IP exacta |
| `equipo` | string | No | `None` | Filtrar por nombre parcial |
| `solo_down` | boolean | No | `false` | Solo equipos con status `down` |

**Flujo completo:**
```
execute(query, ip, equipo, solo_down)
  │
  ├─► 1. get_active_events(ip, equipo, solo_down)
  │         └─► Si ConnectionError → ToolResult.error_result
  │         └─► Si vacío → ToolResult.success_result("No se encontraron alertas...")
  │
  ├─► 2. Tomar evento = events[0] (mayor prioridad)
  │
  ├─► 3. En paralelo (asyncio.gather):
  │         ├─► get_historical_tickets(ip=evento.ip, sensor=evento.sensor)
  │         └─► get_template_id(ip=evento.ip, url=sensor si es_url_sensor)
  │
  ├─► 4. Si hay template_id (en paralelo):
  │         ├─► get_template_info(tid, usar_ekt)
  │         └─► get_escalation_matrix(tid, usar_ekt)
  │
  ├─► 5. En paralelo (asyncio.gather):
  │         ├─► get_contacto_gerencia(id_area_atendedora, usar_ekt)
  │         └─► get_contacto_gerencia(id_area_administradora, usar_ekt)
  │
  ├─► 6. AlertContext(evento, tickets[:15], template, matriz, contactos, query)
  │
  ├─► 7. AlertPromptBuilder.build(context)
  │         └─► Construye (system_prompt, user_prompt) con 4 secciones:
  │               - ALERTA ACTIVA (equipo, sensor, estado, áreas, contactos)
  │               - TICKETS HISTÓRICOS (top 15, con acción correctiva)
  │               - TEMPLATE Y ESCALAMIENTO (aplicación, niveles, tiempos)
  │               - INSTRUCCIÓN (qué generar, formato Markdown esperado)
  │
  └─► 8. data_llm.generate_messages(messages, max_tokens=2048)
            └─► ToolResult.success_result(data=análisis_markdown)
```

**Retorna:** Análisis en Markdown con:
- Equipo y sensor afectado
- Área responsable y contactos
- Matriz de escalamiento
- Posible causa raíz
- Acciones recomendadas
- `DISCLAIMER` al final (⚠️ Las sugerencias son orientativas...)

---

### 3. `get_alert_detail`

**Clase**: `GetAlertDetailTool` | **Archivo**: `get_alert_detail_tool.py`

Contexto completo de un equipo por IP. Combina alerta activa, tickets históricos,
template, escalamiento y contactos **en paralelo**. Sin LLM.

**Parámetros:**

| Parámetro | Tipo | Requerido | Default | Descripción |
|---|---|---|---|---|
| `ip` | string | Sí | — | IP del equipo |
| `sensor` | string | No | `""` | Sensor para filtrar tickets |

**Flujo:**
```
execute(ip, sensor)
  │
  ├─► get_active_events(ip=ip)
  │     ├─► Si hay evento → evento = events[0]
  │     └─► Si no hay → get_last_historical_event(ip)
  │               └─► Si tampoco → ToolResult.success_result("No encontrado")
  │
  ├─► sensor_key = sensor || evento.sensor || evento_historico.sensor
  │
  ├─► En paralelo:
  │     ├─► get_historical_tickets(ip, sensor_key)
  │     └─► get_template_id(ip)
  │
  ├─► Si hay template_id, en paralelo:
  │     ├─► get_template_info(tid, usar_ekt)
  │     └─► get_escalation_matrix(tid, usar_ekt)
  │
  ├─► Si hay evento (no histórico), en paralelo:
  │     ├─► get_contacto_gerencia(id_area_atendedora)
  │     └─► get_contacto_gerencia(id_area_administradora)
  │
  └─► ToolResult.success_result(data=dict con todo)
```

**Retorna:** `dict` estructurado con campos:
```python
{
  "ip": str,
  "alerta_activa": bool,
  "evento": { equipo, ip, sensor, status, prioridad, mensaje, areas... },
  "tickets": [ { ticket, alerta, detalle, accion_correctiva } × 15 ],
  "total_tickets": int,
  "template": { aplicacion, gerencia_desarrollo } | None,
  "escalamiento": [ { nivel, nombre, puesto, extension, celular, correo, tiempo } ],
  "contacto_atendedora": { gerencia, responsable, correos, extensiones } | None,
  "contacto_administradora": { gerencia, responsable, correos, extensiones } | None,
}
```

---

### 4. `get_historical_tickets`

**Clase**: `GetHistoricalTicketsTool` | **Archivo**: `get_historical_tickets_tool.py`

Tickets históricos de un equipo con resolución automática de sensor.

**Parámetros:**

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `ip` | string | Sí | IP del equipo |
| `sensor` | string | No | Sensor específico para filtrar |

**Flujo de resolución de sensor (cuando no se pasa):**
```
1. get_active_events(ip) → toma sensor del evento activo
2. Si no hay activo → get_last_historical_event(ip) → toma sensor del histórico
3. Con el sensor resuelto → get_historical_tickets(ip, sensor)
```

**Retorna:** Texto formateado. Ejemplo:
```
3 ticket(s) histórico(s) para 10.53.34.130 (sensor: Memoria):

#12345 — Memoria: 18 % (Percent Available Memory) is below the error limit
  Detalle: Múltiples procesos Java consumiendo memoria
  Acción correctiva: Se reiniciaron servicios tomcat
  Verificar con: systemctl status tomcat

#12288 — ...
```

---

### 5. `get_escalation_matrix`

**Clase**: `GetEscalationMatrixTool` | **Archivo**: `get_escalation_matrix_tool.py`

Matriz de escalamiento completa + contactos de las áreas responsables.
Los datos de área vienen del **inventario** (fuente de verdad), no del evento.

**Parámetros:**

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `ip` | string | Sí | IP del equipo |

**Flujo:**
```
execute(ip)
  │
  ├─► En paralelo:
  │     ├─► get_template_id(ip)      ← para saber qué template usar
  │     └─► get_inventory_by_ip(ip)  ← fuente de verdad para áreas
  │
  ├─► Si no hay template_id → ToolResult con mensaje "Sin template"
  │
  ├─► En paralelo:
  │     ├─► get_template_info(tid, usar_ekt)
  │     └─► get_escalation_matrix(tid, usar_ekt)
  │
  ├─► IDs de área desde inventario (no desde evento activo):
  │     id_atendedora = inventario.id_area_atendedora
  │     id_administradora = inventario.id_area_administradora
  │
  ├─► En paralelo:
  │     ├─► get_contacto_gerencia(id_atendedora)
  │     └─► get_contacto_gerencia(id_administradora)
  │
  └─► ToolResult.success_result(data=dict)
```

**¿Por qué el inventario es fuente de verdad?**
El evento activo de PRTG puede traer áreas en blanco si el enriquecimiento
del SP falló. El inventario siempre tiene los IDs correctos de área.

**Retorna:** `dict` con:
```python
{
  "encabezado": "📌 #15037 MiApp | ABCMASplus",  # mostrar tal cual
  "gerencia_desarrollo": str | None,
  "area_atendedora":    { gerencia, responsable, correos, extensiones } | None,
  "area_administradora": { gerencia, responsable, correos, extensiones } | None,
  "niveles": [
    { nivel, nombre, puesto, extension, celular, correo, tiempo_escalacion }
  ]
}
```

---

### 6. `get_inventory_by_ip`

**Clase**: `GetInventoryByIpTool` | **Archivo**: `get_inventory_by_ip_tool.py`

Ficha del equipo en el inventario. Busca en 4 tablas en orden hasta encontrar.

**Parámetros:**

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `ip` | string | Sí | IP del equipo |

**Flujo:**
```
execute(ip)
  └─► AlertRepository.get_inventory_by_ip(ip)
        ├─► EquiposFisicos_GetByIp     (BAZ) → si hay → retorna, fuente="Fisico"
        ├─► MaquinasVirtuales_GetByIp  (BAZ) → si hay → retorna, fuente="Virtual"
        ├─► EquiposFisicos_GetByIp_Ekt (EKT) → si hay → retorna, fuente="Fisico"
        └─► MaquinasVirtuales_GetByIp_Ekt (EKT) → si hay → retorna, fuente="Virtual"
```

**Normalización de columnas:**
Las tablas `EquiposFisicos` y `MaquinasVirtuales` usan nombres distintos
(`AreaAtiende` vs `AreaAtendedora`, `IdAreaAtiende` vs `idAreaAtendedora`, etc.).
El repositorio los normaliza al modelo unificado `InventoryItem`.

**Retorna:** `dict` con todos los campos de `InventoryItem`
(hostname, áreas, fuente, OS, ambiente, impacto, urgencia, prioridad, negocio).

---

### 7. `get_template_by_id`

**Clase**: `GetTemplateByIdTool` | **Archivo**: `get_template_by_id_tool.py`

Ficha completa de un template dado su ID numérico.

**Parámetros:**

| Parámetro | Tipo | Requerido | Default | Descripción |
|---|---|---|---|---|
| `template_id` | integer | Sí | — | ID del template |
| `usar_ekt` | boolean | No | `false` | Consultar instancia COMERCIO primero |

**Flujo:**
```
execute(template_id, usar_ekt)
  └─► AlertRepository.get_template_by_id(template_id, usar_ekt)
        ├─► Si usar_ekt=False → Template_GetById (BAZ) → fallback _EKT
        └─► Si usar_ekt=True  → Template_GetById_EKT (EKT) → fallback BAZ
```

**Retorna:** `dict` con campos del template:
`aplicacion`, `gerencia_atendedora`, `id_gerencia_atendedora`,
`gerencia_desarrollo`, `id_gerencia_desarrollo`, `ambiente`,
`negocio`, `tipo_template`, `es_aws`, `es_vertical`.

---

### 8. `get_contacto_gerencia`

**Clase**: `GetContactoGerenciaTool` | **Archivo**: `get_contacto_gerencia_tool.py`

Correo electrónico y extensiones de una gerencia dado su ID.
Útil cuando ya se tiene el `idAreaAtendedora` de un evento o inventario.

**Parámetros:**

| Parámetro | Tipo | Requerido | Default | Descripción |
|---|---|---|---|---|
| `id_gerencia` | integer | Sí | — | ID numérico de la gerencia |
| `usar_ekt` | boolean | No | `false` | Consultar instancia EKT |

**Flujo:**
```
execute(id_gerencia, usar_ekt)
  └─► AlertRepository.get_contacto_gerencia(id_gerencia, usar_ekt)
        ├─► Si usar_ekt=False → Contacto_GetByIdGerencia
        └─► Si usar_ekt=True  → Contacto_GetByIdGerencia_EKT
```

**Retorna:** `dict` con `id_gerencia`, `gerencia`, `responsable`, `correos`, `extensiones`.

---

## AlertPromptBuilder (`src/domain/alerts/alert_prompt_builder.py`)

Construye el prompt enriquecido que recibe el LLM en `alert_analysis`.
Recibe un `AlertContext` y produce `(system_prompt, user_prompt)`.

### Estructura del user_prompt (4 secciones)

```
## ALERTA ACTIVA
- Equipo, IP, Sensor, Status, Detalle, Prioridad
- Área atendedora, Responsable atendedor
- Área administradora, Responsable administrador
- Contacto atendedora: correo | ext
- Contacto administradora: correo | ext

## TICKETS HISTÓRICOS (últimos similares)
Para cada ticket:
  Ticket: #ID
  Alerta: descripción
  Detalle: detalle técnico
  Acción correctiva: pasos (con saltos de línea reales)
  ---

## TEMPLATE Y ESCALAMIENTO
- Aplicación: nombre (#id) [ABCMASplus|ABCEKT]
- Gerencia de desarrollo
- Matriz de escalamiento:
    Nivel N: Nombre (Puesto) | Ext: X | Cel: X | Email: X | ⏱ N min

## INSTRUCCIÓN
[La instrucción le indica al LLM el formato Markdown exacto
 que debe generar: encabezado con template, áreas responsables,
 escalamiento, causa raíz y acciones recomendadas]
```

### System prompt
```
Eres un asistente experto en operaciones de TI y monitoreo de infraestructura.
Analizas alertas activas de PRTG y generas diagnósticos estructurados en Markdown
para Telegram. Usa los datos exactos del contexto — no inventes información.
```

### DISCLAIMER
Añadido al final de todo análisis generado:
```
⚠️ Las sugerencias anteriores son orientativas.
La decisión de ejecutar cualquier acción es responsabilidad exclusiva del operador.
Valide siempre el impacto antes de actuar.
```

---

## Configuración requerida

Las tools de alertas requieren la conexión `monitoreo` en `DB_CONNECTIONS`.
Si no está configurada, las tools no se instancian (el factory las omite).

```env
# .env
DB_CONNECTIONS={"monitoreo": "mssql+pyodbc://user:pass@server/Monitoreos?driver=..."}
```

Verificación en `factory.py`:
```python
if db_registry is not None and db_registry.is_configured("monitoreo"):
    # Instanciar tools de alertas
```

---

**← Anterior** [Tools](tools.md) · [Índice](README.md)
