---
name: gitflow-workflow
description: Skill para gestión de Git y GitHub usando GitFlow. Incluye flujos de trabajo para features, releases, hotfixes, PRs, y mantenimiento del repositorio.
version: 1.0.0
author: Angel
tools: git, gh (GitHub CLI)
---

# GitFlow Workflow Skill

Skill para mantener el repositorio organizado usando **GitFlow** con integración de **GitHub CLI**.

## Estructura de Ramas

```
master (producción)
│
├── hotfix/*        ← Correcciones urgentes de producción
│
└── develop (desarrollo)
    │
    ├── release/*   ← Preparación de releases
    │
    └── feature/*   ← Nuevas funcionalidades
```

### Ramas Principales

| Rama | Propósito | Protegida |
|------|-----------|-----------|
| `master` | Código en producción | Si |
| `develop` | Integración de desarrollo | Si |

### Ramas de Soporte

| Tipo | Prefijo | Base | Merge a |
|------|---------|------|---------|
| Feature | `feature/` | `develop` | `develop` |
| Release | `release/` | `develop` | `master` + `develop` |
| Hotfix | `hotfix/` | `master` | `master` + `develop` |

---

## Flujos de Trabajo

### 1. Nueva Feature

```bash
# 1. Actualizar develop
git checkout develop
git pull origin develop

# 2. Crear rama de feature
git checkout -b feature/nombre-descriptivo

# 3. Desarrollar (commits atómicos)
git add <archivos>
git commit -m "feat(scope): descripción"

# 4. Push y crear PR
git push -u origin feature/nombre-descriptivo

# 5. Crear PR via GitHub CLI
gh pr create \
  --base develop \
  --title "feat(scope): descripción corta" \
  --body "$(cat <<'EOF'
## Resumen
- Cambio 1
- Cambio 2

## Test Plan
- [ ] Test manual realizado
- [ ] Tests unitarios pasan

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"

# 6. Después del merge, limpiar
git checkout develop
git pull origin develop
git branch -d feature/nombre-descriptivo
git push origin --delete feature/nombre-descriptivo  # opcional
```

### 2. Release

```bash
# 1. Crear rama de release desde develop
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0

# 2. Bump version, changelog, últimos ajustes
# Editar version en archivos necesarios
git add .
git commit -m "chore(release): preparar v1.2.0"

# 3. Push release branch
git push -u origin release/v1.2.0

# 4. Crear PR a master
gh pr create \
  --base master \
  --title "release: v1.2.0" \
  --body "$(cat <<'EOF'
## Release v1.2.0

### Features
- feat1
- feat2

### Fixes
- fix1

### Breaking Changes
- ninguno

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"

# 5. Después del merge a master, crear tag
git checkout master
git pull origin master
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0

# 6. Merge release a develop también
git checkout develop
git merge release/v1.2.0
git push origin develop

# 7. Limpiar
git branch -d release/v1.2.0
git push origin --delete release/v1.2.0
```

### 3. Hotfix

```bash
# 1. Crear hotfix desde master
git checkout master
git pull origin master
git checkout -b hotfix/descripcion-bug

# 2. Corregir el bug
git add <archivos>
git commit -m "fix(scope): descripción del fix"

# 3. Push y PR a master
git push -u origin hotfix/descripcion-bug

gh pr create \
  --base master \
  --title "hotfix: descripción corta" \
  --body "$(cat <<'EOF'
## Hotfix

### Problema
Descripción del bug en producción.

### Solución
Descripción de la corrección.

### Test Plan
- [ ] Verificado en ambiente de prueba

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"

# 4. Después del merge, actualizar tag
git checkout master
git pull origin master
git tag -a v1.2.1 -m "Hotfix v1.2.1"
git push origin v1.2.1

# 5. Merge hotfix a develop
git checkout develop
git pull origin develop
git merge hotfix/descripcion-bug
git push origin develop

# 6. Limpiar
git branch -d hotfix/descripcion-bug
git push origin --delete hotfix/descripcion-bug
```

---

## Convención de Commits

### Formato

