# Actividad 06 — Ejecución reproducible

Misma API de actividades e inscripciones, con dos modos de ejecución. El contrato HTTP (`/api/v1/...`) no cambia.

## Requisitos

- Docker y Docker Compose
- (Opcional, modo local sin contenedores) Python 3.13+, pnpm

```bash
cp .env.example .env
```

## Modo desarrollo

Vite + `runserver` + PostgreSQL. Recarga en caliente y puertos habituales.

```bash
docker compose up --build
```

| Servicio   | URL                         |
| ---------- | --------------------------- |
| Frontend   | http://127.0.0.1:5173/      |
| Backend    | http://127.0.0.1:8000/      |
| OpenAPI    | http://127.0.0.1:8000/api/v1/docs |

Detener:

```bash
docker compose down
```

Los datos de PostgreSQL viven en el volumen `pgdata`. Sobreviven a `docker compose down`. Se borran con `docker compose down -v`.

### Solo Parte A (backend con SQLite, sin Compose)

```bash
cd backend
docker build -t untdf-backend .
docker run --rm -p 8000:8000 \
  -v "${PWD}:/app" \
  untdf-backend \
  sh -c "python manage.py migrate --noinput && python manage.py seed_activities && python manage.py runserver 0.0.0.0:8000"
```

Sin `POSTGRES_HOST`, Django usa SQLite.

## Modo objetivo (topología productiva local)

Build de React + Gunicorn + PostgreSQL. **Nginx es el único punto de entrada** (puerto 8080). Backend y DB quedan en la red interna.

```bash
docker compose -f compose.prod.yaml up --build
```

Abrir http://127.0.0.1:8080/

- `/` → build estático de React
- `/api/*` → proxy a Django (Gunicorn)

Detener:

```bash
docker compose -f compose.prod.yaml down
```

## Verificación del contrato

Con cualquiera de los dos modos:

```bash
curl -sS http://127.0.0.1:8000/api/v1/activities   # desarrollo
curl -sS http://127.0.0.1:8080/api/v1/activities    # objetivo
```

Usuario de demostración: `demo` / `demo`. Las rutas `/me` usan `Authorization: Bearer <access>` obtenido en `POST /api/v1/token/`.

## API

- `POST /api/v1/token/`
- `POST /api/v1/token/refresh/`
- `GET /api/v1/activities`
- `GET /api/v1/activities/{activity_id}`
- `GET /api/v1/me/enrollments`
- `PUT /api/v1/me/enrollments/{activity_id}`
- `DELETE /api/v1/me/enrollments/{activity_id}`

## Piezas Docker

| Archivo | Rol |
| --- | --- |
| `backend/Dockerfile` | Dev: dependencias + `runserver` (código por volumen) |
| `backend/prod.Dockerfile` | Objetivo: código en imagen + Gunicorn |
| `frontend/Dockerfile` | Dev: Node/pnpm + Vite |
| `frontend/prod.Dockerfile` | Objetivo: multi-stage build → Nginx + `nginx.conf` |
| `compose.yaml` | Desarrollo (db + backend + frontend) |
| `compose.prod.yaml` | Objetivo (db + backend + nginx; solo publica 8080) |
