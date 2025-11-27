# GitFlow - Estrategia de Branches

Esta guía define la estrategia de branches y flujo de trabajo para este proyecto basado en GitFlow.

## 📋 Tabla de Contenidos

- [Estructura de Branches](#estructura-de-branches)
- [Flujo de Trabajo](#flujo-de-trabajo)
- [Tipos de Ramas](#tipos-de-ramas)
- [Versionado Semántico](#versionado-semántico)
- [Comandos Útiles](#comandos-útiles)
- [Casos de Uso](#casos-de-uso)

## 🌳 Estructura de Branches

```
master (main)
  ├── v0.1.0-base (tag) ← Versión base/template
  ├── develop ← Desarrollo activo
  │   ├── feature/autenticacion-mejorada
  │   ├── feature/nuevos-reportes
  │   └── feature/integracion-whatsapp
  ├── release/v1.0.0 ← Preparación para producción
  └── hotfix/fix-sql-injection ← Correcciones urgentes
```

### Ramas Principales

| Rama | Propósito | Protección | Vida |
|------|-----------|------------|------|
| `master` | Código en producción | ✅ Protegida | Permanente |
| `develop` | Desarrollo activo | ✅ Protegida | Permanente |

### Ramas de Soporte

| Tipo | Prefijo | Base | Merge a | Vida |
|------|---------|------|---------|------|
| Feature | `feature/*` | `develop` | `develop` | Temporal |
| Release | `release/*` | `develop` | `master` + `develop` | Temporal |
| Hotfix | `hotfix/*` | `master` | `master` + `develop` | Temporal |

## 🔄 Flujo de Trabajo

### 1. Configuración Inicial (Ya realizado)

```bash
# Estado actual
master ← Versión base del proyecto
```

### 2. Crear Versión Base y Develop

```bash
# Crear tag de la versión base
git tag -a v0.1.0-base -m "Versión base del proyecto - Template inicial"
git push origin v0.1.0-base

# Crear rama develop desde master
git checkout -b develop
git push -u origin develop

# Volver a master
git checkout master
```

### 3. Trabajar en Nuevas Features

```bash
# Crear feature desde develop
git checkout develop
git pull origin develop
git checkout -b feature/nombre-descriptivo

# Trabajar en la feature
git add .
git commit -m "feat(scope): descripción del cambio"

# Actualizar con develop regularmente
git checkout develop
git pull origin develop
git checkout feature/nombre-descriptivo
git merge develop

# Cuando esté lista, merge a develop
git checkout develop
git pull origin develop
git merge --no-ff feature/nombre-descriptivo
git push origin develop

# Eliminar rama local
git branch -d feature/nombre-descriptivo
```

### 4. Preparar Release

```bash
# Crear rama release desde develop
git checkout develop
git pull origin develop
git checkout -b release/v1.0.0

# Actualizar versión, changelog, etc.
# Hacer últimos ajustes y testing

# Merge a master
git checkout master
git pull origin master
git merge --no-ff release/v1.0.0

# Crear tag
git tag -a v1.0.0 -m "Release v1.0.0 - Descripción"
git push origin master
git push origin v1.0.0

# Merge de vuelta a develop
git checkout develop
git merge --no-ff release/v1.0.0
git push origin develop

# Eliminar rama release
git branch -d release/v1.0.0
```

### 5. Hotfix Urgente

```bash
# Crear hotfix desde master
git checkout master
git pull origin master
git checkout -b hotfix/descripcion-bug

# Corregir el bug
git add .
git commit -m "fix(scope): corrección urgente de bug"

# Merge a master
git checkout master
git merge --no-ff hotfix/descripcion-bug
git tag -a v1.0.1 -m "Hotfix v1.0.1 - Corrección de bug"
git push origin master
git push origin v1.0.1

# Merge a develop
git checkout develop
git merge --no-ff hotfix/descripcion-bug
git push origin develop

# Eliminar rama hotfix
git branch -d hotfix/descripcion-bug
```

## 🏷️ Tipos de Ramas

### Feature Branches

**Propósito**: Desarrollo de nuevas funcionalidades

**Nomenclatura**: `feature/descripcion-corta`

**Ejemplos**:
- `feature/autenticacion-biometrica`
- `feature/exportar-excel`
- `feature/dashboard-estadisticas`
- `feature/integracion-slack`

**Ciclo de vida**:
1. Crear desde `develop`
2. Desarrollar la funcionalidad
3. Merge a `develop` cuando esté completa
4. Eliminar la rama

**Buenas prácticas**:
- ✅ Una feature por rama
- ✅ Merge frecuente desde develop para evitar conflictos
- ✅ Commits descriptivos siguiendo Conventional Commits
- ✅ Tests antes de hacer merge
- ❌ No hacer merge directo a master
- ❌ No mezclar múltiples features

### Release Branches

**Propósito**: Preparación para producción

**Nomenclatura**: `release/vX.Y.Z`

**Ejemplos**:
- `release/v1.0.0`
- `release/v1.1.0`
- `release/v2.0.0`

**Qué se hace aquí**:
- Actualizar número de versión
- Actualizar CHANGELOG.md
- Corrección de bugs menores
- Testing final
- Actualizar documentación

**Qué NO se hace**:
- ❌ Nuevas features
- ❌ Cambios grandes de código
- ❌ Refactorings mayores

### Hotfix Branches

**Propósito**: Correcciones urgentes en producción

**Nomenclatura**: `hotfix/descripcion-bug`

**Ejemplos**:
- `hotfix/sql-injection-fix`
- `hotfix/memory-leak`
- `hotfix/auth-bypass`

**Cuándo usar**:
- Bug crítico en producción
- Vulnerabilidad de seguridad
- Error que bloquea funcionalidad principal

**Proceso**:
1. Crear desde `master`
2. Corregir el bug
3. Merge a `master` y `develop`
4. Crear nuevo tag de versión

## 📦 Versionado Semántico

Usamos **Semantic Versioning** (SemVer): `MAJOR.MINOR.PATCH`

```
v1.2.3
│ │ │
│ │ └─ PATCH: Bug fixes, hotfixes
│ └─── MINOR: Nuevas features (compatible hacia atrás)
└───── MAJOR: Breaking changes (no compatible)
```

### Ejemplos

| Cambio | Versión Anterior | Versión Nueva | Tipo |
|--------|------------------|---------------|------|
| Corregir bug en autenticación | v1.2.3 | v1.2.4 | PATCH |
| Agregar exportación a PDF | v1.2.4 | v1.3.0 | MINOR |
| Cambiar estructura de API | v1.3.0 | v2.0.0 | MAJOR |
| Hotfix de seguridad | v1.3.0 | v1.3.1 | PATCH |

### Tags Especiales

- `v0.1.0-base`: Versión base/template del proyecto
- `v1.0.0-beta.1`: Versión beta
- `v1.0.0-rc.1`: Release candidate

## 💡 Comandos Útiles

### Ver Estado de Ramas

```bash
# Ver todas las ramas locales
git branch

# Ver todas las ramas (locales + remotas)
git branch -a

# Ver última commit de cada rama
git branch -v

# Ver ramas mergeadas a la actual
git branch --merged

# Ver ramas NO mergeadas a la actual
git branch --no-merged
```

### Ver Tags

```bash
# Listar todos los tags
git tag

# Ver detalles de un tag
git show v0.1.0-base

# Buscar tags por patrón
git tag -l "v1.*"
```

### Limpiar Ramas

```bash
# Eliminar rama local
git branch -d feature/mi-feature

# Forzar eliminación (si no está mergeada)
git branch -D feature/mi-feature

# Eliminar rama remota
git push origin --delete feature/mi-feature

# Limpiar referencias de ramas remotas eliminadas
git fetch --prune
```

### Sincronizar con Remoto

```bash
# Actualizar todas las ramas remotas
git fetch --all

# Ver diferencias con rama remota
git diff develop origin/develop

# Actualizar rama actual
git pull origin develop
```

## 📝 Casos de Uso

### Caso 1: Usar la Base para un Nuevo Proyecto

```bash
# Opción 1: Clonar y crear nueva rama desde tag base
git clone https://github.com/Roque98/TelegramBotIA.git nuevo-proyecto
cd nuevo-proyecto
git checkout v0.1.0-base
git checkout -b develop-nuevo-proyecto

# Opción 2: Fork del repositorio en GitHub
# 1. Fork en GitHub UI
# 2. Clonar tu fork
git clone https://github.com/tu-usuario/TelegramBotIA.git
cd TelegramBotIA
git checkout v0.1.0-base
git checkout -b develop
```

### Caso 2: Trabajar en Nueva Feature

```bash
# 1. Asegurarse de estar en develop actualizado
git checkout develop
git pull origin develop

# 2. Crear rama de feature
git checkout -b feature/sistema-notificaciones

# 3. Desarrollar (hacer commits siguiendo Conventional Commits)
git add src/notifications/
git commit -m "feat(notifications): agregar servicio de notificaciones email"

git add tests/test_notifications.py
git commit -m "test(notifications): agregar tests de notificaciones"

# 4. Sincronizar con develop regularmente
git checkout develop
git pull origin develop
git checkout feature/sistema-notificaciones
git merge develop

# 5. Cuando esté lista, merge a develop
git checkout develop
git merge --no-ff feature/sistema-notificaciones
git push origin develop

# 6. Limpiar
git branch -d feature/sistema-notificaciones
```

### Caso 3: Crear un Release

```bash
# 1. Crear rama release desde develop
git checkout develop
git pull origin develop
git checkout -b release/v1.0.0

# 2. Actualizar versión y documentación
# Editar archivos de versión, CHANGELOG.md, etc.
git commit -m "chore(release): preparar v1.0.0"

# 3. Testing final y bug fixes menores
git commit -m "fix(auth): corregir validación de tokens"

# 4. Merge a master
git checkout master
git pull origin master
git merge --no-ff release/v1.0.0
git tag -a v1.0.0 -m "Release v1.0.0

Nuevas características:
- Sistema de notificaciones
- Dashboard de estadísticas
- Exportación a PDF

Bug fixes:
- Corrección en validación de tokens
- Mejora en manejo de errores de BD"

git push origin master
git push origin v1.0.0

# 5. Merge de vuelta a develop
git checkout develop
git merge --no-ff release/v1.0.0
git push origin develop

# 6. Limpiar
git branch -d release/v1.0.0
```

### Caso 4: Hotfix Urgente en Producción

```bash
# 1. Crear hotfix desde master
git checkout master
git pull origin master
git checkout -b hotfix/sql-injection-usuarios

# 2. Corregir el bug
git add src/database/connection.py
git commit -m "fix(db): prevenir SQL injection en queries de usuarios

Se implementa sanitización de inputs y uso de
parámetros preparados en todas las queries.

Security: Fixes CVE-2024-XXXX"

# 3. Testing
# Ejecutar tests

# 4. Merge a master
git checkout master
git merge --no-ff hotfix/sql-injection-usuarios
git tag -a v1.0.1 -m "Hotfix v1.0.1 - Corrección SQL injection"
git push origin master
git push origin v1.0.1

# 5. Merge a develop
git checkout develop
git merge --no-ff hotfix/sql-injection-usuarios
git push origin develop

# 6. Limpiar
git branch -d hotfix/sql-injection-usuarios
```

## 🔒 Protección de Ramas

En GitHub, configura protección para `master` y `develop`:

**Settings → Branches → Add rule**

Para `master`:
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass
- ✅ Include administrators
- ✅ Restrict who can push (solo releases y hotfixes)

Para `develop`:
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass

## 📊 Visualizar el Flujo

```bash
# Ver historial gráfico
git log --graph --oneline --all --decorate

# Alias útil (agregar a ~/.gitconfig)
git config --global alias.lg "log --graph --oneline --all --decorate --abbrev-commit"

# Usar el alias
git lg
```

## 📚 Referencias

- [GitFlow Original (Vincent Driessen)](https://nvie.com/posts/a-successful-git-branching-model/)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

---

**Resumen**:
- `master` = Producción (solo releases y hotfixes)
- `develop` = Desarrollo activo (features se mergean aquí)
- `feature/*` = Nuevas funcionalidades (vida corta)
- `release/*` = Preparación de release (vida corta)
- `hotfix/*` = Correcciones urgentes (vida muy corta)
- Tags = Versiones específicas (permanentes)
