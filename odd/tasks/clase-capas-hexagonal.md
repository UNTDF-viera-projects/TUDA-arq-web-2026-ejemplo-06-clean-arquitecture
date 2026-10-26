# Clase capas / hexagonal — UNTDF Arquitecturas Web

One continuous block-based deck (teacher paces it, up to 4 meetings) that teaches layered and hexagonal architecture while the enrollments project evolves branch by branch.
Repo: `modular-capas-v2`. Base code: `../modular-capas` commits `63d3cb5` (actividad 06) and `d2a59fd` (email in the view, no layers).

## Specs

- S1: "Quiero que la presentación ayude a mostrar los conceptos a la vez que evolucionar el proyecto."
- S2: "Podríamos tener diferentes ramas para cada etapa así los chichos van viendo los cambios paulatinos"
- S3: "también es importante que puedan visualizar a dónde vamos a llegar. Cómo escribiremos los componentes, cual es la estructura de carpetas final."
- S4: "me encantó como quedó la "guia visual" sobre partes de comandos y archivos. [...] Creo que se puede hacer algo genial con ese formato o incluso complementar con pequeñas herramientas web dentro de la presentación que permitan entender mejor los ejemplos/conceptos/estructuras."
- S5: "No quiero que dividas las slides por \"día\". Yo lo iré regulando ayándome en los bloques." / "puedo hacer otra clase si es necesario. Tengo hasta 4 clases para terminar el tema"
- S6: "lleguemos hasta el final pero hagamos pequeños branches con cada cambio"
- S7: Naming: "sigamos tu recomendación" (Spanish for domain/application, existing English Django models and HTTP API unchanged).
- S8: "todas puedes incluir gráficos con https://github.com/tt-a1i/archify si vez que vale la pena."
- S9: "Ojo que el modular-caas capáz no conviene tomar del commit actual, si no del que tenga "todo monolito" sin que se le haya aplicado ninguna modificación "de capas""
- S10: "Me gusta lo de la propuesta de cancelar y consultar para los alumnos"
- S11: "Hagamos el monolito modular al final y pondemos crear una branch "opcional" dónde mostramos esto. Me gusta lo de hablar de vertical y horizontal creo que ayuda." / "osea el monolito modular sería conceptual + opcional a nivel de código"

## Tasks

- [x] T1 (S1-S11) Write `storyboard.md` — inline — main
- [x] T2 (S2, S9) Branches e00-e02 from modular-capas — inline — e00-base (cb7e714, c4d9023), e01 (eb468d8), e02 (b5d81cb)
- [x] T3 (S4) Slides infrastructure: build.py with branch refs, diffs, tree, import graph; UNTDF theme; minimap — worker — main (slides/)
- [x] T4 (S6, S7) Branches e03-e06 (layers) — inline — 682e0ca, 7c6ac20, fc92f07, d99f1c1
- [ ] T5 (S1, S3, S4) Slides blocks 0-5 — blocks 0-1 done (worker), blocks 2-5 pending
- [x] T6 (S6, S7) Branches e07-e14 (ports and adapters) — inline — c9979f1 … 4fac3cc
- [ ] T7 (S1, S3, S4) Slides blocks 6-14
- [x] T8 (S10, S11) Exercise branches cancel/query + optional modular monolith branch — inline — ejercicio-cancelar-consultar (fc61579, red on purpose), solucion-cancelar-consultar (a25836e, on top of ejercicio), opcional-monolito-modular
- [ ] T9 (S4) Interactive tools H2-H5 (H1 done)
- [ ] T10 (S8) Archify evaluation (offline) and pieces
- [x] T11 (S2, S6) `scripts/verificar-ramas.sh`: tests on every branch — all 15 green (11→30 tests)

- [x] T12 (S4) Optional gRPC input adapter branch `opcional-entrada-grpc` — inline — 2eb6624 (33 tests; real server smoke OK)

## Log

- L1: "Soy Leonel Viera, docente investigador de la universidad nacional de tierra del Fuego (UNTDF). Estoy dando la materia de Arquitecturas Web con un ejemplo de inscripciones a actividades. Ahora estaba introduciendo a los chicos al concecpto de arquitectura de capas / hexagonal, que proponen y sus componentes. Ellos nunca vieron como organizar esto y quiero primero plantearlo a nivel concepto y luego a nivel código. [...] Me puedes ayudar a planificar esta clase, su slide (storyboard y el código de apoyo). Una vez lleguemos a un acuerdo general comenzamos a generar"
- L2: Answers: 2 classes x 2h; small branches to the end; naming per recommendation; all interactive tools; archify when worth it; base = "todo monolito" commit.
- L3: "Me gusta lo de la propuesta de cancelar y consultar para los alumnos. Punto 3. Hagamos el monolito modular al final y pondemos crear una branch "opcional" dónde mostramos esto. [...] Comencemos con el storyboard"
- L4: "osea el monolito modular sería conceptual + opcional a nivel de código"
- L5: "Creo que no hay un problema en el storyboard planteado pero te menciono por las dudas que no lo plantees así. No quiero que dividas las slides por \"día\". Yo lo iré regulando ayándome en los bloques. 1 me gusta la discución sobre repositorio. 2 no te preocupes, puedo hacer otra clase si es necesario. Tengo hasta 4 clases para terminar el tema. arranquemos" → S5 rewritten, storyboard reorganized by blocks only.
- L6: Evidence: base 63d3cb5 had 2 stale tests (empty activities/urls.py) → cleanup commit in e00. emails.py swallows SMTP errors (201 + log): contract kept on every branch, so the "fallo" adapter yields 201 + log (storyboard 9.6 updated). import-linter must run in a subprocess inside tests (it reconfigures logging). Slice boundaries: each eNN branch is one reviewable unit.
- L7: "Las slides estarían disponibles en todas las ramas? No quiero tener que cambiar de rama para ver como sigue la slide" → slides stay on main (code embedded at build time); scripts/etapa.sh shows any stage in a separate worktree ../modular-capas-v2-codigo.
- L8: "Hay algo que no me termina de convencer antes de colorear la vista gorda [...] no explicamos nada de los conceptos de capaz ... como van a saber los alumnos qué colorear? faltarían un par de slides teóricas creo yo" → storyboard block 1 gains 1.4 (responsabilidad = pregunta) and 1.5 (cuatro preguntas para clasificar); H1 → 1.6 with legend; 4.1 becomes a recap. Sent to worker mvpgl510-2-tn4f.
- L9: "los chicos vieron grpc, creo qeu sería un mejor ejemplo de presentación/entrada eso que cli ? no te parece? al menos en el gráfico de la slide 2" → hexagon in 0.3 shows gRPC; teacher chose "Rama opcional (recomendado)": e13 keeps CLI, `opcional-entrada-grpc` from e14; storyboard 11.3 added.
- L10: "Al script de etapas podés agregarle un selector así puedo solo escribir ./scripts/etapa.sh y que me ofrezca una lista con cuál etapa quiero ir" → done (0888a32).
- L11: "instalalo pero solo localmente para este repo con pnpm" (archify) → project-local install; A1/A2 generated in archify/.
