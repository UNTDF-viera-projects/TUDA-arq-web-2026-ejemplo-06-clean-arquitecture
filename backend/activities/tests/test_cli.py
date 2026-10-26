from datetime import datetime
from io import StringIO
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from ..models import Activity, Enrollment


@override_settings(NOTIFICADOR="memoria")
class ComandoInscribirTests(TestCase):
    def setUp(self):
        get_user_model().objects.create_user(username="ada")
        self.actividad = Activity.objects.create(
            title="Diseño de una API",
            starts_at=timezone.make_aware(datetime(2026, 3, 23, 18, 0)),
            capacity=1,
        )

    def inscribir(self, usuario, actividad_id):
        salida = StringIO()
        call_command("inscribir", usuario, str(actividad_id), stdout=salida)
        return salida.getvalue()

    def test_inscribe_y_es_idempotente(self):
        self.assertIn("Inscripción creada.", self.inscribir("ada", self.actividad.id))
        self.assertIn("Ya estaba inscripto", self.inscribir("ada", self.actividad.id))
        self.assertEqual(Enrollment.objects.count(), 1)

    def test_errores_del_caso_de_uso_como_mensajes(self):
        get_user_model().objects.create_user(username="grace")
        self.inscribir("grace", self.actividad.id)

        casos = {
            "No hay cupos disponibles.": ("ada", self.actividad.id),
            "La actividad no existe.": ("ada", uuid4()),
            "El usuario 'nadie' no existe.": ("nadie", self.actividad.id),
        }
        for mensaje, argumentos in casos.items():
            with self.subTest(mensaje), self.assertRaisesMessage(CommandError, mensaje):
                self.inscribir(*argumentos)

        self.assertEqual(Enrollment.objects.count(), 1)
