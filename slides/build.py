"""Genera slides/index.html a partir de slides/index.src.html.

Solo biblioteca estándar. Se corre desde la raíz del repo (o desde cualquier lado):

    python3 slides/build.py

Atributos que reconoce en elementos VACÍOS del HTML fuente (<code>, <textarea>, <div>, <script>…):

  data-incluir="ruta"              contenido del archivo en el árbol de trabajo (relativo a la raíz del repo)
  data-incluir="rama:ruta"         contenido del archivo en esa rama (git show rama:ruta)
  data-lineas="160-200"            (con data-incluir) solo ese rango de líneas, 1-based e inclusivo
  data-diff="ramaA..ramaB:ruta"    diff unificado del archivo entre ramas, como líneas HTML
                                   (.l.add / .l.del / .l.ctx / .l.hunk); si falta de un lado, todo suma/resta.
                                   Usar un <div class="diff">, no <pre><code> (reveal lo resaltaría como texto).
                                   Opcional: data-contexto="1" = líneas de contexto por hunk (default 3)
  data-arbol="rama:carpeta"        árbol HTML de carpetas (sin migrations/, __pycache__, __init__.py);
                                   cada archivo lleva la clase de su capa (capa-dominio, …)
  data-grafo="rama"                JSON {rama, nodos, aristas} con el grafo de imports de backend/activities
                                   (ver construir_grafo); va dentro de <script type="application/json">

Nombres de rama: completos (`e01-email-en-la-vista`) o cortos (`e01`: la única rama que empieza con `e01-`).
Si la rama local no existe se prueba `origin/<rama>`. Cualquier error termina con un mensaje claro.
"""

import ast
import difflib
import html
import json
import re
import subprocess
import sys
from pathlib import Path

SLIDES = Path(__file__).resolve().parent
RAIZ = SLIDES.parent
PAQUETE = "backend/activities"

PATRON = re.compile(
    r"<(?P<tag>[a-zA-Z][a-zA-Z0-9]*)(?P<attrs>[^>]*?\bdata-(?P<tipo>incluir|diff|arbol|grafo)=\"(?P<valor>[^\"]+)\"[^>]*)>"
    r"(?P<vacio>\s*)</(?P=tag)>"
)


def fallar(mensaje: str) -> None:
    sys.exit(f"build.py: {mensaje}")


# ---------------------------------------------------------------- git

def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8")


_refs: list[str] | None = None


def refs_disponibles() -> list[str]:
    global _refs
    if _refs is None:
        salida = git("for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes/origin")
        if salida.returncode != 0:
            fallar(f"git for-each-ref falló: {salida.stderr.strip()}")
        _refs = salida.stdout.split()
    return _refs


def resolver_rama(nombre: str) -> str:
    """Devuelve la referencia git a usar (rama local u `origin/<rama>`)."""
    refs = refs_disponibles()
    locales = {r[len("refs/heads/"):] for r in refs if r.startswith("refs/heads/")}
    remotas = {r[len("refs/remotes/origin/"):] for r in refs if r.startswith("refs/remotes/origin/")}
    remotas.discard("HEAD")
    for conjunto, prefijo in ((locales, ""), (remotas, "origin/")):
        if nombre in conjunto:
            return prefijo + nombre
        if re.fullmatch(r"e\d\d", nombre):
            candidatas = sorted(r for r in conjunto if r.startswith(nombre + "-"))
            if len(candidatas) > 1:
                fallar(f"la rama corta '{nombre}' es ambigua: {', '.join(candidatas)}")
            if candidatas:
                return prefijo + candidatas[0]
    fallar(f"no existe la rama '{nombre}' (ni local ni origin/{nombre})")


def nombre_completo(ref: str) -> str:
    return ref[len("origin/"):] if ref.startswith("origin/") else ref


def leer_en_rama(rama: str, ruta: str) -> str | None:
    """Contenido de `ruta` en `rama`, o None si el archivo no existe allí."""
    ref = resolver_rama(rama)
    r = git("show", f"{ref}:{ruta}")
    if r.returncode != 0:
        return None
    return r.stdout


def listar_en_rama(rama: str, carpeta: str) -> list[str]:
    ref = resolver_rama(rama)
    r = git("ls-tree", "-r", "--name-only", ref, carpeta.rstrip("/") + "/")
    if r.returncode != 0:
        fallar(f"git ls-tree falló para {rama}:{carpeta}: {r.stderr.strip()}")
    archivos = r.stdout.splitlines()
    if not archivos:
        fallar(f"la carpeta {carpeta} no existe en la rama {rama}")
    return archivos


def partir_rama_ruta(valor: str) -> tuple[str, str]:
    rama, _, ruta = valor.partition(":")
    return rama, ruta


# ---------------------------------------------------------------- capas

