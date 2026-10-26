from datetime import datetime
from uuid import uuid4

from django.test import SimpleTestCase

from ..application.cancelar import Cancelar
from ..domain.errores import ActividadNoEncontrada
from ..domain.modelos import Actividad, Participante
from .fakes import RepositorioEnMemoria


class CancelarTests(SimpleTestCase):
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
        self.cancelar = Cancelar(self.repositorio)

    def test_elimina_solo_la_inscripcion_del_participante(self):
        self.repositorio.crear_inscripcion(self.ada.id, self.actividad.id)
        self.repositorio.crear_inscripcion(self.grace.id, self.actividad.id)

        self.cancelar.ejecutar(self.ada, self.actividad.id)

        self.assertEqual(
            [i.participante_id for i in self.repositorio.inscripciones],
            [self.grace.id],
        )

    def test_libera_el_cupo(self):
        self.repositorio.crear_inscripcion(self.ada.id, self.actividad.id)

        self.cancelar.ejecutar(self.ada, self.actividad.id)

        actividad = self.repositorio.obtener_actividad(self.actividad.id)
        self.assertEqual(actividad.inscriptos, 0)

    def test_es_idempotente(self):
        self.cancelar.ejecutar(self.ada, self.actividad.id)
        self.cancelar.ejecutar(self.ada, self.actividad.id)

        self.assertEqual(self.repositorio.inscripciones, [])

    def test_actividad_inexistente(self):
        with self.assertRaises(ActividadNoEncontrada):
            self.cancelar.ejecutar(self.ada, uuid4())
