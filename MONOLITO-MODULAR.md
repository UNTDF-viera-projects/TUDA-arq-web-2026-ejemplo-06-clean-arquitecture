# Opcional: corte vertical (monolito modular)

Hasta `e14` cortamos el código **en horizontal**: por tipo de responsabilidad (capas). Esta rama
agrega un corte **vertical**: notificaciones pasa a ser un módulo propio, con una interfaz pública.

```
backend/
  activities/          # módulo inscripciones (la app conserva su nombre: renombrarla obliga a migrar)
    infrastructure/notificaciones/modulo.py   # adaptador: usa notificaciones.api
  notificaciones/      # módulo nuevo
    api.py             # lo ÚNICO que otros módulos pueden importar
    tipos.py           # Correo, ErrorDeEnvio
    canales.py         # SMTP, memoria, fallo (detalle interno)
```

- Sigue siendo **un proceso, un deploy y una base**: nada se distribuye.
- Para inscripciones, el módulo de notificaciones es un mecanismo más detrás de su puerto
  `Notificador`.
- `.importlinter` suma dos contratos: inscripciones solo importa `notificaciones.api`, y
  notificaciones no conoce a inscripciones.

Pregunta abierta: separar actividades de inscripciones obliga a decidir quién es dueño de la tabla
y cómo se consulta el cupo de otro módulo (hoy `Enrollment` tiene una FK a `Activity`).
