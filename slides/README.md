# Slides — Organizar el código: de la vista gorda a puertos y adaptadores

Presentación reveal.js, sin dependencias de red. El guion está en [`../storyboard.md`](../storyboard.md).

## Presentar

Abrir `slides/index.html` en el navegador (funciona offline).
`S` = notas del orador · `O` = vista general · `?print-pdf` en la URL = exportar a PDF (Chrome → Imprimir → Guardar como PDF).

## Editar y generar

Se edita `index.src.html` (contenido) y `untdf.css` (estilo). Después, desde la raíz del repo:

```bash
python3 slides/build.py   # regenera slides/index.html (solo biblioteca estándar; necesita git)
```

`index.html` es un archivo generado y se commitea para poder abrirlo sin compilar. Los elementos vacíos con estos atributos se completan al generar:

| Atributo | Resultado |
| --- | --- |
| `data-incluir="ruta"` / `"rama:ruta"` | contenido del archivo (árbol de trabajo o `git show rama:ruta`) |
| `data-lineas="160-200"` | con `data-incluir`: solo ese rango (1-based, inclusivo) |
| `data-diff="ramaA..ramaB:ruta"` | diff resaltado (`<div class="diff">`; `data-contexto="1"` acota el contexto) |
| `data-arbol="rama:backend/activities"` | árbol de carpetas coloreado por capa |
| `data-grafo="rama"` | JSON con el grafo de imports (para la herramienta H4) |

Las ramas se escriben cortas (`e01`) o completas (`e01-email-en-la-vista`); si no existe la local se prueba `origin/<rama>`.
Si falta una rama o archivo, el build termina con un mensaje claro.

Cada `<section>` puede declarar para el minimapa: `data-rama="e01"`, `data-p1|p2|p3="no|parcial|si"` (si existe `data-p1` se muestran las preguntas) y `data-contrato="si"`.
