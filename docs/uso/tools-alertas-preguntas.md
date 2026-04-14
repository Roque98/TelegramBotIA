# Tools de Alertas — Referencia y Preguntas de Prueba

Guía para operadores y desarrolladores que quieran probar o afinar las respuestas
del bot en el flujo de monitoreo PRTG.

---

## Mapa de Tools

| Tool | Cuándo la usa el agente | Requiere IP |
|---|---|---|
| `get_active_alerts` | Hay alertas activas / resumen general | No |
| `alert_analysis` | Análisis profundo con diagnóstico LLM | No (opcional) |
| `get_alert_detail` | Detalle completo de un equipo específico | Sí |
| `get_historical_tickets` | Historial de tickets de un equipo | Sí |
| `get_escalation_matrix` | Matriz de escalamiento + contactos de área | Sí |
| `get_inventory_by_ip` | Datos de inventario (área, OS, ambiente) | Sí |
| `get_template_by_id` | Ficha de aplicación por ID de template | Sí (template_id) |
| `get_contacto_gerencia` | Correo/ext de un área por ID numérico | Sí (id_gerencia) |

---

## Detalle de cada tool

### `get_active_alerts`
Lista todas las alertas activas de PRTG con filtros opcionales.
Retorna: equipo, IP, sensor, status, prioridad, área atendedora/administradora y responsables.

**Filtros disponibles:**
- `ip` — IP exacta del equipo
- `equipo` — nombre parcial del equipo
- `solo_down` — solo equipos con status "down"

---

### `alert_analysis`
Análisis completo con LLM: toma la alerta más crítica, la enriquece con
tickets históricos, template y matriz de escalamiento, y genera un diagnóstico
en Markdown con acciones recomendadas y posible causa raíz.

**Filtros disponibles:** los mismos que `get_active_alerts`.

---

### `get_alert_detail`
Contexto completo de un equipo por IP: estado actual del sensor, tickets
históricos (últimos 15), template de aplicación, matriz de escalamiento y
contactos de las áreas responsables. Todo obtenido en paralelo.

**Parámetros:**
- `ip` — requerido
- `sensor` — opcional, para filtrar tickets por sensor específico

---

### `get_historical_tickets`
Tickets previos de un equipo: ID, descripción de la alerta, detalle y
acción correctiva registrada. Si no se pasa sensor, lo resuelve automáticamente
desde la alerta activa o el último evento histórico.

**Parámetros:**
- `ip` — requerido
- `sensor` — opcional

---

### `get_escalation_matrix`
Matriz de escalamiento con todos los niveles: nombre, puesto, extensión,
celular, correo y tiempo de respuesta. También incluye datos de contacto
de las áreas atendedora y administradora desde el inventario.

**Parámetros:**
- `ip` — requerido

---

### `get_inventory_by_ip`
Ficha del equipo en el inventario: hostname, área atendedora, área
administradora, tipo (Físico/Virtual), OS, ambiente, capa, impacto, urgencia,
prioridad y negocio. Busca en instancias BAZ y EKT.

**Parámetros:**
- `ip` — requerido

---

### `get_template_by_id`
Ficha de aplicación por ID de template: nombre, gerencia atendedora,
gerencia de desarrollo, ambiente, negocio y tipo.

**Parámetros:**
- `template_id` — requerido (entero)
- `usar_ekt` — opcional, para instancia COMERCIO/EKT

---

### `get_contacto_gerencia`
Correo electrónico y extensiones telefónicas de una gerencia dado su ID
numérico. Útil cuando ya se tiene el ID de área desde un evento o inventario.

**Parámetros:**
- `id_gerencia` — requerido (entero)
- `usar_ekt` — opcional

---

## Preguntas para pulir resultados

Las preguntas están agrupadas por lo que quieres probar o afinar.

### Resumen general de alertas

```
¿Hay alertas activas ahora mismo?
¿Cuántos equipos están en alerta?
Dame un resumen de las alertas activas
¿Qué equipos tienen problemas en este momento?
Muéstrame solo los equipos que están caídos (down)
¿Hay equipos DOWN en este momento?
```

