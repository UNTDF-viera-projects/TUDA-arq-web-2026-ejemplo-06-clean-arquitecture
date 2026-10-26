from datetime import datetime
from uuid import uuid4

import grpc
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from ..models import Activity, Enrollment
from ..presentation.grpc import inscripciones_pb2
from ..presentation.grpc.servicio import ServicioInscripciones


class Abortado(Exception):
    pass


class ContextoFalso:
    """Imita grpc.ServicerContext: metadata de entrada y abort()."""

    def __init__(self, token=None):
        self.metadata = [("authorization", f"Bearer {token}")] if token else []
        self.codigo = None

    def invocation_metadata(self):
        return self.metadata

    def abort(self, codigo, detalle):
        self.codigo, self.detalle = codigo, detalle
        raise Abortado(detalle)


@override_settings(NOTIFICADOR="memoria")
class ServicioInscripcionesTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(username="ada")
        self.token = str(AccessToken.for_user(self.usuario))
        self.actividad = Activity.objects.create(
            title="Diseño de una API",
            starts_at=timezone.make_aware(datetime(2026, 3, 23, 18, 0)),
            capacity=1,
        )
        self.servicio = ServicioInscripciones()

    def inscribir(self, actividad_id, token="propio"):
        contexto = ContextoFalso(self.token if token == "propio" else token)
        pedido = inscripciones_pb2.InscribirRequest(actividad_id=str(actividad_id))
        try:
            return self.servicio.Inscribir(pedido, contexto), contexto
        except Abortado:
            return None, contexto

    def test_inscribe_con_el_mismo_caso_de_uso_y_es_idempotente(self):
        primera, _ = self.inscribir(self.actividad.id)
        segunda, _ = self.inscribir(self.actividad.id)

        self.assertTrue(primera.creada)
        self.assertFalse(segunda.creada)
        self.assertEqual(primera.actividad_id, str(self.actividad.id))
        self.assertEqual(Enrollment.objects.count(), 1)

    def test_errores_del_caso_de_uso_como_codigos_grpc(self):
        otro = get_user_model().objects.create_user(username="grace")
        self.inscribir(self.actividad.id, token=str(AccessToken.for_user(otro)))

        casos = {
            grpc.StatusCode.FAILED_PRECONDITION: (self.actividad.id, "propio"),
            grpc.StatusCode.NOT_FOUND: (uuid4(), "propio"),
            grpc.StatusCode.INVALID_ARGUMENT: ("no-es-uuid", "propio"),
            grpc.StatusCode.UNAUTHENTICATED: (self.actividad.id, None),
        }
        for codigo, (actividad_id, token) in casos.items():
            with self.subTest(codigo):
                respuesta, contexto = self.inscribir(actividad_id, token)
                self.assertIsNone(respuesta)
                self.assertEqual(contexto.codigo, codigo)

        self.assertEqual(Enrollment.objects.count(), 1)

    def test_rechaza_un_token_invalido(self):
        respuesta, contexto = self.inscribir(self.actividad.id, token="basura")

        self.assertIsNone(respuesta)
        self.assertEqual(contexto.codigo, grpc.StatusCode.UNAUTHENTICATED)
