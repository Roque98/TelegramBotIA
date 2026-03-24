# PLAN: CORS con restricciones de origen

> **Objetivo**: Restringir los orígenes permitidos en el endpoint REST del bot
> **Rama**: `feature/sec-04-cors`
> **Prioridad**: 🔴 Crítica
> **Progreso**: 0% (0/4)

---

## Contexto

`src/api/chat_endpoint.py` habilita CORS sin restricciones:

```python
CORS(app)  # Cualquier origen puede hacer requests
```

Esto permite que cualquier sitio web haga requests al endpoint del bot, lo que facilita ataques CSRF y exposición de datos de la API.

---

## Archivos involucrados

- `src/api/chat_endpoint.py` — configurar CORS
- `.env` / `.env.example` — variable `ALLOWED_ORIGINS`
- `src/config/settings.py` — leer `ALLOWED_ORIGINS`

---

## Tareas

- [ ] **4.1** Agregar variable `ALLOWED_ORIGINS` en `.env.example` con valor por defecto restrictivo
- [ ] **4.2** Leer `ALLOWED_ORIGINS` desde `settings.py` como lista (separada por comas)
- [ ] **4.3** Reemplazar `CORS(app)` por `CORS(app, origins=settings.allowed_origins, supports_credentials=True)`
- [ ] **4.4** Documentar en `.env.example` cómo configurar los orígenes permitidos

---

## Criterios de aceptación

- Un request desde un origen no configurado recibe status 403
- En desarrollo, `localhost:*` está permitido por defecto
- En producción, solo los dominios explícitamente configurados están permitidos