```
<type>(<scope>): <description>

[optional body]

[optional footer]
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

### Tipos

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| `feat` | Nueva funcionalidad | `feat(auth): agregar login con Google` |
| `fix` | Corrección de bug | `fix(api): corregir timeout en requests` |
| `refactor` | Refactorización sin cambio de comportamiento | `refactor(agent): extraer clasificador` |
| `docs` | Documentación | `docs(readme): actualizar instalación` |
| `test` | Tests | `test(tools): agregar tests para QueryTool` |
| `chore` | Mantenimiento | `chore(deps): actualizar dependencias` |
| `style` | Formato, espacios, etc. | `style(lint): aplicar black formatter` |
| `perf` | Mejora de performance | `perf(db): optimizar query de ventas` |
| `ci` | CI/CD | `ci(github): agregar workflow de tests` |

### Scopes del Proyecto

| Scope | Área |
|-------|------|
| `agent` | `src/agent/` - LLMAgent, classifiers, memory |
| `bot` | `src/bot/` - Handlers de Telegram |
| `tools` | `src/tools/` - Sistema de tools |
| `db` | `src/database/` - Conexión y queries |
| `auth` | `src/auth/` - Autenticación y permisos |
| `api` | `src/api/` - API REST |
| `config` | `src/config/` - Configuración |
| `prompts` | `src/agent/prompts/` - Templates de prompts |
| `knowledge` | `src/agent/knowledge/` - Base de conocimiento |
| `memory` | `src/agent/memory/` - Sistema de memoria |
| `deps` | Dependencias (Pipfile, requirements) |
| `ci` | GitHub Actions, CI/CD |

### Ejemplos de Commits Buenos

```bash
# Feature
git commit -m "feat(agent): implementar ReActAgent con loop de razonamiento

- Agregar Scratchpad para historial de pasos
- Implementar execute() con máximo 10 iteraciones
- Agregar tools: database_query, knowledge_search, calculate

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

# Fix
git commit -m "fix(db): corregir SQL injection en execute_query

Usar queries parametrizadas en lugar de f-strings.

Closes #123

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

# Refactor
git commit -m "refactor(tools): extraer validación a ToolValidator

Mover lógica de validación de parámetros a clase dedicada
para mejorar testabilidad.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## GitHub CLI (gh)

### Autenticación

```bash
# Login
gh auth login

# Verificar
gh auth status
```

### Pull Requests

```bash
# Listar PRs abiertos
gh pr list

# Ver PR específico
gh pr view 123

# Crear PR
gh pr create --base develop --title "título" --body "descripción"

# Checkout a PR para revisar
gh pr checkout 123

# Aprobar PR
gh pr review 123 --approve

# Merge PR
gh pr merge 123 --merge  # merge commit
gh pr merge 123 --squash # squash and merge
gh pr merge 123 --rebase # rebase and merge

# Cerrar PR sin merge
gh pr close 123
```

### Issues

```bash
# Listar issues
gh issue list

# Crear issue
gh issue create --title "Bug: descripción" --body "detalles"

# Ver issue
gh issue view 123

# Cerrar issue
gh issue close 123
```

### Releases

```bash
# Crear release
gh release create v1.2.0 --title "v1.2.0" --notes "Changelog..."

# Listar releases
gh release list

# Ver release
gh release view v1.2.0
```

### Acciones Útiles

```bash
# Ver estado de checks del PR actual
gh pr checks

# Ver diff del PR
gh pr diff 123

# Agregar reviewer
gh pr edit 123 --add-reviewer usuario

# Agregar labels
gh pr edit 123 --add-label "feature"

# Ver workflows de GitHub Actions
gh run list

# Ver logs de un workflow
gh run view 123456 --log
```

---

## Comandos Git Útiles

### Estado y Logs

```bash
# Estado conciso
git status -s

# Log de una línea
git log --oneline -10

# Log con gráfico
git log --oneline --graph --all -20

# Ver cambios sin staged
git diff

# Ver cambios staged
git diff --staged

# Ver qué archivos cambiaron
git diff --stat HEAD~5
```

### Branches

