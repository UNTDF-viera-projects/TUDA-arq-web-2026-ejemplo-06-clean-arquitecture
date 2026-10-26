from datetime import datetime
from uuid import uuid4

from django.test import SimpleTestCase

from ..domain.errores import CupoAgotado
from ..domain.modelos import Actividad
from ..domain.reglas import exigir_cupo, hay_cupo


def actividad(capacidad, inscriptos):
    return Actividad(
        id=uuid4(),
        titulo="Diseño de una API",
        inicia_en=datetime(2026, 3, 23, 18, 0),
        capacidad=capacidad,
        inscriptos=inscriptos,
    )


class ReglaDeCupoTests(SimpleTestCase):
    """Reglas puras: no necesitan base de datos, HTTP ni SMTP."""

    def test_hay_cupo_mientras_queden_lugares(self):
        self.assertTrue(hay_cupo(actividad(capacidad=2, inscriptos=1)))

    def test_no_hay_cupo_cuando_se_completa(self):
        self.assertFalse(hay_cupo(actividad(capacidad=2, inscriptos=2)))

    def test_una_actividad_sin_capacidad_nunca_tiene_cupo(self):
        self.assertFalse(hay_cupo(actividad(capacidad=0, inscriptos=0)))

    def test_exigir_cupo_lanza_cupo_agotado(self):
        with self.assertRaises(CupoAgotado):
            exigir_cupo(actividad(capacidad=1, inscriptos=1))

    def test_exigir_cupo_no_hace_nada_si_hay_lugar(self):
        exigir_cupo(actividad(capacidad=1, inscriptos=0))
