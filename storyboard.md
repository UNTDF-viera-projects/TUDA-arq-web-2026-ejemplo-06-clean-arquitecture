# Storyboard — Organizar el código: de la vista gorda a puertos y adaptadores

Docente: Leonel Viera · Arquitecturas Web · UNTDF
Formato: **una presentación continua organizada en bloques** · el docente regula el ritmo (hasta 4 encuentros) · ~60 slides · reveal.js offline
Caso conductor: inscripción a actividades + correo de confirmación (Mailpit)

---

## La idea en una línea

**Primero el mapa, después el viaje.** Los chicos ven desde el minuto 10 la estructura a la que vamos a llegar, y después
recorremos el camino en ramas chicas, cada una motivada por un dolor concreto. El contrato HTTP y el frontend **no
cambian nunca**: reorganizamos sin romper.

### El hilo conductor: tres preguntas

Al final de la apertura dejamos escritas tres preguntas que la vista gorda no puede responder. Cada una se "tilda" en el
minimapa cuando una rama la resuelve.

| # | Pregunta | Se resuelve en |
| --- | --- | --- |
| P1 | ¿Cómo pruebo la regla de cupo sin levantar HTTP, base de datos ni SMTP? | `e05` (parcial) → `e12` |
| P2 | Si mañana el correo sale por una API (o por WhatsApp), ¿qué código tengo que tocar? | `e07` → `e09` |
| P3 | Si quiero inscribir desde la terminal (o desde un script de carga), ¿reescribo la lógica? | `e13` |

### Dos ejes: horizontal y vertical

- **Horizontal (capas)**: cortamos por *tipo de responsabilidad*. Es el eje del recorrido principal.
- **Vertical (módulos)**: cortamos por *capacidad del negocio*. Se presenta como concepto en el bloque 2 (para nombrarlo) y
  se retoma en el bloque 13. El código vive **solo** en la rama opcional `opcional-monolito-modular`.

---

## Formato: reveal.js (misma base que la clase de Docker)

Se reutiliza `clase-docker-fede/slides`: reveal.js vendorizado, `untdf.css`, notas de orador (`S`), PDF con `?print-pdf`,
callouts sincronizados con `data-line-numbers`.

Extensiones a `slides/build.py`:

| Atributo | Qué hace |
| --- | --- |
| `data-incluir="e05:backend/activities/domain/reglas.py"` | Inserta el archivo **tal como está en esa rama** (`git show rama:ruta`). Sin rama, usa el árbol de trabajo. |
| `data-diff="e06..e07:backend/activities/application/inscribir.py"` | Inserta el diff entre dos ramas, resaltado (+ verde / − rojo). |
| `data-arbol="e06:backend/activities"` | Árbol de carpetas de esa rama (genera el HTML del árbol). |
| `data-grafo="e06"` | JSON con el grafo de imports entre capas de esa rama (lo calcula con `ast`). Alimenta la herramienta H4. |

Si la rama local no existe, `build.py` prueba `origin/<rama>`. El `index.html` generado se commitea, así los chicos lo
abren sin compilar nada.

## Identidad visual

Igual que la clase de Docker (rojo UNTDF `#BE1C1D`, gris `#6F6F6E`, fondo oscuro para código). Se agrega una **paleta
de capas** que se usa en todo el material (árbol, código coloreado, hexágono, grafo):

| Capa / rol | Color | Uso |
| --- | --- | --- |
| Presentación / adaptador de entrada | violeta `#7B5EA7` | vistas, serializers, comando CLI |
| Aplicación (casos de uso) | azul `#2F6DB5` | `Inscribir`, DTO |
| Dominio (reglas) | verde `#2E8B57` | dataclasses, `reglas.py`, errores |
| Puertos (contratos) | rojo UNTDF `#BE1C1D` | `Notificador`, `RepositorioInscripciones` |
| Infraestructura / adaptador de salida | gris `#6F6F6E` | ORM, SMTP, memoria, fallo |
| Composición | ámbar `#C98A1B` | `composition.py` |

Flechas: **azul continua = llamada en ejecución**; **roja discontinua = dependencia de código (import / implementa)**.

## Componentes recurrentes

- **Minimapa de ramas** (esquina superior derecha, en todas las slides de código): fila de puntitos `e00 … e14`, el
  actual en rojo; debajo, las tres preguntas P1–P3 con su estado (☐ / ◐ / ☑) y un indicador "tests de contrato ✔".
- **Etiqueta de rama** en cada slide de código: `git checkout e05-reglas-de-dominio`, para que los chicos la sigan.
- **Anatomía de archivo** (como el Dockerfile): código a la izquierda, callouts ①②③ a la derecha que se encienden con
  la línea resaltada. Hay una anatomía por **tipo de componente** (ver "Cómo se escribe cada componente").
