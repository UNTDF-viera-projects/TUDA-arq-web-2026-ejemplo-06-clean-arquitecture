from datetime import datetime
from uuid import uuid4

from django.test import SimpleTestCase

from ..application.consultar import ConsultarMisInscripciones
from ..domain.modelos import Actividad, Participante
from .fakes import RepositorioEnMemoria


def actividad(titulo):
    return Actividad(
        id=uuid4(),
        titulo=titulo,
        inicia_en=datetime(2026, 3, 23, 18, 0),
        capacidad=10,
        inscriptos=0,
    )


class ConsultarMisInscripcionesTests(SimpleTestCase):
    def setUp(self):
        self.ada = Participante(id=uuid4(), nombre="Ada", email="ada@example.com")
        self.grace = Participante(id=uuid4(), nombre="Grace", email="")
        self.api = actividad("Diseño de una API")
        self.docker = actividad("Docker")
        self.repositorio = RepositorioEnMemoria([self.api, self.docker])
        self.consultar = ConsultarMisInscripciones(self.repositorio)

    def test_sin_inscripciones_devuelve_una_lista_vacia(self):
        self.assertEqual(self.consultar.ejecutar(self.ada), [])

    def test_devuelve_solo_las_propias_de_la_mas_antigua_a_la_mas_nueva(self):
        primera = self.repositorio.crear_inscripcion(self.ada.id, self.docker.id)
        self.repositorio.crear_inscripcion(self.grace.id, self.api.id)
        segunda = self.repositorio.crear_inscripcion(self.ada.id, self.api.id)

        self.assertEqual(self.consultar.ejecutar(self.ada), [primera, segunda])
