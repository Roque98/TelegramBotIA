[Docs](../index.md) › [Uso](README.md) › Qué puede hacer el bot

# Qué puede hacer el bot

Iris es el nombre del asistente. Opera principalmente a través de Telegram y responde preguntas
sobre los sistemas internos de la empresa.

---

## Capacidades

### Consultas a la base de datos

Iris puede responder preguntas sobre datos de negocio haciendo consultas SQL de forma transparente
al usuario. El usuario escribe en español; Iris genera y ejecuta el SQL internamente.

Ejemplos de consultas que puede responder:

- "¿Cuántas ventas hubo ayer?"
- "Dame el total facturado por sucursal este mes"
- "¿Cuál es el stock actual del producto X?"
- "Mostrá los 5 empleados con más horas registradas esta semana"
- "¿Cuántos pedidos están pendientes de despacho?"

**Restricciones**: Solo puede ejecutar `SELECT`. No puede insertar, modificar ni eliminar datos.
Las consultas pasan por un validador que rechaza cualquier operación que no sea de lectura.

---

### Base de conocimiento empresarial

Iris puede buscar en una base de conocimiento estructurada con artículos sobre políticas,
procedimientos, contactos y preguntas frecuentes.

Ejemplos:

- "¿Cuál es la política de devoluciones?"
- "¿Cómo solicito vacaciones?"
- "¿A quién llamo para soporte de sistemas?"
- "¿Cuáles son los pasos para dar de alta a un proveedor?"

Las categorías disponibles dependen de los permisos del usuario:
`PROCESOS`, `POLITICAS`, `FAQS`, `CONTACTOS`, `RECURSOS_HUMANOS`, `SISTEMAS`, `BASE_DATOS`.

---

### Cálculos matemáticos

Iris puede resolver cálculos sin inventar resultados:

- "¿Cuánto es el 15% de 8.450?"
- "Si tengo 120 unidades a $350 cada una, ¿cuál es el total con IVA del 21%?"
- "Calculá la diferencia entre 1.847 y 923"

---

### Fecha y hora

- "¿Qué fecha es hoy?"
- "¿Qué día de la semana cae el 25 de mayo?"

---

### Preferencias del usuario

El usuario puede pedirle a Iris que lo recuerde de cierta manera:

- "Llamame Ángel"
- "Prefiero respuestas cortas"
- "Respondeme en inglés"

Estas preferencias se guardan en la base de datos y persisten entre sesiones.

---

### Memoria entre sesiones

Iris puede guardar hechos relevantes del usuario:

- "Recordá que trabajo en el área de ventas del sur"
- "Mi número de legajo es 4521"

---

## Limitaciones

| Limitación | Detalle |
|------------|---------|
| No puede modificar datos | Solo ejecuta SELECT, nunca INSERT/UPDATE/DELETE |
| No tiene internet | No puede buscar en Google ni acceder a URLs externas |
| No procesa imágenes | No interpreta fotos (solo texto y archivos adjuntos de texto) |
| Sin memoria ilimitada | El contexto de conversación cubre las últimas interacciones |
| Permisos por usuario | Cada usuario ve solo los datos y funciones que su rol permite |

---

## Qué no puede hacer

- Enviar correos o notificaciones en nombre del usuario
- Modificar registros en ninguna tabla
- Ejecutar procesos o scripts del sistema
- Acceder a sistemas externos a la empresa
- Responder con datos que no estén en la BD o la base de conocimiento
  (si no sabe algo, lo dice explícitamente)

---

[Índice](README.md) · **Siguiente →** [Guía de usuario Telegram](guia-usuario-telegram.md)
