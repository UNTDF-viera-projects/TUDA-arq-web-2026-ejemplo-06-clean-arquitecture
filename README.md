# Actividad 06 — Ejecución reproducible

Misma API de actividades e inscripciones, con dos modos de ejecución. El contrato HTTP (`/api/v1/...`) no cambia.

## Requisitos

- Docker y Docker Compose
- (Opcional, modo local sin contenedores) Python 3.13+, pnpm

```bash
cp .env.example .env
```

## Modo desarrollo

Vite + `runserver` + PostgreSQL + Mailpit. Recarga en caliente y puertos habituales.

```bash
docker compose up --build
```

| Servicio   | URL                         |
| ---------- | --------------------------- |
| Frontend   | http://127.0.0.1:5173/      |
| Backend    | http://127.0.0.1:8000/      |
| OpenAPI    | http://127.0.0.1:8000/api/v1/docs |
| Mailpit    | http://127.0.0.1:8025/      |

En la interfaz: iniciar sesión con `demo` / `demo`, inscribirse en una actividad y revisar el email en Mailpit.

El notificador se elige con `NOTIFICADOR` (`smtp` por defecto, `memoria` o `fallo`):

```bash
NOTIFICADOR=fallo docker compose up --build
```

Con `fallo`, la inscripción se confirma igual (201) y el error queda en el log del backend.

También se puede inscribir desde la terminal, con el mismo caso de uso que usa la API:

```bash
docker compose exec backend python manage.py inscribir demo <uuid-de-la-actividad>
```

### Entrada gRPC (rama opcional)

`compose.yaml` levanta también el servicio `grpc` (puerto 50051): el mismo caso de uso `Inscribir`
detrás de otro protocolo. La identidad es el mismo access JWT de la API HTTP, en la metadata
`authorization`. Con [grpcurl](https://github.com/fullstorydev/grpcurl):

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/v1/token/ \
  -H 'Content-Type: application/json' -d '{"username":"demo","password":"demo"}' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["access"])')

grpcurl -plaintext -proto backend/activities/presentation/grpc/inscripciones.proto \
  -H "authorization: Bearer $TOKEN" \
  -d '{"actividad_id": "<uuid-de-la-actividad>"}' \
  localhost:50051 inscripciones.v1.Inscripciones/Inscribir
```

La regla de dependencias entre capas está en `backend/.importlinter` y se verifica con los tests
(`python manage.py test`) o directamente:

```bash
docker compose exec backend lint-imports
```

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

Sin `POSTGRES_HOST`, Django usa SQLite. Sin Mailpit, el backend escribe el email en la consola.

## Modo objetivo (topología productiva local)

Build de React + Gunicorn + PostgreSQL. **Nginx es el punto de entrada de la app** (puerto 8080). Backend y DB quedan en la red interna. Mailpit queda publicado en 8025 para inspeccionar correos.

```bash
docker compose -f compose.prod.yaml up --build
```

Abrir http://127.0.0.1:8080/

- `/` → build estático de React
- `/api/*` → proxy a Django (Gunicorn)
- Mailpit → http://127.0.0.1:8025/

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

Usuario de demostración: `demo` / `demo` (`demo@example.com`). Las rutas `/me` usan `Authorization: Bearer <access>` obtenido en `POST /api/v1/token/`. Un `PUT` que crea la inscripción envía un email de confirmación.

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
| `compose.yaml` | Desarrollo (db + backend + frontend + mailpit) |
| `compose.prod.yaml` | Objetivo (db + backend + nginx + mailpit; app en 8080) |