- **Diff de etapa**: "qué cambió en esta rama", con `+`/`−` y un resumen de una línea arriba.
- **Terminal 🧪**: igual que en Docker, comandos que aparecen de a uno.
- **Árbol coloreado**: la estructura de carpetas con cada archivo pintado según su capa.
- **Slide 🛠 Herramienta**: marca una herramienta interactiva (H1–H5).
- **Pregunta tildada**: animación corta cuando una rama resuelve P1, P2 o P3.

---

## Mapa de ramas

Cada rama sale de la anterior y tiene **un commit chico**. En **todas** pasan los tests de contrato
(`python manage.py test`) y levanta `docker compose up`.

| Rama | Bloque | Cambio | Concepto |
| --- | --- | --- | --- |
| `e00-base` | 1 | Actividad 06 tal cual (`modular-capas@63d3cb5`) | Punto de partida |
| `e01-email-en-la-vista` | 1 | La vista del `PUT` envía el correo (`modular-capas@d2a59fd`) | El dolor: responsabilidades mezcladas |
| `e02-red-de-seguridad` | 3 | Test del correo con backend `locmem` | Refactor = cambiar estructura sin cambiar comportamiento |
| `e03-caso-de-uso` | 4 | La lógica del `PUT` pasa a `application/inscribir.py` | Capa de aplicación |
| `e04-errores-de-aplicacion` | 4 | El caso de uso lanza `CupoAgotado` / `ActividadNoEncontrada`; la vista traduce a HTTP | Presentación delgada |
| `e05-reglas-de-dominio` | 4 | `hay_cupo`, `exigir_cupo` como funciones puras; los errores pasan a `domain/errores.py`; tests sin base | Capa de dominio |
| `e06-carpetas-por-capa` | 4 | `presentation/`, `infrastructure/email.py` explícitos | Capas tradicionales (dependencias hacia abajo) |
| `e07-puerto-notificador` | 9 | `Notificador` (Protocol) + `ConfirmacionInscripcion`; `Inscribir` lo recibe por constructor | DIP + DI, puerto de salida |
| `e08-adaptadores-memoria-y-fallo` | 9 | `NotificadorMemoria`, `NotificadorFallo` + tests | Un puerto, varias implementaciones |
| `e09-composicion` | 9 | `composition.py` elige por `NOTIFICADOR=smtp\|memoria\|fallo` | Raíz de composición |
| `e10-dominio-puro` | 10 | Dataclasses `Actividad`, `Inscripcion` sin Django | Dominio independiente del framework |
| `e11-puerto-repositorio` | 10 | `RepositorioInscripciones` + adaptador Django (`select_for_update` adentro) | Puerto de persistencia |
| `e12-repositorio-en-memoria` | 10 | Tests del caso de uso sin base ni SMTP | Probar el interior aislado |
| `e13-entrada-cli` | 11 | `manage.py inscribir <usuario> <actividad>` | Adaptador de entrada |
| `e14-regla-como-test` | 12 | `import-linter`: el dominio y la aplicación no importan Django | La regla de dependencias, verificable |
| `ejercicio-cancelar-consultar` | 14 | Sale de `e14`: consigna + tests que fallan | Aplicar el patrón |
| `solucion-cancelar-consultar` | — | Solución de referencia | — |
| `opcional-monolito-modular` | 13 | Sale de `e14`: `notificaciones/` como módulo con `api.py` público | Corte vertical |
| `main` | — | `e14` + `slides/` + `storyboard.md` | — |

## A dónde llegamos: estructura final (`e14`)

```
backend/
  config/                          # proyecto Django: settings, urls (no es una capa)
  activities/
    models.py                      # ORM — infraestructura, pero Django lo busca acá
    admin.py, apps.py
    migrations/
    composition.py                 # COMPOSICIÓN: arma Inscribir con sus adaptadores

    domain/                        # DOMINIO — sin imports de Django
      modelos.py                   #   @dataclass Actividad, Inscripcion
      reglas.py                    #   hay_cupo(), exigir_cupo()
      errores.py                   #   CupoAgotado, ActividadNoEncontrada

    application/                   # APLICACIÓN — coordina, depende solo de domain + puertos
      puertos.py                   #   Notificador, RepositorioInscripciones (Protocol)
      dto.py                       #   ConfirmacionInscripcion, ResultadoInscripcion
      inscribir.py                 #   class Inscribir(repositorio, notificador)

    infrastructure/                # ADAPTADORES DE SALIDA
      db/repositorio_django.py     #   implementa RepositorioInscripciones con el ORM
      notificaciones/
        smtp.py                    #   NotificadorSMTP → Mailpit
        memoria.py                 #   NotificadorMemoria
        fallo.py                   #   NotificadorFallo

    presentation/                  # ADAPTADORES DE ENTRADA
      http/views.py                #   DRF: request → caso de uso → response
      http/serializers.py
      http/urls.py
    management/commands/
      inscribir.py                 # adaptador de entrada CLI (Django lo exige en esta ruta)
      seed_activities.py

    tests/
      test_contrato_api.py         # red de seguridad: no cambia desde e02
      test_reglas.py               # dominio, sin base
      test_inscribir.py            # caso de uso con repositorio y notificador en memoria
      fakes.py                     # RepositorioEnMemoria
  .importlinter                    # la regla de dependencias como test
```

