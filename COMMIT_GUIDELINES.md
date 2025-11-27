# Guía de Commits para el Proyecto

Esta guía define las mejores prácticas para realizar commits en este repositorio.

## 📋 Tabla de Contenidos

- [Formato de Commits](#formato-de-commits)
- [Tipos de Commits](#tipos-de-commits)
- [Alcance (Scope)](#alcance-scope)
- [Ejemplos](#ejemplos)
- [Buenas Prácticas](#buenas-prácticas)
- [Flujo de Trabajo](#flujo-de-trabajo)

## 🎯 Formato de Commits

Usamos el formato **Conventional Commits** para mantener un historial limpio y semántico:

```
<tipo>(<alcance>): <descripción corta>

[Cuerpo opcional del mensaje]

[Nota al pie opcional]
```

### Estructura:

- **tipo**: Categoría del cambio (obligatorio)
- **alcance**: Área del código afectada (opcional)
- **descripción**: Resumen conciso en presente imperativo (obligatorio)
- **cuerpo**: Explicación detallada del cambio (opcional)
- **nota al pie**: Referencias a issues, breaking changes, etc. (opcional)

## 🏷️ Tipos de Commits

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| `feat` | Nueva funcionalidad | `feat(agent): agregar soporte para Claude AI` |
| `fix` | Corrección de bugs | `fix(db): corregir conexión a SQL Server` |
| `docs` | Cambios en documentación | `docs(readme): actualizar instrucciones de instalación` |
| `style` | Cambios de formato (no afectan la lógica) | `style(agent): aplicar formato PEP 8` |
| `refactor` | Refactorización de código | `refactor(llm): simplificar lógica de retry` |
| `perf` | Mejoras de rendimiento | `perf(query): optimizar consultas SQL` |
| `test` | Agregar o modificar tests | `test(agent): agregar tests para clasificador` |
| `build` | Cambios en build o dependencias | `build: actualizar pydantic a v2.10.2` |
| `ci` | Cambios en CI/CD | `ci: agregar GitHub Actions workflow` |
| `chore` | Tareas de mantenimiento | `chore: limpiar archivos temporales` |
| `revert` | Revertir un commit anterior | `revert: revertir feat(agent): agregar cache` |

## 📦 Alcance (Scope)

El alcance especifica qué parte del código se modificó. Ejemplos para este proyecto:

- `agent` - Agente LLM y clasificadores
- `bot` - Bot de Telegram
- `db` - Base de datos y queries
- `config` - Configuración y settings
- `auth` - Autenticación y permisos
- `sql` - Generación de SQL
- `prompts` - Templates de prompts
- `utils` - Utilidades y helpers

## 📝 Ejemplos

### Commit Simple
```bash
git commit -m "feat(bot): agregar comando /estadisticas"
```

### Commit con Cuerpo
```bash
git commit -m "fix(db): corregir timeout en consultas largas

El timeout de 15 segundos era insuficiente para consultas
complejas con múltiples JOINs. Se aumenta a 60 segundos.

Fixes #123"
```

### Commit con Breaking Change
```bash
git commit -m "feat(agent)!: cambiar estructura de respuestas

BREAKING CHANGE: La estructura de respuesta del agente ahora
incluye metadata adicional. Los clientes deben actualizar
su código para manejar el nuevo formato."
```

### Múltiples Cambios Relacionados
```bash
# Opción 1: Un commit con alcances múltiples
git commit -m "refactor(agent,prompts): mejorar sistema de templates"

# Opción 2: Commits separados (preferido)
git commit -m "refactor(agent): extraer lógica de templates"
git commit -m "refactor(prompts): reorganizar estructura de carpetas"
```

## ✅ Buenas Prácticas

### 1. Descripción Clara y Concisa
- ✅ `feat(bot): agregar persistencia de conversaciones`
- ❌ `fix: arreglar bug`
- ❌ `update files`

### 2. Usar Presente Imperativo
- ✅ `agregar`, `corregir`, `actualizar`
- ❌ `agregado`, `agregando`, `agregué`

### 3. No Capitalizar la Primera Letra
- ✅ `feat(db): agregar índices a tabla usuarios`
- ❌ `feat(db): Agregar índices a tabla usuarios`

### 4. No Usar Punto Final
- ✅ `docs: actualizar guía de instalación`
- ❌ `docs: actualizar guía de instalación.`

### 5. Máximo 50 Caracteres en la Descripción
- Mantén el título conciso
- Usa el cuerpo del mensaje para detalles

### 6. Commits Atómicos
Cada commit debe representar **un único cambio lógico**:
- ✅ Un commit por feature
- ✅ Un commit por bugfix
- ❌ Múltiples features en un commit
- ❌ Mezclar refactoring con nuevas features

### 7. No Commitear Archivos Sensibles
**NUNCA** commitear:
- ❌ `.env` (credenciales, API keys)
- ❌ `*.db`, `*.sqlite` (bases de datos locales)
- ❌ Tokens o contraseñas hardcodeados
- ✅ Usar `.env.example` como plantilla

## 🔄 Flujo de Trabajo

### 1. Verificar Estado
```bash
git status
```

### 2. Agregar Archivos
```bash
# Agregar archivos específicos (PREFERIDO)
git add src/agent/llm_agent.py
git add tests/test_agent.py

# O agregar todos los cambios (CON PRECAUCIÓN)
git add .
```

### 3. Verificar Cambios Staged
```bash
git diff --staged
```

### 4. Crear Commit
```bash
git commit -m "feat(agent): agregar retry con backoff exponencial"
```

### 5. Verificar Historial
```bash
git log --oneline
```

### 6. Push al Remoto
```bash
# Primera vez (configurar upstream)
git push -u origin master

# Siguientes veces
git push
```

## 🚨 Qué NO Hacer

### ❌ Commits Masivos
```bash
# MAL - Demasiado genérico
git commit -m "update code"
git add . && git commit -m "cambios varios"
```

### ❌ Mezclar Cambios No Relacionados
```bash
# MAL - Mezcla refactor con nueva feature
git commit -m "refactor(agent): mejorar código y agregar cache"

# BIEN - Separar en dos commits
git commit -m "refactor(agent): mejorar legibilidad del código"
git commit -m "feat(agent): agregar sistema de cache"
```

### ❌ Mensajes Poco Descriptivos
```bash
# MAL
git commit -m "fix bug"
git commit -m "update"
git commit -m "wip"  # Work In Progress

# BIEN
git commit -m "fix(sql): corregir escape de comillas en queries"
git commit -m "docs(readme): actualizar sección de configuración"
```

## 📚 Referencias

- [Conventional Commits](https://www.conventionalcommits.org/)
- [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/)
- [Angular Commit Guidelines](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit)

## 🔍 Verificar Commits Antes de Push

```bash
# Ver últimos 5 commits
git log -5 --oneline

# Ver cambios del último commit
git show HEAD

# Modificar último commit (SI NO SE HA HECHO PUSH)
git commit --amend -m "nuevo mensaje"

# NUNCA uses --amend después de hacer push a remote
```

## 📌 Ejemplo Completo de Sesión

```bash
# 1. Ver cambios
git status

# 2. Agregar archivos específicos
git add src/agent/llm_agent.py
git add src/agent/prompts/system_prompt.py

# 3. Verificar lo que se va a commitear
git diff --staged

# 4. Crear commit descriptivo
git commit -m "feat(agent): implementar retry con backoff exponencial

Se agrega lógica de reintentos para manejar errores de API.
- Backoff exponencial con jitter
- Máximo 3 reintentos
- Logs detallados de cada intento

Closes #45"

# 5. Verificar commit
git log -1

# 6. Push al remoto
git push
```

---

**Recuerda**: Un buen historial de commits facilita el code review, debugging, y la colaboración en equipo.
