# Ejercicio: Cancelar y Consultar como casos de uso

En `e14` solo **inscribir** sigue la arquitectura completa. `DELETE /me/enrollments/{id}` y
`GET /me/enrollments` todavía usan el ORM directamente desde la vista
(`backend/activities/presentation/http/views.py`). Tu tarea es aplicarles el mismo patrón.

## Qué hay que lograr

1. **`application/cancelar.py`**: clase `Cancelar(repositorio)` con
   `ejecutar(participante, actividad_id) -> None`.
   - Lanza `ActividadNoEncontrada` si la actividad no existe.
   - Elimina solo la inscripción de ese participante y libera el cupo.
   - Es idempotente: cancelar dos veces no es un error.
2. **`application/consultar.py`**: clase `ConsultarMisInscripciones(repositorio)` con
   `ejecutar(participante) -> list[Inscripcion]`, de la más antigua a la más nueva y solo las del
   participante.
3. **Puerto**: los métodos que necesiten esos casos de uso se agregan a `RepositorioInscripciones`
   en `application/puertos.py`. Pensalos desde lo que necesita la aplicación, no desde el ORM.
4. **Adaptadores**: implementá esos métodos en `infrastructure/db/repositorio_django.py` y en el
   repositorio de prueba `tests/fakes.py`.
5. **Composición**: `composition.py` arma los dos casos de uso.
6. **Vistas**: `GET` y `DELETE` de `/me/enrollments` delegan en los casos de uso y solo traducen
   HTTP (usá `participante_actual` e `inscripcion_a_json`, como hace `put`).

## Cómo sé que terminé

```bash
cd backend
python manage.py test        # todos en verde, incluidos los nuevos y el de arquitectura
lint-imports                 # 3 contratos KEPT
```

- `tests/test_cancelar.py` y `tests/test_consultar.py` hoy fallan: no existen los casos de uso.
  Están escritos contra el repositorio en memoria, así que corren sin base de datos.
- `tests/test_contrato_api.py` no se toca: el contrato HTTP tiene que seguir igual.
- `test_libera_el_cupo` usa `repositorio.obtener_actividad(...)`: es una pista sobre uno de los
  métodos del puerto.

## Preguntas para la entrega

1. ¿Qué métodos agregaste al puerto y por qué con esos nombres?
2. ¿Dónde quedó la transacción de `Cancelar`? ¿Hace falta?
3. Las vistas de actividades (`GET /activities`) todavía usan el ORM. ¿Vale la pena llevarlas a un
   caso de uso? Argumentá con lo que vimos sobre costos y beneficios.