Dos aclaraciones que aparecen en las slides:

1. **Idioma**: las carpetas de capa usan el vocabulario estándar en inglés (`domain/`, `application/`, …), que es el que
   van a encontrar en la bibliografía. Archivos, clases y funciones del dominio y la aplicación van en español. Los
   modelos Django (`Activity`, `Enrollment`) y la API HTTP ya existían en inglés y no se tocan.
2. **El framework también opina**: `models.py`, `migrations/` y `management/commands/` quedan donde Django los busca. La
   capa es un concepto, no una carpeta obligatoria.

## Cómo se escribe cada componente (anatomías)

Cada uno tiene su slide de anatomía y aparece en el machete final.

| Componente | Archivo | Qué sabe | Qué **no** sabe |
| --- | --- | --- | --- |
| Adaptador de entrada HTTP | `presentation/http/views.py` | request, identidad, códigos HTTP, el caso de uso | ORM, SMTP, reglas |
| Adaptador de entrada CLI | `management/commands/inscribir.py` | argumentos, salida por consola, el caso de uso | HTTP |
| Caso de uso | `application/inscribir.py` | el orden de la operación, los puertos | Django, SMTP, HTTP |
| Regla de dominio | `domain/reglas.py` | el negocio (cupo, duplicados) | todo lo demás |
| Entidad de dominio | `domain/modelos.py` | datos y significado | cómo se guardan |
| Puerto | `application/puertos.py` | *qué* necesita la aplicación | *cómo* se hace |
| Adaptador de salida | `infrastructure/...` | el mecanismo (ORM, SMTP) y cómo traducir errores | reglas, HTTP |
| Composición | `composition.py` | qué implementación va con qué | — (es el único lugar que conoce todo) |

---

## Herramientas interactivas

Todas están hechas en HTML/JS dentro de reveal.js, funcionan offline y leen datos que genera `build.py` desde las ramas.

| Id | Nombre | Qué hace | Datos | Dónde aparece |
| --- | --- | --- | --- | --- |
| H1 | **Coloreá la vista gorda** | El `put()` de `e01` línea por línea. Clic en una línea → ciclo de colores de capa. Botón "ver propuesta" muestra la clasificación del docente; contador "¿cuántas capas conoce esta función?". | `e01:views.py` + clasificación en JSON | Bloque 1 |
| H2 | **Explorador del destino** | Árbol final a la izquierda, hexágono a la derecha. Clic en un archivo → se ilumina su lugar en el hexágono y aparecen sus imports como flechas. | `e14` árbol + grafo | Bloques 0, 6 y 14 |
| H3 | **Llamadas vs. dependencias** | Una petición `PUT` animada paso a paso por el hexágono (flechas azules). Interruptor → muestra las dependencias de código (rojas discontinuas). Selector de entrada HTTP / CLI. | estático | Bloques 7 y 11 |
| H4 | **Grafo de imports por etapa** | Deslizador `e01 … e14`. Nodos = capas (con su color), aristas = imports reales. Se ve cómo la flecha `aplicación → infraestructura` se invierte en `e07`. Aristas que violan la regla, en rojo. | `data-grafo` por rama | Bloques 4, 6 y 12 |
| H5 | **Cambiá el adaptador** | Selector SMTP / Memoria / Fallo + botón "Inscribir". Muestra qué pasa: inscripción, cupo, código HTTP, buzón de Mailpit simulado, lista de memoria. | simulación en JS | Bloque 9 |

### Archify

Se evalúa (T10) para dos piezas **fuera** del flujo de las slides, solo si el resultado funciona offline:

- **A1 · Mapa del destino**: diagrama de arquitectura generado desde `e14`, enlazado desde la slide de destino.
- **A2 · Explainer para repasar**: una página con conclusión primero, tablas y código, para el aula virtual.

Si no funciona offline, se exporta como imagen. Las herramientas H1–H5 no dependen de archify.

---

## Bloques y tiempos estimados

La presentación es una sola y no se divide por encuentro. Los minutos son orientativos: el docente decide dónde cortar
cada encuentro. Cada bloque cierra una idea, así que cualquier frontera entre bloques sirve como corte. El bloque 6
(recapitular) está pensado para usarlo al retomar después de un corte, esté donde esté.