CAPAS = ("presentacion", "aplicacion", "dominio", "puerto", "infraestructura", "composicion", "tests")


def capa_de(ruta: str) -> str:
    """Capa de un archivo según su ruta (relativa a la raíz del repo o a la app). '' = neutral."""
    partes = ruta.split("/")
    nombre = partes[-1]
    if any(p.startswith("tests") for p in partes):
        return "tests"
    if nombre == "composition.py":
        return "composicion"
    if "domain" in partes[:-1]:
        return "dominio"
    if "application" in partes[:-1]:
        # Extensión sobre las reglas del encargo: los contratos de la aplicación se pintan como puerto.
        return "puerto" if nombre == "puertos.py" else "aplicacion"
    if "presentation" in partes[:-1]:
        return "presentacion"
    if "management" in partes and "commands" in partes and nombre == "inscribir.py":
        return "presentacion"
    if "infrastructure" in partes[:-1] or "migrations" in partes:
        return "infraestructura"
    if nombre == "models.py":
        return "infraestructura"
    if nombre in ("views.py", "serializers.py", "api_urls.py"):
        return "presentacion"
    if nombre == "emails.py":
        return "infraestructura"
    return ""


def es_excluido(ruta: str) -> bool:
    partes = ruta.split("/")
    return "migrations" in partes or "__pycache__" in partes or partes[-1] == "__init__.py"


# ---------------------------------------------------------------- includes

def incluir(valor: str, atributos: str) -> str:
    if ":" in valor and not valor.startswith("/"):
        rama, ruta = partir_rama_ruta(valor)
        contenido = leer_en_rama(rama, ruta)
        if contenido is None:
            fallar(f"no existe el archivo {ruta} en la rama {rama} (data-incluir=\"{valor}\")")
    else:
        archivo = RAIZ / valor
        if not archivo.is_file():
            fallar(f"no existe {valor} (data-incluir)")
        contenido = archivo.read_text(encoding="utf-8")

    rango = re.search(r'\bdata-lineas="(\d+)-(\d+)"', atributos)
    lineas = contenido.splitlines()
    if rango:
        desde, hasta = int(rango.group(1)), int(rango.group(2))
        if not 1 <= desde <= hasta <= len(lineas):
            fallar(f"data-lineas=\"{desde}-{hasta}\" fuera de rango en {valor} ({len(lineas)} líneas)")
        lineas = lineas[desde - 1:hasta]
    return html.escape("\n".join(lineas).rstrip("\n"), quote=False)


def diff(valor: str, atributos: str) -> str:
    cabecera, _, ruta = valor.partition(":")
    if ".." not in cabecera or not ruta:
        fallar(f"data-diff=\"{valor}\" debe tener la forma ramaA..ramaB:ruta")
    rama_a, rama_b = cabecera.split("..", 1)
    a = leer_en_rama(rama_a, ruta)
    b = leer_en_rama(rama_b, ruta)
    if a is None and b is None:
        fallar(f"{ruta} no existe ni en {rama_a} ni en {rama_b} (data-diff)")
    a_lineas = (a or "").splitlines()
    b_lineas = (b or "").splitlines()
    contexto = re.search(r'\bdata-contexto="(\d+)"', atributos)
    contexto = int(contexto.group(1)) if contexto else 3
    filas = []
    for linea in list(difflib.unified_diff(a_lineas, b_lineas, lineterm="", n=contexto))[2:]:
        if linea.startswith("@@"):
            clase, texto = "hunk", linea
        elif linea.startswith("+"):
            clase, texto = "add", linea
        elif linea.startswith("-"):
            clase, texto = "del", linea
        else:
            clase, texto = "ctx", linea
        filas.append(f'<span class="l {clase}">{html.escape(texto, quote=False)}</span>')
    if not filas:
        filas.append('<span class="l ctx">(sin cambios)</span>')
    return "".join(filas)


def arbol(valor: str) -> str:
    rama, carpeta = partir_rama_ruta(valor)
    archivos = [a for a in listar_en_rama(rama, carpeta) if not es_excluido(a)]
    raiz: dict = {}
    for a in archivos:
        nodo = raiz
        relativa = a[len(carpeta.rstrip("/")) + 1:].split("/")
        for parte in relativa[:-1]:
            nodo = nodo.setdefault(parte, {})
        nodo[relativa[-1]] = a  # hoja = ruta completa

    def render(nodo: dict) -> str:
        # carpetas primero, después archivos, cada grupo alfabético
        orden = sorted(nodo, key=lambda k: (not isinstance(nodo[k], dict), k))
        items = []
        for nombre in orden:
            hijo = nodo[nombre]
            if isinstance(hijo, dict):
                items.append(f'<li class="dir"><span class="nombre">{html.escape(nombre)}/</span>{render(hijo)}</li>')
            else:
                capa = capa_de(hijo)
                clase = f"hoja capa-{capa}" if capa else "hoja"
                items.append(f'<li class="{clase}"><span class="nombre">{html.escape(nombre)}</span></li>')
        return "<ul>" + "".join(items) + "</ul>"

    return render(raiz)