```bash
# Listar ramas locales
git branch

# Listar todas (incluyendo remotas)
git branch -a

# Crear y cambiar a rama
git checkout -b feature/nueva

# Cambiar de rama
git checkout develop

# Eliminar rama local
git branch -d feature/vieja

# Eliminar rama remota
git push origin --delete feature/vieja

# Renombrar rama actual
git branch -m nuevo-nombre
```

### Stash

```bash
# Guardar cambios en stash
git stash push -m "WIP: descripción"

# Listar stashes
git stash list

# Aplicar último stash
git stash pop

# Aplicar stash específico
git stash apply stash@{2}

# Eliminar stash
git stash drop stash@{0}

# Limpiar todos los stashes
git stash clear
```

### Rebase

```bash
# Rebase sobre develop
git checkout feature/mi-feature
git fetch origin
git rebase origin/develop

# Rebase interactivo (últimos 5 commits)
git rebase -i HEAD~5

# Si hay conflictos
git rebase --continue  # después de resolver
git rebase --abort     # cancelar rebase
```

### Reset y Restore

```bash
# Deshacer último commit (mantiene cambios)
git reset --soft HEAD~1

# Deshacer último commit (descarta cambios staged)
git reset HEAD~1

# Deshacer cambios en un archivo
git restore archivo.py

# Deshacer todos los cambios no staged
git restore .

# Unstage un archivo
git restore --staged archivo.py
```

### Cherry-pick

```bash
# Traer commit específico a rama actual
git cherry-pick abc1234

# Cherry-pick sin commit automático
git cherry-pick --no-commit abc1234
```

---

## Flujo de Trabajo del Proyecto

### Ramas de Migración ReAct

```
develop
└── feature/react-agent-migration (rama principal)
    ├── feature/react-fase1-foundation
    ├── feature/react-fase2-tools
    ├── feature/react-fase3-core
    ├── feature/react-fase4-single-step-agents
    ├── feature/react-fase5-orchestrator
    ├── feature/react-fase6-integration
    └── feature/react-fase7-polish
```

### Workflow para Fases ReAct

```bash
# 1. Trabajar en una fase
git checkout feature/react-fase1-foundation
# ... desarrollar ...

# 2. Commit
git add .
git commit -m "feat(agents): implementar BaseAgent y contratos"

# 3. Push
git push origin feature/react-fase1-foundation

# 4. PR a rama principal de migración
gh pr create \
  --base feature/react-agent-migration \
  --title "feat(agents): Fase 1 - Foundation" \
  --body "Implementación de contratos base..."

# 5. Después del merge, actualizar siguiente fase
git checkout feature/react-fase2-tools
git rebase feature/react-agent-migration
git push --force-with-lease origin feature/react-fase2-tools

# 6. Continuar con siguiente fase...
```

### Al Completar Migración

```bash
# PR de migración completa a develop
gh pr create \
  --base develop \
  --head feature/react-agent-migration \
  --title "feat(architecture): migración a arquitectura ReAct Agent" \
  --body "Migración completa del sistema a arquitectura multi-agent..."
```

---

## Resolución de Conflictos

### Merge Conflicts

```bash
# 1. Ver archivos con conflictos
git status

# 2. Abrir archivo y buscar marcadores
<<<<<<< HEAD
código local
=======
código remoto
>>>>>>> branch-name

# 3. Resolver manualmente, luego:
git add archivo-resuelto.py
git commit -m "fix: resolver conflictos de merge"
```

### Rebase Conflicts

```bash
# 1. Resolver conflicto
# Editar archivos...

# 2. Marcar como resuelto
git add archivo-resuelto.py

# 3. Continuar rebase
git rebase --continue

# 4. Si es muy complicado, abortar
git rebase --abort
```

---

## Limpieza y Mantenimiento

### Limpiar Ramas Mergeadas

```bash
# Ver ramas mergeadas a develop
git checkout develop
git branch --merged

# Eliminar ramas locales mergeadas (excepto develop y master)
git branch --merged | grep -v "develop\|master" | xargs git branch -d

# Limpiar referencias remotas obsoletas
git fetch --prune

# Limpiar ramas remotas que ya no existen
git remote prune origin
```