| Bloque | Tema | Slides | Min |
| --- | --- | --- | --- |
| 0 | Apertura y destino | 4 | 10 |
| 1 | El caso y el dolor (con las cuatro preguntas para clasificar) | 7 | 28 |
| 2 | Vocabulario: arquitectura, cohesión, acoplamiento, ejes | 6 | 20 |
| 3 | Red de seguridad | 2 | 10 |
| 4 | Capas, paso a paso | 9 | 40 |
| 5 | Punto de control: capas | 2 | 10 |
| 6 | Recapitular | 2 | 7 |
| 7 | Inversión e inyección de dependencias | 4 | 15 |
| 8 | Arquitectura hexagonal | 6 | 20 |
| 9 | Puerto de salida: notificar | 6 | 25 |
| 10 | Puerto de persistencia | 5 | 20 |
| 11 | Otra entrada: CLI | 2 | 8 |
| 12 | La regla como test | 2 | 8 |
| 13 | Corte vertical: monolito modular | 3 | 10 |
| 14 | Cierre, límites y ejercicio | 4 | 10 |
| | **Total** | **64** | **241** |

---

## Bloque 0 — Apertura y destino (4 slides · 10 min)

| # | Slide | Contenido | Visual |
| --- | --- | --- | --- |
| 0.1 | Portada | "Organizar el código: de la vista gorda a puertos y adaptadores" · Arquitecturas Web · UNTDF | Fondo rojo; hexágono blanco que se arma con piezas de colores |
| 0.2 | Hoja de ruta | Los bloques en orden: del monolito a las capas (bloques 1–5), de las capas a puertos y adaptadores (6–12), el corte vertical (13). Un repo, una rama por paso | Línea de ramas `e00 … e14` con los bloques encima |
| 0.3 | **A dónde llegamos** | Árbol final coloreado + hexágono con nuestros componentes. "No hace falta entenderlo hoy: es el mapa." | 🛠 **H2** en modo "solo mirar" |
| 0.4 | Cómo seguir la clase | `git clone …` · las slides quedan abiertas en `main` · `scripts/etapa.sh e00` deja el código de la etapa en `../modular-capas-v2-codigo` · `docker compose up` ahí · el minimapa y las tres preguntas (P1–P3 aparecen recién en 1.7) | Terminal + minimapa explicado con flechas |

Notas: insistir en que el contrato HTTP no va a cambiar en todo el recorrido. El frontend es un testigo.

## Bloque 1 — El caso y el dolor (7 slides · 28 min)

| # | Slide | Contenido | Visual | Rama |
| --- | --- | --- | --- | --- |
| 1.1 | El proyecto que ya conocen | Actividades, inscripciones `PUT/DELETE /me/enrollments/{id}`, JWT, PostgreSQL. Lo que ya hicimos: contrato OpenAPI, Docker | Diagrama de tiers navegador → Django → PostgreSQL | `e00` |
| 1.2 | Nueva funcionalidad: comprobante por correo 🧪 | "Cuando alguien se inscribe, le mandamos un correo." Se agrega Mailpit al compose. Demo: inscribirse en la UI y ver el correo en `:8025` | Terminal + captura de Mailpit | `e01` |
| 1.3 | ¿Dónde lo pusimos? Anatomía de la vista | `put()` completo con callouts: ① parsear el UUID ② identidad ③ transacción y bloqueo ④ regla de duplicado ⑤ regla de cupo ⑥ crear ⑦ enviar correo ⑧ respuesta HTTP | Anatomía, `data-incluir="e01:…/views.py"` + `emails.py` al costado | `e01` |
| 1.4 | Una responsabilidad es una pregunta que el código responde | Cada línea del `put()` responde una pregunta: "¿qué devuelvo si el UUID es inválido?" (HTTP), "¿se puede inscribir si no hay cupo?" (negocio), "¿cómo le hablo a Mailpit?" (mecanismo). Si una función responde preguntas de naturaleza distinta, cualquier cambio en una de ellas obliga a tocarla | Tres líneas reales del `put()` de `e01`, cada una con su globo de pregunta | `e01` |
| 1.5 | Cuatro preguntas para clasificar cada línea | Tabla con capa · pregunta · pistas en el código · ejemplo del `put()`. **Presentación**: ¿cómo entra el pedido y cómo sale la respuesta? (request, `Response`, `status`, serializers, parsear la URL). **Aplicación**: ¿en qué orden se hacen los pasos? (transacción, "primero… después…", llamar a otras partes). **Dominio**: ¿qué regla del negocio se cumple, sin importar la tecnología? (cupo, duplicado). **Infraestructura**: ¿con qué tecnología concreta? (ORM, `send_mail`, `settings`). Aviso: una línea puede mezclar dos (la condición de cupo usa el ORM para contar), y eso también es una señal. "Capa = tipo de responsabilidad; no es carpeta ni servidor (bloque 2)" | Tabla de 4 filas con los colores de la paleta; cada ejemplo es una línea real de `e01` | `e01` |
| 1.6 | 🛠 Coloreá la vista gorda | Actividad: entre todos clasificamos cada línea con las cuatro preguntas de 1.5 (quedan visibles como leyenda). Al final: "una sola función conoce los 4 tipos de responsabilidad" | 🛠 **H1** | `e01` |
| 1.7 | Tres preguntas que esta vista no puede responder | P1, P2, P3 (ver arriba). Quedan fijas en el minimapa hasta el final | Tres tarjetas grandes con ☐ | — |