# ---------------------------------------------------------------- grafo

def construir_grafo(rama: str) -> dict:
    """Grafo de imports entre los módulos de backend/activities en `rama`.

    Nodos: módulos .py (sin migrations, tests*, __init__) con su capa. Id = nombre punteado ("activities.views").
    Aristas {"from","to"}: imports entre esos módulos, resueltos con `ast` (incluye imports relativos y
    `from paquete import modulo`). Además, hacia dos pseudo-nodos externos:
      - "SMTP": el módulo importa `django.core.mail` (from django.core.mail import …, from django.core import mail).
      - "ORM":  el módulo importa algo de `django.db` (incluye django.db.models/transaction) o importa el
                módulo `activities.models` (usar los modelos es usar el ORM). models.py también aparece como
                nodo, así que además de "x → ORM" existe "x → activities.models".
    """
    ref = resolver_rama(rama)
    archivos = [a for a in listar_en_rama(rama, PAQUETE) if a.endswith(".py") and not es_excluido(a)
                and capa_de(a) != "tests"]

    def modulo(ruta: str) -> str:
        return ruta[len("backend/"):-3].replace("/", ".")

    ids = {modulo(a): a for a in archivos}
    nodos = [{"id": m, "ruta": a, "capa": capa_de(a)} for m, a in sorted(ids.items())]
    aristas: set[tuple[str, str]] = set()

    for mod, ruta in ids.items():
        codigo = leer_en_rama(rama, ruta)
        try:
            arbol_ast = ast.parse(codigo or "")
        except SyntaxError as e:
            fallar(f"no pude parsear {ruta} en {rama}: {e}")
        paquete = mod.split(".")[:-1]  # paquete que contiene al módulo

        def destino(nombre: str) -> None:
            if nombre in ids and nombre != mod:
                aristas.add((mod, nombre))
            if nombre == "activities.models" and mod != "activities.models":
                aristas.add((mod, "ORM"))

        for n in ast.walk(arbol_ast):
            if isinstance(n, ast.Import):
                for alias in n.names:
                    base = alias.name
                    if base.startswith("django.db"):
                        aristas.add((mod, "ORM"))
                    if base.startswith("django.core.mail"):
                        aristas.add((mod, "SMTP"))
                    destino(base)
            elif isinstance(n, ast.ImportFrom):
                if n.level:
                    base = ".".join(paquete[: len(paquete) - (n.level - 1)] + ([n.module] if n.module else []))
                else:
                    base = n.module or ""
                if base.startswith("django.db"):
                    aristas.add((mod, "ORM"))
                if base.startswith("django.core.mail") or (
                    base == "django.core" and any(a.name == "mail" for a in n.names)
                ):
                    aristas.add((mod, "SMTP"))
                if base == "django" and any(a.name == "db" for a in n.names):
                    aristas.add((mod, "ORM"))
                destino(base)
                for alias in n.names:  # from paquete import modulo
                    destino(f"{base}.{alias.name}")

    externos = [{"id": "SMTP", "capa": "externo"}, {"id": "ORM", "capa": "externo"}]
    return {
        "rama": nombre_completo(ref),
        "nodos": nodos + externos,
        "aristas": [{"from": a, "to": b} for a, b in sorted(aristas)],
    }


def grafo(valor: str) -> str:
    # `</` dentro de <script> cerraría la etiqueta: se escapa
    return json.dumps(construir_grafo(valor), ensure_ascii=False, indent=1).replace("</", "<\\/")


# ---------------------------------------------------------------- main

contador = 0


def reemplazar(m: re.Match) -> str:
    global contador
    tipo, valor, tag, attrs = m.group("tipo"), m.group("valor"), m.group("tag"), m.group("attrs")
    if tipo == "incluir":
        cuerpo = incluir(valor, attrs)
    elif tipo == "diff":
        cuerpo = diff(valor, attrs)
    elif tipo == "arbol":
        cuerpo = arbol(valor)
    else:
        cuerpo = grafo(valor)
    contador += 1
    return f"<{tag}{attrs}>{cuerpo}</{tag}>"


def main() -> None:
    fuente = (SLIDES / "index.src.html").read_text(encoding="utf-8")
    salida = PATRON.sub(reemplazar, fuente)
    aviso = "<!-- GENERADO por slides/build.py: editar index.src.html -->\n"
    (SLIDES / "index.html").write_text(aviso + salida, encoding="utf-8")
    print(f"index.html generado ({contador} includes resueltos)")


if __name__ == "__main__":
    main()
