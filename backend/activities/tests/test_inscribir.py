from datetime import datetime
from uuid import uuid4

from django.test import SimpleTestCase

from ..application.inscribir import Inscribir
from ..domain.errores import ActividadNoEncontrada, CupoAgotado
from ..domain.modelos import Actividad, Participante
from ..infrastructure.notificaciones.fallo import NotificadorFallo
from ..infrastructure.notificaciones.memoria import NotificadorMemoria
from .fakes import RepositorioEnMemoria


class InscribirTests(SimpleTestCase):
    """El caso de uso aislado: sin base de datos, sin SMTP y sin HTTP."""

    def setUp(self):
        self.ada = Participante(id=uuid4(), nombre="Ada", email="ada@example.com")
        self.grace = Participante(id=uuid4(), nombre="Grace", email="")
        self.actividad = Actividad(
            id=uuid4(),
            titulo="Diseño de una API",
            inicia_en=datetime(2026, 3, 23, 18, 0),
            capacidad=1,
            inscriptos=0,
        )
        self.repositorio = RepositorioEnMemoria([self.actividad])
        self.notificador = NotificadorMemoria()
        self.inscribir = Inscribir(self.repositorio, self.notificador)

    def test_crea_la_inscripcion_y_pide_notificar(self):
        resultado = self.inscribir.ejecutar(self.ada, self.actividad.id)

        self.assertTrue(resultado.creada)
        self.assertEqual(len(self.repositorio.inscripciones), 1)
        confirmacion = self.notificador.enviadas[0]
        self.assertEqual(confirmacion.destinatario, "ada@example.com")
        self.assertEqual(confirmacion.nombre, "Ada")
        self.assertEqual(confirmacion.actividad, "Diseño de una API")

    def test_repetir_devuelve_la_misma_inscripcion_sin_notificar_de_nuevo(self):
        primera = self.inscribir.ejecutar(self.ada, self.actividad.id)
        segunda = self.inscribir.ejecutar(self.ada, self.actividad.id)

        self.assertFalse(segunda.creada)
        self.assertEqual(segunda.inscripcion, primera.inscripcion)
        self.assertEqual(len(self.notificador.enviadas), 1)

    def test_sin_cupo_no_inscribe_ni_notifica(self):
        self.inscribir.ejecutar(self.grace, self.actividad.id)

        with self.assertRaises(CupoAgotado):
            self.inscribir.ejecutar(self.ada, self.actividad.id)

        self.assertEqual(len(self.repositorio.inscripciones), 1)
        self.assertEqual(self.notificador.enviadas, [])

    def test_actividad_inexistente(self):
        with self.assertRaises(ActividadNoEncontrada):
            self.inscribir.ejecutar(self.ada, uuid4())

    def test_sin_email_inscribe_sin_notificar(self):
        with self.assertLogs("activities", level="WARNING"):
            resultado = self.inscribir.ejecutar(self.grace, self.actividad.id)

        self.assertTrue(resultado.creada)
        self.assertEqual(self.notificador.enviadas, [])

    def test_si_el_notificador_falla_la_inscripcion_se_conserva(self):
        inscribir = Inscribir(self.repositorio, NotificadorFallo())

        with self.assertLogs("activities", level="ERROR"):
            resultado = inscribir.ejecutar(self.ada, self.actividad.id)

        self.assertTrue(resultado.creada)
        self.assertEqual(len(self.repositorio.inscripciones), 1)