Notas: en 1.6 dejar que discutan; hay líneas ambiguas (¿`select_for_update` es regla o mecanismo?) y es bueno que
aparezca la ambigüedad.

## Bloque 2 — Vocabulario (6 slides · 20 min)

| # | Slide | Contenido | Visual |
| --- | --- | --- | --- |
| 2.1 | Qué es arquitectura (y qué es diseño) | Zoom: sistema → componente → colaboración. Arquitectura = decisiones caras de cambiar sobre partes, responsabilidades y dependencias | Tres niveles de zoom sobre el mismo sistema |
| 2.2 | Patrones, principios, técnicas, criterios | Capas y puertos y adaptadores (patrones) · monolito modular (organización) · DIP (principio) · DI (técnica) · cohesión y acoplamiento (criterios). Clean y Onion: parientes, no sinónimos | Tabla de 3 columnas; los términos se "guardan" en una mochila que vuelve en el machete |
| 2.3 | Cohesión | Lo que cambia junto, vive junto. Ejemplo: `put()` mezcla el cupo con el asunto del correo | Dos cajas: "inscribir" coherente vs. "hace de todo" |
| 2.4 | Acoplamiento: qué necesita saber una parte de otra | Formato, modelo, configuración, comportamiento (bloquea, falla). Ejemplo: la vista conoce `EMAIL_HOST` indirectamente | Tabla de 4 filas con ejemplo de nuestro código |
| 2.5 | Capa ≠ tier | Capa = organización lógica del código. Tier = proceso o máquina donde corre. Muchas capas pueden compartir un proceso | Dos vistas del mismo sistema lado a lado |
| 2.6 | **Dos ejes: horizontal y vertical** | Horizontal: por tipo de responsabilidad (capas). Vertical: por capacidad del negocio (actividades, inscripciones, notificaciones) = **monolito modular**: un deploy, límites internos. "Primero recorremos el eje horizontal; al final volvemos al vertical." | Grilla: filas = capas, columnas = capacidades; se ilumina primero una fila y después una columna |

## Bloque 3 — Red de seguridad (2 slides · 10 min)

| # | Slide | Contenido | Visual | Rama |
| --- | --- | --- | --- | --- |
| 3.1 | Refactorizar = cambiar la estructura, no el comportamiento | Antes de mover código, fijamos lo que hoy hace. Los tests de contrato ya existen (`test_put_creates_an_idempotent_enrollment`, …); agregamos uno para el correo con el backend `locmem` | Anatomía del test nuevo, diff `e01..e02` | `e02` |
| 3.2 | Correr la red 🧪 | `docker compose exec backend python manage.py test` · todos verdes · "esta salida tiene que ser idéntica en cada rama" | Terminal; aparece el badge "contrato ✔" en el minimapa | `e02` |

## Bloque 4 — Capas, paso a paso (9 slides · 40 min)

