from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings

from ..composition import construir_inscribir
from ..infrastructure.notificaciones.fallo import NotificadorFallo
from ..infrastructure.notificaciones.memoria import NotificadorMemoria
from ..infrastructure.notificaciones.smtp import NotificadorSMTP


class ComposicionTests(SimpleTestCase):
    def test_elige_el_notificador_segun_la_configuracion(self):
        casos = {
            "smtp": NotificadorSMTP,
            "memoria": NotificadorMemoria,
            "fallo": NotificadorFallo,
        }
        for nombre, clase in casos.items():
            with self.subTest(nombre), override_settings(NOTIFICADOR=nombre):
                self.assertIsInstance(construir_inscribir().notificador, clase)

    @override_settings(NOTIFICADOR="paloma")
    def test_un_notificador_desconocido_es_un_error_de_configuracion(self):
        with self.assertRaisesMessage(ImproperlyConfigured, "NOTIFICADOR='paloma'"):
            construir_inscribir()
