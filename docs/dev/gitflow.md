[Docs](../index.md) › [Dev](README.md) › GitFlow del proyecto

# GitFlow del proyecto

---

## Ramas

| Rama | Propósito |
|------|-----------|
| `master` | Código en producción. Solo recibe merges desde `develop` vía PR. |
| `develop` | Rama de integración activa. Base para nuevas features. |
| `feature/<nombre>` | Trabajo de una feature o plan específico. |

### Crear una feature branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/nombre-descriptivo
```

### Mergear de vuelta

```bash
git checkout develop
git merge --no-ff feature/nombre-descriptivo
git push origin develop
git branch -d feature/nombre-descriptivo
```

---

## Convención de commits

Formato: `tipo(scope): descripción en minúsculas`

### Tipos

| Tipo | Usar cuando |
|------|-------------|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `refactor` | Refactorización sin cambio funcional |
| `docs` | Documentación |
| `test` | Tests |
| `chore` | Mantenimiento (dependencias, config) |
| `perf` | Mejora de rendimiento |

### Scopes del proyecto

| Scope | Módulo |
|-------|--------|
| `agent` | ReActAgent y agentes |
| `tools` | Sistema de herramientas |
| `bot` | Handlers de Telegram |
| `api` | API REST |
| `db` | Base de datos |
| `auth` | Autenticación y permisos |
| `memory` | Sistema de memoria |
| `obs` | Observabilidad |
| `plan` | Planes del proyecto |
| `docs` | Documentación |

### Ejemplos

```bash
git commit -m "feat(tools): agregar MiTool para procesar facturas"
git commit -m "fix(agent): corregir síntesis parcial cuando max_iterations=1"
git commit -m "docs(plan): crear plan DOC-34 reescritura de documentación"
git commit -m "refactor(db): extraer SQLValidator a clase separada"
```

---

## Push

Se hace push después de cada commit significativo:

```bash
git push origin develop          # rama activa
git push origin feature/nombre  # feature branch
```

---

## Ramas de planes completados

Cada plan del directorio `plan/` tiene una rama asociada. Cuando un plan se completa:

1. Asegurarse de que todo está mergeado en `develop`
2. El archivo del plan se mueve de `plan/02-activos/` a `plan/01-completados/`
3. La feature branch puede eliminarse

---

## Etiquetas de versión

Las versiones se etiquetan en `master`:

```bash
git tag -a v1.2.0 -m "Descripción del release"
git push origin v1.2.0
```

Versionado semántico: `MAJOR.MINOR.PATCH`
- `MAJOR`: cambios de arquitectura o incompatibilidad
- `MINOR`: nuevas funcionalidades
- `PATCH`: bug fixes

---

**← Anterior** [Setup local](setup.md) · [Índice](README.md) · **Siguiente →** [Testing](testing.md)