| # | Slide | Contenido | Visual | Rama |
| --- | --- | --- | --- | --- |
| 4.1 | De las cuatro preguntas a cuatro capas | Retomamos la tabla de 1.5 y el resultado de H1: ahora cada pregunta va a tener su lugar en el código. Presentación (¿cómo entra y sale?) · Aplicación (¿cómo coordinamos?) · Dominio (¿qué reglas valen?) · Infraestructura (¿con qué mecanismo?) | Pila de 4 bandas con los colores de la paleta; al lado, la vista coloreada de H1 en miniatura | — |
| 4.2 | Paso 1: un caso de uso | Movemos el cuerpo del `put()` a `application/inscribir.py`. La vista llama `inscribir(participante, actividad_id)` | **Diff** `e02..e03` (views.py se achica, aparece inscribir.py) | `e03` |
| 4.3 | Anatomía del caso de uso (v1) | ① recibe datos, no un request ② transacción ③ reglas ④ crear ⑤ notificar (todavía `send_mail`) ⑥ devuelve un resultado. Problema: ¿cómo devuelve el 409? | Anatomía | `e03` |
| 4.4 | Paso 2: la aplicación habla en errores, la vista en HTTP | `raise CupoAgotado()` en la aplicación; `except CupoAgotado: return 409` en la vista | Split: anatomía de `errores.py` + anatomía de la vista delgada (traducción error → status) | `e04` |
| 4.5 | Paso 3: reglas de dominio | `hay_cupo(capacidad, inscriptos)` y `exigir_cupo(...)`: funciones puras. Los errores se mudan de `application/` a `domain/`: son conceptos del negocio. Primer test **sin base de datos** 🧪 (5 tests en ~0 ms) | Anatomía de `reglas.py` + `test_reglas.py`; **P1 pasa a ◐** | `e05` |
| 4.6 | Paso 4: carpetas por capa | Movemos a `presentation/` e `infrastructure/email.py`. Árbol coloreado: ya se parece al destino | Árbol de `e06` al lado del árbol final (H2 en miniatura) | `e06` |
| 4.7 | Anatomía de la vista delgada | Lo que queda: ① parsear ② identidad ③ llamar al caso de uso ④ traducir resultado o error a HTTP. "Esto es un adaptador de entrada, aunque todavía no le pusimos nombre" | Anatomía `e06:presentation/views.py` | `e06` |
| 4.8 | 🛠 ¿Hacia dónde apuntan los imports? | Comparar `e01` (todo en un nodo) con `e06` (capas, flechas hacia abajo: presentación → aplicación → infraestructura) | 🛠 **H4** con el deslizador entre e01 y e06 | `e06` |
| 4.9 | Lo que sigue doliendo | La aplicación **importa** `send_mail` y el ORM. Para probar `Inscribir` hace falta una base y un backend de correo. Repasamos P1 ◐, P2 ☐, P3 ☐ | El grafo de 4.8 con la flecha aplicación → infraestructura en rojo | `e06` |

## Bloque 5 — Punto de control: capas (2 slides · 10 min)

| # | Slide | Contenido | Visual |
| --- | --- | --- | --- |
| 5.1 | Machete de capas 📸 | ¿Dónde va cada cosa? (versión capas): tabla capa / pregunta / archivo en `e06` / ejemplo | Slide "para sacarle foto" |
| 5.2 | Pregunta puente | "¿Y si la aplicación no dependiera de SMTP, sino al revés?" Lectura sugerida: Cockburn, *Hexagonal Architecture* (secciones 1 y 2) | Fondo rojo, pregunta grande |

---

## Bloque 6 — Recapitular (2 slides · 7 min)

Pensado para abrir un encuentro nuevo; si los bloques 5 y 7 se dan seguidos, se pasa rápido.

| # | Slide | Contenido | Visual | Rama |
| --- | --- | --- | --- | --- |
| 6.1 | Dónde quedamos | Minimapa en `e06`, P1 ◐ P2 ☐ P3 ☐, mapa del destino (H2) al lado: "¿qué falta?" | H2 con lo hecho en color y lo que falta en gris | `e06` |
| 6.2 | El problema, en una flecha | Aplicación → infraestructura. El negocio depende del mecanismo | 🛠 **H4** detenido en `e06`, flecha resaltada | `e06` |

## Bloque 7 — Inversión e inyección de dependencias (4 slides · 15 min)

| # | Slide | Contenido | Visual |
| --- | --- | --- | --- |
| 7.1 | DIP: depender de un contrato propio | Antes: `Inscribir → SMTP`. Después: `Inscribir → Notificador ← SMTP`. La aplicación **define** lo que necesita | Dos diagramas; la flecha de SMTP gira |
| 7.2 | DI: recibir la implementación desde afuera | `Inscribir(notificador=...)`. Un constructor alcanza; no hace falta un contenedor de DI | Fragmento de Python con callouts |
| 7.3 | DIP ≠ DI | DIP decide **de qué** depende; DI decide **cómo llega**. Se puede inyectar una clase concreta sin DIP | Tabla 2×2 con ejemplos |
| 7.4 | 🛠 Llamadas vs. dependencias | La llamada sigue yendo de Inscribir a SMTP; la dependencia de código se invierte | 🛠 **H3** (primera vez) |

## Bloque 8 — Arquitectura hexagonal (6 slides · 20 min)

