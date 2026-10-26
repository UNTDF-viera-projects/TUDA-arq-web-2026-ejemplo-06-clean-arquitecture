from django.test import SimpleTestCase

from ..composition import construir_inscribir
from ..infrastructure.notificaciones.modulo import NotificadorModulo


class ComposicionTests(SimpleTestCase):
    def test_inscribir_notifica_a_traves_del_modulo_notificaciones(self):
        self.assertIsInstance(construir_inscribir().notificador, NotificadorModulo)
