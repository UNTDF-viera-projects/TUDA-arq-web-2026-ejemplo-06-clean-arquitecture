from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ..application.inscribir import Inscribir
from ..domain.errores import CupoAgotado
from ..domain.modelos import Participante
from ..infrastructure.db.repositorio_django import RepositorioDjango
from ..infrastructure.notificaciones.fallo import NotificadorFallo
from ..infrastructure.notificaciones.memoria import NotificadorMemoria
from ..models import Activity, Enrollment, Participant


class InscribirTests(TestCase):
    """El caso de uso con notificadores sustitutos: sin SMTP ni HTTP."""

    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username="ada", email="ada@example.com", first_name="Ada"
        )
        fila = Participant.objects.create(name="Ada", user=usuario)
        self.participante = Participante(
            id=fila.id, nombre="Ada", email="ada@example.com"
        )
        self.actividad = Activity.objects.create(
            title="Diseño de una API",
            starts_at=timezone.make_aware(datetime(2026, 3, 23, 18, 0)),
            capacity=1,
        )

    def test_pide_notificar_una_vez_con_los_datos_de_la_inscripcion(self):
        notificador = NotificadorMemoria()

        Inscribir(RepositorioDjango(), notificador).ejecutar(self.participante, self.actividad.id)
        Inscribir(RepositorioDjango(), notificador).ejecutar(self.participante, self.actividad.id)

        self.assertEqual(len(notificador.enviadas), 1)
        confirmacion = notificador.enviadas[0]
        self.assertEqual(confirmacion.destinatario, "ada@example.com")
        self.assertEqual(confirmacion.nombre, "Ada")
        self.assertEqual(confirmacion.actividad, "Diseño de una API")

    def test_sin_cupo_no_notifica(self):
        otra = Participant.objects.create(name="Grace")
        Enrollment.objects.create(participant=otra, activity=self.actividad)
        notificador = NotificadorMemoria()

        with self.assertRaises(CupoAgotado):
            Inscribir(RepositorioDjango(), notificador).ejecutar(self.participante, self.actividad.id)

        self.assertEqual(notificador.enviadas, [])

    def test_si_el_notificador_falla_la_inscripcion_se_conserva(self):
        with self.assertLogs("activities", level="ERROR"):
            resultado = Inscribir(RepositorioDjango(), NotificadorFallo()).ejecutar(
                self.participante, self.actividad.id
            )

        self.assertTrue(resultado.creada)
        self.assertTrue(
            Enrollment.objects.filter(
                participant_id=self.participante.id, activity=self.actividad
            ).exists()
        )