| # | Slide | Contenido | Visual |
| --- | --- | --- | --- |
| 8.1 | El problema que plantea Cockburn | Una aplicación que solo puede usarse por su UI y solo funciona con su base no se puede probar ni reutilizar | Figura 1 de Cockburn (`organizar-antes-de-distribuir-recursos/`) |
| 8.2 | Adentro y afuera | Adentro: casos de uso y reglas. Afuera: HTTP, CLI, tests, base, correo. La forma de hexágono no significa seis partes | Hexágono vacío; se agregan elementos alrededor |
| 8.3 | Puerto: contrato en la frontera | Lo define la aplicación por su propósito ("notificar una confirmación"). No es el puerto de red 1025 | Hexágono con un puerto rojo |
| 8.4 | Entrada y salida | Entrada (*driving*): quien activa la aplicación (HTTP, CLI, tests). Salida (*driven*): lo que la aplicación necesita (notificar, persistir) | Hexágono con dos lados rotulados |
| 8.5 | Adaptadores | Traducen un mecanismo a un puerto. Un puerto, varios adaptadores | Hexágono con nuestros adaptadores reales |
| 8.6 | Capas y hexágono no se pelean | Las capas ordenan el interior; el hexágono ordena la frontera. Nuestro destino usa las dos (mismo árbol final, coloreado por rol) | H2 con el árbol coloreado por rol hexagonal |

## Bloque 9 — Puerto de salida: notificar (6 slides · 25 min)

| # | Slide | Contenido | Visual | Rama |
| --- | --- | --- | --- | --- |
| 9.1 | Anatomía del puerto | `ConfirmacionInscripcion` (dataclass inmutable) + `Notificador(Protocol)` con `enviar(datos) -> None` y `ErrorNotificacion` | Anatomía `e07:application/puertos.py` + `dto.py` | `e07` |
| 9.2 | El caso de uso recibe el puerto | `__init__(self, notificador)` · `self.notificador.enviar(...)`. Desaparece el import de `send_mail` | **Diff** `e06..e07:application/inscribir.py` | `e07` |
| 9.3 | Anatomía del adaptador SMTP | ① implementa el puerto ② traduce el DTO a un mensaje ③ usa `send_mail` ④ traduce `SMTPException` a `ErrorNotificacion`. Lo que significa "éxito": el servidor aceptó, no que alguien lo leyó | Anatomía `e07:infrastructure/notificaciones/smtp.py` | `e07` |
| 9.4 | Memoria y fallo | Dos adaptadores de 5 líneas. Test: el caso de uso pide notificar con los datos correctos, sin SMTP | Anatomía de los dos + `test_inscribir.py` | `e08` |
| 9.5 | La composición | `composition.py`: único lugar que conoce las implementaciones. Elige por `NOTIFICADOR` | Anatomía `e09:composition.py`; **P2 ☑** | `e09` |
| 9.6 | 🛠 Cambiá el adaptador 🧪 | Simulación (H5) y después en vivo: `NOTIFICADOR=fallo docker compose up backend` → igual responde 201 y `GET /me/enrollments` muestra la inscripción, pero el correo se perdió y solo queda en el log. Así se comportaba ya `e01` (`emails.py` atrapaba la excepción) y la red de seguridad lo fija | 🛠 **H5** + terminal | `e09` |

Notas 9.6: es el momento de mencionar que el fallo ocurre **después del commit**; se retoma en 14.3.

## Bloque 10 — Puerto de persistencia (5 slides · 20 min)

| # | Slide | Contenido | Visual | Rama |
| --- | --- | --- | --- | --- |
| 10.1 | El caso de uso todavía usa el ORM | `Activity.objects.select_for_update()` dentro de la aplicación → para probarlo hace falta una base | Grafo H4 en `e09`: queda una flecha aplicación → ORM | `e09` |
| 10.2 | Dominio puro | `@dataclass Actividad`, `Inscripcion`. Las reglas de `e05` ahora reciben entidades | Anatomía `e10:domain/modelos.py` | `e10` |
| 10.3 | Anatomía del puerto y del adaptador de repositorio | `RepositorioInscripciones`: `obtener_actividad_para_inscribir`, `buscar`, `crear`. El adaptador Django traduce modelo ORM ↔ entidad y encapsula el bloqueo y la transacción | Split: anatomía del puerto / anatomía de `repositorio_django.py` | `e11` |
| 10.4 | Probar el interior completo 🧪 | `RepositorioEnMemoria` + `NotificadorMemoria`: tests del caso de uso sin Django. Comparar tiempos | Anatomía `e12:tests/test_inscribir.py` + terminal; **P1 ☑** | `e12` |
| 10.5 | ¿Vale la pena? | Costos: mapeo duplicado, más archivos, el ORM de Django ya es casi un repositorio. Cuándo sí: reglas ricas, varios mecanismos, tests rápidos. Cuándo no: CRUD simple | Balanza ganancias / costos |

## Bloque 11 — Otra entrada: CLI (2 slides · 8 min)

