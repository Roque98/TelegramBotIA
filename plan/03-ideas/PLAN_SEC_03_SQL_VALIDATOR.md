# PLAN: SQL Validator robusto

> **Objetivo**: Fortalecer la validación de SQL generado por IA contra ataques e información sensible
> **Rama**: `feature/sec-03-sql-validator`
> **Prioridad**: 🔴 Crítica
> **Progreso**: 0% (0/6)

---

## Contexto

`src/database/sql_validator.py` valida el SQL que genera la IA antes de ejecutarlo. Vulnerabilidades actuales:

1. **Table enumeration permitida**: Un usuario malicioso puede preguntar "¿qué tablas existen?" y la IA generaría `SELECT table_name FROM information_schema.tables` — esto pasa la validación actual
2. **ReDoS posible**: El regex `r'\b' + keyword + r'\b'` sobre queries muy largas puede ser explotado para hacer lenta la validación
3. **Comentarios SQL no filtrados**: `SELECT /*! MAX(id) */ FROM users` puede evadir keywords por estar dentro de comentarios

---

## Archivos involucrados

- `src/database/sql_validator.py` — refactorizar validación
- `tests/test_sql_validator.py` — agregar casos de ataque

---

## Tareas

- [ ] **3.1** Agregar pre-procesamiento: eliminar comentarios SQL (`-- ...`, `/* ... */`) antes de validar
- [ ] **3.2** Agregar lista negra de tablas/vistas del sistema:
  - `information_schema`, `sys`, `sysobjects`, `syscolumns`, `sysusers`
  - `master`, `msdb`, `model` (bases del sistema en SQL Server)
- [ ] **3.3** Reemplazar regex con `re.search(r'\b' + re.escape(keyword) + r'\b', query, re.IGNORECASE)` + timeout máximo de 100ms
- [ ] **3.4** Agregar lista de funciones peligrosas permitidas solo a admins: `EXEC`, `xp_cmdshell`, `OPENROWSET`
- [ ] **3.5** Agregar tests específicos de evasión:
  - SQL con comentarios
  - SQL con acceso a information_schema
  - SQL con UNION-based injection
- [ ] **3.6** Documentar en CLAUDE.md qué queries son permitidas y cuáles no

---

## Criterios de aceptación

- `SELECT table_name FROM information_schema.tables` es rechazado
- SQL con comentarios maliciosos es rechazado
- Los tests incluyen al menos 10 casos de ataque conocidos
- La validación completa tarda menos de 100ms para cualquier query