### Filtrar por equipo o IP

```
¿Hay alertas para el equipo SWITCH-CORE?
¿Qué alertas tiene el equipo FIREWALL?
¿Está en alerta la IP 10.53.34.130?
¿Qué está pasando con el equipo 10.118.57.142?
```

### Análisis profundo de una alerta

```
Analiza la alerta más crítica que tengas
Dame un diagnóstico del equipo con más prioridad
Analiza el equipo 10.53.34.130 y dime qué hacer
¿Qué está fallando en 10.118.57.142 y cuál es la causa raíz?
Analiza el sensor de memoria del equipo 10.118.57.142
```

### Historial de tickets

```
¿Qué tickets históricos tiene el equipo 10.53.34.130?
¿Cuántas veces ha fallado este equipo antes? IP: 10.118.57.142
¿Cuál fue la acción correctiva que se aplicó la última vez en 10.53.34.130?
Muéstrame el historial de incidentes de 10.118.57.142 en el sensor de CPU
```

### Escalamiento y contactos

```
¿A quién escalo si el equipo 10.53.34.130 sigue caído?
Dame la matriz de escalamiento de 10.118.57.142
¿Quién es el responsable de atender el equipo 10.53.34.130?
¿Cuáles son los contactos del área que administra la IP 10.118.57.142?
¿Quién atiende este equipo y cómo los contacto?
```

### Inventario del equipo

```
¿A qué área pertenece el equipo 10.80.133.56?
¿Qué sistema operativo tiene el equipo 10.118.57.142?
¿Es físico o virtual el equipo 10.53.34.130?
¿En qué ambiente está el equipo con IP 10.80.133.56? (producción, QA, etc.)
¿Cuál es el impacto y urgencia del equipo 10.118.57.142?
```

### Detalle completo (combina varias tools)

```
Dame todo lo que tengas sobre el equipo 10.53.34.130
Necesito el contexto completo de la alerta en 10.118.57.142
¿Qué alerta tiene, quién la atiende, cuál es el historial y a quién escalo para 10.53.34.130?
```

### Preguntas que refinan el formato de respuesta

```
Muéstrame las alertas en formato de tabla
Lista solo equipo e IP de las alertas activas, nada más
Dame solo el primer nivel de escalamiento para 10.53.34.130
¿Cuántos tickets tiene el equipo 10.118.57.142? Solo el número
Dime el correo del área atendedora de 10.53.34.130
```

### Casos borde y validación

```
¿Hay alertas para la IP 1.2.3.4?
Dame el historial del equipo 999.999.999.999
¿Qué alertas hay para el equipo INEXISTENTE?
```

---

## Flujo típico del agente (para entender qué tool se activa)

```
Pregunta general
    └─► get_active_alerts
            └─► Si hay alertas → alert_analysis (con la IP del más crítico)

"Analiza el equipo X.X.X.X"
    └─► alert_analysis (ip=X.X.X.X)
            └─► Internamente: get_active_events + get_historical_tickets +
                              get_template_id + get_escalation_matrix +
                              get_contacto_gerencia (paralelo)

"Detalle de X.X.X.X"
    └─► get_alert_detail (ip=X.X.X.X)

"¿A quién escalo X.X.X.X?"
    └─► get_escalation_matrix (ip=X.X.X.X)

"Historial de X.X.X.X"
    └─► get_historical_tickets (ip=X.X.X.X)

"¿A qué área pertenece X.X.X.X?"
    └─► get_inventory_by_ip (ip=X.X.X.X)
```

---

## Notas para refinar respuestas

- Si el agente da **demasiada información**, especifica: *"Solo dime equipo y status"*
- Si el agente no usa **el sensor correcto**, añade: *"sensor de CPU / sensor de Memoria / sensor Ping"*
- Si quieres **solo los caídos**: agrega *"equipos DOWN"* o *"solo los que están caídos"*
- Si la alerta pertenece a **COMERCIO/EKT**, el agente lo detecta automáticamente por la instancia
- Los tickets históricos se limitan a **15 más recientes** por defecto