| # | Slide | Contenido | Visual | Rama |
| --- | --- | --- | --- | --- |
| 11.1 | Anatomía del comando | `manage.py inscribir ada <uuid>` usa el **mismo** `Inscribir` armado en `composition.py`. Traduce errores a mensajes y exit codes | Anatomía `e13:management/commands/inscribir.py` + terminal 🧪; **P3 ☑** | `e13` |
| 11.2 | 🛠 Dos entradas, un interior | H3 con el selector en CLI: cambia el adaptador de entrada, el interior queda igual | 🛠 **H3** | `e13` |

## Bloque 12 — La regla como test (2 slides · 8 min)

| # | Slide | Contenido | Visual | Rama |
| --- | --- | --- | --- | --- |
| 12.1 | Anatomía de `.importlinter` | Contratos: `domain` no importa `django`; `application` no importa `infrastructure` ni `presentation`; capas en orden | Anatomía `e14:.importlinter` | `e14` |
| 12.2 | Romperlo a propósito 🧪 | Agregar `from django.db import transaction` en `inscribir.py` → `lint-imports` falla. El grafo H4 en `e14`: todas las flechas hacia adentro | Terminal + 🛠 **H4** completo (deslizador e01 → e14) | `e14` |

## Bloque 13 — Corte vertical: monolito modular (3 slides · 10 min · conceptual + rama opcional)

| # | Slide | Contenido | Visual | Rama |
| --- | --- | --- | --- | --- |
| 13.1 | Volvemos a la grilla | Recorrimos una columna (inscripciones) por todas sus filas. ¿Y si cortamos por columnas? Actividades, inscripciones, notificaciones | La grilla de 2.6 con las columnas iluminadas | — |
| 13.2 | Un módulo con interfaz pública (opcional en código) | `notificaciones/api.py` es lo único que otros módulos pueden importar. Mismo proceso, misma base, límite explícito. Árbol + `api.py` | Árbol de `opcional-monolito-modular` + anatomía de `api.py` | `opcional-monolito-modular` |
| 13.3 | Lo que queda abierto | Separar actividades de inscripciones: la FK `Enrollment → Activity`, ¿quién es dueño de la tabla?, ¿cómo consulto el cupo de otro módulo? Organizar antes de distribuir | Dos módulos con una flecha "¿?" entre ellos |

## Bloque 14 — Cierre, límites y ejercicio (4 slides · 10 min)

| # | Slide | Contenido | Visual |
| --- | --- | --- | --- |
| 14.1 | Llegamos | El mapa del destino, ahora con todo en color. P1 ☑ P2 ☑ P3 ☑ · contrato ✔ en las 15 ramas | 🛠 **H2** completo |
| 14.2 | Machete final 📸 | "Cómo se escribe cada componente": tabla de componentes (qué sabe, qué no sabe, archivo) | Slide para sacarle foto |
| 14.3 | Lo que la organización no resuelve | El correo sigue siendo síncrono (la petición espera a SMTP) y falla **después** del commit: la base y el correo no forman una operación atómica. Reintentar puede duplicar correos. → tema siguiente: notificación pendiente / asincronía | Línea de tiempo de la petición + caja de transacción con SMTP afuera |
| 14.4 | Ejercicio: Cancelar y Consultar | `git checkout ejercicio-cancelar-consultar`. Consigna: llevar `DELETE /me/enrollments/{id}` y `GET /me/enrollments` a casos de uso con puertos. Criterios: los tests de contrato siguen verdes, los tests nuevos pasan, `lint-imports` pasa. Fecha y entrega | Consigna con checklist ☐ |

---

## Rama `ejercicio-cancelar-consultar`

- Sale de `e14`. Incluye `EJERCICIO.md` con la consigna y **tests que fallan**:
  - `tests/test_cancelar.py`: `Cancelar` con `RepositorioEnMemoria` (idempotente, libera cupo, actividad inexistente).
  - `tests/test_consultar.py`: `ConsultarMisInscripciones`.
- Pistas en `EJERCICIO.md`: qué métodos agregar al puerto del repositorio, dónde componer y qué debe traducir la vista.
- `solucion-cancelar-consultar`: la referencia, para publicar después de la entrega.

## Fuentes

- [Alistair Cockburn, *Hexagonal Architecture* (2005)](https://alistair.cockburn.us/hexagonal-architecture) — figuras 1 y 3.
- [Martin Fowler, *Inversion of Control Containers and the Dependency Injection pattern*](https://martinfowler.com/articles/injection.html).
- [Django, envío de correo](https://docs.djangoproject.com/en/5.2/topics/email/) · [transacciones](https://docs.djangoproject.com/en/5.2/topics/db/transactions/).
- [Python, `typing.Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol).
- [import-linter](https://import-linter.readthedocs.io/).
- Material previo: `presentaciones-actividades/arq-web/organizar-antes-de-distribuir-storyboard.md` (de ahí se reutilizan
  las slides conceptuales 3–30 y 39–42, condensadas).
