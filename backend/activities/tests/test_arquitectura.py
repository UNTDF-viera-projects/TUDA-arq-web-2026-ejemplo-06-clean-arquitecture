import subprocess
import sys

from django.conf import settings
from django.test import SimpleTestCase

LINT_IMPORTS = (
    "import sys; from importlinter.cli import lint_imports; "
    "sys.exit(lint_imports(config_filename='.importlinter', no_cache=True, no_logo=True))"
)


class ReglaDeDependenciasTests(SimpleTestCase):
    """Falla si alguien rompe los contratos de .importlinter."""

    def test_las_dependencias_apuntan_hacia_adentro(self):
        # En un proceso aparte: import-linter configura su propio logging.
        resultado = subprocess.run(
            [sys.executable, "-c", LINT_IMPORTS],
            cwd=settings.BASE_DIR,
            capture_output=True,
            text=True,
        )

        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