### Verificar Estado del Repo

```bash
# Verificar integridad
git fsck

# Ver tamaño del repo
git count-objects -vH

# Limpiar objetos no referenciados
git gc --prune=now
```

### Sincronizar con Remote

```bash
# Actualizar todas las ramas
git fetch --all

# Ver diferencias con remote
git log origin/develop..develop  # commits locales no pusheados
git log develop..origin/develop  # commits remotos no pulleados

# Actualizar develop
git checkout develop
git pull origin develop

# Actualizar feature con develop
git checkout feature/mi-feature
git rebase origin/develop
```

---

## Protecciones de Seguridad

### Nunca Hacer

```bash
# ❌ NUNCA force push a master/develop
git push --force origin master  # ¡PELIGROSO!
git push --force origin develop # ¡PELIGROSO!

# ❌ NUNCA reset --hard sin verificar
git reset --hard origin/master  # Pierde cambios locales

# ❌ NUNCA commitear secrets
git add .env        # ¡NO!
git add credentials # ¡NO!
```

### Buenas Prácticas

```bash
# ✅ Usar force-with-lease en lugar de force
git push --force-with-lease origin feature/mi-rama

# ✅ Verificar antes de reset
git stash  # Guardar cambios primero
git reset --hard origin/develop

# ✅ Verificar qué se va a pushear
git log origin/develop..HEAD  # Ver commits a pushear
git push origin develop       # Luego push

# ✅ Usar .gitignore correctamente
echo ".env" >> .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
```

---

## Templates

### Template de PR - Feature

```markdown
## Resumen
Breve descripción de qué hace esta feature.

## Cambios
- Cambio 1
- Cambio 2
- Cambio 3

## Screenshots (si aplica)
[Agregar screenshots]

## Test Plan
- [ ] Tests unitarios agregados
- [ ] Tests de integración pasan
- [ ] Probado manualmente en desarrollo

## Checklist
- [ ] Código sigue convenciones del proyecto
- [ ] Documentación actualizada si es necesario
- [ ] No hay console.log/print de debug
- [ ] No hay secrets hardcodeados

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Template de PR - Hotfix

```markdown
## Problema
Descripción del bug en producción.

## Causa Raíz
Qué causó el problema.

## Solución
Cómo se corrigió.

## Impacto
Qué usuarios/funcionalidades estaban afectados.

## Test Plan
- [ ] Bug reproducido localmente
- [ ] Fix verificado localmente
- [ ] No hay regresiones

## Rollback Plan
Pasos para revertir si algo sale mal.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Template de Commit - Feature Grande

```
feat(scope): título corto (max 50 chars)

Descripción más detallada del cambio. Explicar el "por qué"
más que el "qué". El código explica el qué; el commit message
explica el contexto y la motivación.

- Punto 1 del cambio
- Punto 2 del cambio
- Punto 3 del cambio

Closes #123
Related to #456

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

---

## Aliases Útiles

Agregar a `~/.gitconfig`:

```ini
[alias]
    # Status corto
    s = status -s

    # Log bonito
    lg = log --oneline --graph --all -20

    # Último commit
    last = log -1 HEAD --stat

    # Branches ordenadas por fecha
    recent = branch --sort=-committerdate -v

    # Diff de lo staged
    staged = diff --staged

    # Commit con mensaje
    cm = commit -m

    # Amend sin cambiar mensaje
    amend = commit --amend --no-edit

    # Push con upstream
    pushu = push -u origin HEAD

    # Pull con rebase
    pullr = pull --rebase

    # Stash con mensaje
    stashm = stash push -m

    # Undo último commit (soft)
    undo = reset --soft HEAD~1

    # Ver ramas mergeadas
    merged = branch --merged

    # Cleanup
    cleanup = "!git branch --merged | grep -v 'develop\\|master' | xargs git branch -d"
```

Uso:

```bash
git s          # status -s
git lg         # log bonito
git cm "msg"   # commit -m "msg"
git pushu      # push -u origin HEAD
git cleanup    # eliminar ramas mergeadas
```

---

*Skill de GitFlow - v1.0.0*
